
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
    def current_observation(self):
        pass

    @property
    def current_market_tree(self):
        return global_objects.external_global_stats.area_stats_tree_dict
    
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
    
    def start(self, args=[ "-t", "5s", "-s", "15m", "--setup", "api_setup.default_community", "--enable-external-connection", "--paused", "--slot-length-realtime", "10"], 
              wait_for_start=True,
              with_oracle=True):
        click_context = gsy_cli.run.make_context("run", args)
    
        thread = threading.Thread(target=gsy_cli.execute, args=(click_context.params.values()), kwargs={"object_shared":self.shared_object}, daemon=True)
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

    def start_oracle(self):
        self.asset_oracle = Oracle(aggregator_name="my asset oracle")
        self.is_oracle_running = True


    
        
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

    def register_asset(self, area_name):
        asset = RedisAssetClient(autoregister=True, pubsub_thread=self.asset_oracle.pubsub, is_blocking=True, area_id=area_name)
        asset.select_aggregator(self.asset_oracle.aggregator_uuid)

    # def _run_live_command(self, eventType, *args):
    #     self.redis.publish("/live-event", json.dumps({"transaction_id": str(uuid.uuid1()),"eventType":eventType, "transaction_id":1, **args[0]}))

    # def add_area(self, area, parent_uuid = ""):
    #     area_repr = area_to_string(area)
    #     area_dic = json.loads(area_repr)
    #     self._run_live_command("create_area", {"parent_uuid":parent_uuid, "area_representation":area_dic})


        

    