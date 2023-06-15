
import numpy as np

import gymnasium as gym
from gymnasium import spaces

from simulationController import SimulationController
from gsy_e.models.area import Market

class GsyEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    def __init__(self):
        self.sim_controller = SimulationController()
        self.obs = {}
        pass

    def reset(self):
        self.sim_controller.start()
        obs = self.sim_controller.current_observation
        info = self.sim_controller.current_info
        return obs, info

    def step(self):
        self.sim_controller.next_slot()
        obs = self.sim_controller.current_observation
        info = self.sim_controller.current_info
        terminated = self.sim_controller.is_finished
        reward = [0,0,0,0]
        return obs, reward, terminated, False, info

    def render(self):
        pass

    def close(self):
        pass

class MarketAgent(object):
    def __init__(self, area, marketNode) -> None:
        self.area = area
        self.strategy = area.strategy
        self.marketNode = marketNode
        pass

    def send_offer(self, rate, energy, replace_existing=False):
        self.strategy.post_offer(
            self.marketNode.spot_market,
            price = energy * rate / 1000.0,
            energy = energy / 1000.0,
            replace_existing=replace_existing
            
        )

    def send_bid(self, rate, energy, replace_existing=False):
        self.strategy.post_bid(
            self.marketNode.spot_market,
            energy * rate / 1000.0,
            energy / 1000.0,
            replace_existing=replace_existing

        )

class AgentsCoordinator():
    def __init__(self, agents: list[MarketAgent], market:Market)-> None:
        self.agents = agents
        self.market = market

    @property
    def spot_market(self):
        return self.market.spot_market

    @property
    def past_markets(self):
        return self.market.past_markets
    
    @property 
    def current_bids(self):
        return [bid.serializable_dict() for bid in list(self.spot_market.bids.values())]
    @property 
    def current_offers(self):
        return [offer.serializable_dict() for offer in list(self.spot_market.offers.values())]


    


