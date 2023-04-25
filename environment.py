
import numpy as np

import gymnasium as gym
from gymnasium import spaces

from simulationController import SimulationController

class GsyEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    def __init__(self):
        self.sim_controller = SimulationController()
        pass

    def reset(self):
        self.sim_controller.start()
        pass

    def step(self):
        pass

    def render(self):
        pass

    def close(self):
        pass
