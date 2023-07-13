import gym
from gym import spaces
import numpy as np

class BidOfferEnv(gym.Env):
    def __init__(self, bids, offers):
        super(BidOfferEnv, self).__init__()
        self.bids = bids
        self.offers = offers
        self.num_bids = len(bids)
        self.num_offers = len(offers)
        self.action_space = spaces.Discrete(self.num_offers)
        self.observation_space = spaces.Discrete(self.num_bids)
        self.current_bid_index = 0
        self.done = False

    def reset(self):
        self.current_bid_index = 0
        self.done = False
        return self.current_bid_index - 1

    def step(self, action):
        assert self.action_space.contains(action)
        reward = 0
        info = {}
        if self.done:
            return self.current_bid_index - 1, reward, self.done, info
        
        current_bid = self.bids[self.current_bid_index]
        current_offer = self.offers[action]

        if current_offer["energy"] >= current_bid["energy"]:
            reward = current_offer["energy_rate"] - current_bid["energy_rate"]
            info["matched"] = True
        else:
            reward = -1
            info["matched"] = False

        self.current_bid_index = min(self.current_bid_index + 1, self.num_bids - 1)

        if self.current_bid_index == self.num_bids - 1:
            self.done = True

        return self.current_bid_index - 1, reward, self.done, info, current_bid, current_offer

class Agent:
    def __init__(self, env):
        self.env = env
        self.q_table = np.zeros((env.observation_space.n, env.action_space.n))

    def choose_action(self, state):
        return np.argmax(self.q_table[state, :])

    def update_q_table(self, state, action, reward, next_state):
        learning_rate = 0.1
        discount_factor = 0.9
        old_value = self.q_table[state, action]
        next_max = np.max(self.q_table[next_state, :])
        new_value = (1 - learning_rate) * old_value + learning_rate * (reward + discount_factor * next_max)
        self.q_table[state, action] = new_value

    def train(self, num_episodes):
        for episode in range(num_episodes):
            state = self.env.reset()
            done = False
            while not done:
                action = self.choose_action(state)
                next_state, reward, done, _,_,_ = self.env.step(action)
                self.update_q_table(state, action, reward, next_state)
                state = next_state


# env = BidOfferEnv(ac.current_bids, ac.current_offers)
# agent = Agent(env)
# agent.train(num_episodes=1000)

# # Test the learned policy
# state = env.reset()
# done = False
# unmatched_bids = []
# while not done:
#     action = agent.choose_action(state)
#     state, _, done, info , bid, offer= env.step(action)
#     if info["matched"]:
#         print(f"Bid Id {bid['id']} corresponding {bid['energy_rate']} price and {bid['energy']}is matching with {offer['id']} and {offer['energy_rate']} and {offer['energy']}"  )
#         print(f'Bid matched with Offer.')
        
#     else:
#         unmatched_bids.append(state)
        
# if len(unmatched_bids) == 0:
#     print("No matching Offer found.")
#     print(f'{bid["id"]} with {bid["energy_rate"]} and {bid["energy"]}')
#     print(f'{offer["id"]} with {offer["energy_rate"]} and {offer["energy"]}')


# for bid in unmatched_bids:
#     print(f"Bid {bid} was unmatched.")