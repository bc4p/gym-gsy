
import numpy as np

import gymnasium as gym
from gymnasium import spaces

from simulationController import SimulationController

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
