
import redis
import json
import uuid
import time
from gsy_e_sdk import cli as sdk_cli
from gsy_e.gsy_e_core import cli as gsy_cli
from gsy_e.models.config import SimulationConfig

from redis_basic_strategies_BC import Oracle
import threading

from gsy_e_sdk.redis_aggregator import RedisAggregator
from gsy_e_sdk.clients.redis_asset_client import RedisAssetClient
from gsy_e.setup.api_setup.default_community_BC import get_setup
from gsy_e.gsy_e_core.area_serializer import area_to_string
from gsy_e.gsy_e_core.global_objects_singleton import global_objects

from gsy_e.models.area import Area, Market


class SimulationController():
    def __init__(self):
        # self.redis = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
        # self.pubsub = self.redis.pubsub()
        # self.redis_sub_channels = {
        #     "/response/resume": self.handle_resume_response
        # }
        # self.pubsub.psubscribe(**self.redis_sub_channels)
        # self.pubsub.run_in_thread(daemon=True, sleep_time=1)
        self.shared_object = {}
        self.has_started = False

    def check_simulation(f):
        def validated_function(*args, **kwargs):
            _self = args[0]
            if "simulation" not in _self.shared_object:
                return None
            return f(*args, **kwargs)
        return validated_function
    
    @property
    @check_simulation
    def simulation(self):
        return self.shared_object["simulation"]
    @property
    def is_paused(self):
        return self.simulation._status.paused
    
    @property
    def is_finished(self):
        return self.simulation._status.finished

    @property
    def current_market_tree(self):
        return global_objects.external_global_stats.area_stats_tree_dict

    @property
    def current_observation(self):
        return self.current_market_tree
    
    @property
    def current_info(self):
        return self.current_market_tree
    
    @property
    def slot_number(self):
        return self.simulation.progress_info.current_slot_number
    

    
    def next_slot(self):
        if self.is_paused:
            self.resume()
        current_slot = self.slot_number
        while current_slot == self.slot_number:
            time.sleep(0.1)
        self.pause()
    
    def start(self, args=[ "-t", "5s", "-s", "15m", "--setup", "api_setup.default_community_BC", "--enable-external-connection", "--paused", "--slot-length-realtime", "10"], 
              wait_for_start=True,
              with_oracle=True):
        
        if self.has_started:
            self.stop()
            self.shared_object = {}
        click_context = gsy_cli.run.make_context("run", args)
        function_parameters = click_context.params
        args_param, kwargs_param = split_params(function_parameters, ["paused", "seed", "repl", "no_export", "export_path", "enable_bc"])
        kwargs_param["object_shared"] = self.shared_object
        thread = threading.Thread(target=gsy_cli.execute, args=(args_param.values()), kwargs=kwargs_param, daemon=True)
        thread.start()
        self.has_started = True

        if wait_for_start:
            while not self.simulation:
                time.sleep(0.1)
                
        if with_oracle:
            self.start_oracle()
    
    def pause(self):
        if self.is_paused:
            print("simulation already in pause")
        else:
            self.simulation._status.toggle_pause()

    def resume(self):
        if not self.is_paused:
            print("simulation is already running")
        else:
            self.simulation._status.toggle_pause()

    def stop(self):
        if not self.has_started:
            print("simulation was never started")
        else:
            self.simulation._status.stop()
            self.has_started = False

    def start_oracle(self):
        self.asset_oracle = Oracle(aggregator_name="my asset oracle")
        self.is_oracle_running = True


    def register_asset(self, area_name):
        asset = RedisAssetClient(autoregister=True, pubsub_thread=self.asset_oracle.pubsub, is_blocking=True, area_id=area_name)
        asset.select_aggregator(self.asset_oracle.aggregator_uuid)


    def get_assets(self) -> list[Area]:
        return separate_leafs(self.simulation.area)[0]
    
    def get_no_asset_areas(self) -> list[Market]:
        return separate_leafs(self.simulation.area)[1]
    
    def get_all_areas(self):
        return get_nodes(self.simulation.area)
        

    # def resume(self):
    #     self._run_command("resume")
    #     self.is_running = True

    # def pause(self):
    #     self._run_command("pause")
    #     self.is_running = False

    # def stop(self):
    #     self._run_command("stop")
    #     self.has_started = False

    # def _run_command(self, command):
    #     self.redis.publish("/"+command, json.dumps({"transaction_id": str(uuid.uuid1())}))

    # def handle_resume_response(self, message):
    #     print("resume message: ", message)


    # def _run_live_command(self, eventType, *args):
    #     self.redis.publish("/live-event", json.dumps({"transaction_id": str(uuid.uuid1()),"eventType":eventType, "transaction_id":1, **args[0]}))

    # def add_area(self, area, parent_uuid = ""):
    #     area_repr = area_to_string(area)
    #     area_dic = json.loads(area_repr)
    #     self._run_live_command("create_area", {"parent_uuid":parent_uuid, "area_representation":area_dic})

## UTILS
def split_params(param_dict, kwargs_param_list):
    kwargs_param_dict = {}
    args_param_dict = {}
    for param in param_dict:
        if param in kwargs_param_list:
            kwargs_param_dict[param] = param_dict[param]
        else:
            args_param_dict[param] = param_dict[param]

    return args_param_dict, kwargs_param_dict


def separate_leafs(area) -> tuple[list[Area], list[Market]]:
    leafs = []
    non_leafs = []
    areas = get_nodes(area)
    for area in areas:
        if len(area.children)==0:
            leafs.append(area)
        else:
            non_leafs.append(area)
    return leafs, non_leafs

def get_nodes(area):
    import numpy as np
    children = area.children
    leafs_areas = np.array([area])
    
    for child in children:
        leafs_areas = np.append(leafs_areas, get_nodes(child))    
    return leafs_areas
    