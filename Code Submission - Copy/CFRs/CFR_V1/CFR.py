
import numpy as np
from collections import defaultdict
from game_logic10 import GameState  
from tqdm import tqdm
import csv
import matplotlib.pyplot as plt

NUM_ACTIONS = 3  # Fold, Call, Raise
PLAYERS = {1, 2}

class Node:
    def __init__(self, information_set):
        self.information_set = information_set
        self.regret_sum = np.zeros(NUM_ACTIONS, dtype=np.float32)
        self.strategy_sum = np.zeros(NUM_ACTIONS, dtype=np.float32)

    def get_strategy(self, reach_prob):
        # Regret-matching
        strategy = np.maximum(self.regret_sum, 0)
        norm_sum = np.sum(strategy)
        if norm_sum > 0:
            strategy /= norm_sum
        else:
            strategy = np.ones(NUM_ACTIONS) / NUM_ACTIONS
        
        self.strategy_sum += reach_prob * strategy
        return strategy

    def get_average_strategy(self):
        norm_sum = np.sum(self.strategy_sum)
        if norm_sum > 0:
            return self.strategy_sum / norm_sum
        return np.ones(NUM_ACTIONS) / NUM_ACTIONS

class CFRTrainer:
    def __init__(self):
        self.nodes = defaultdict(lambda: None)

#ADD AVERAGE GAME VALUE AFTER EVERY 1000 or something
    def train(self, iterations, filename="cfr_training.csv"):
        util = 0.0
        self.util_at_x_iterations = []  # List to store averages at each 100 iterations
        total_steps = iterations * len(PLAYERS)
        with tqdm(total=total_steps, desc="Training CFR") as pbar:
            for iteration in range(iterations):
                for player in PLAYERS:
                    state = GameState.new_hand()
                    util += self.cfr(state, player, 1, 1)
                    pbar.update(1)  
                if (iteration + 1) % 1000 == 0: # every 100 rounds
                    current_avg = util / ((iteration + 1) * len(PLAYERS))
                    self.util_at_x_iterations.append(current_avg)
        print(f"Average game value: {util / (iterations * len(PLAYERS))}")
    
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["info_set", "strategies"])
            for information_set, node in self.nodes.items():
                if node:
                    strat = node.get_average_strategy()
                    writer.writerow([information_set, f"[{','.join(f'{s:.2f}' for s in strat)}]"])
    def plot_average_game_value(self):
        if not hasattr(self, 'util_at_x_iterations') or not self.util_at_x_iterations:
            raise ValueError("No training data available. Run training first.")
        
        x = [1000 * (i + 1) for i in range(len(self.util_at_x_iterations))]
        
        plt.figure(figsize=(10, 6))
        plt.plot(x, self.util_at_x_iterations, marker='o', linestyle='-')
        plt.xlabel("Training Iterations")
        plt.ylabel("Average Game Value")
        plt.title("CFR Training Progress: Average Game Value per 100 Iterations")
        plt.grid(True, which='both', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()

    def cfr(self, state, traversing_player, π1, π2):
        if state.is_terminal():
            return state.get_showdown_value(traversing_player)

        if state.is_chance_node():
            sampled_state = state.sample_chance_outcome() 
            return self.cfr(sampled_state, traversing_player, π1, π2) 

        acting_player = state.acting_player
        info_set = state.get_info_set()
        node = self.nodes.get(info_set)
        if node is None:
            node = Node(info_set)
            self.nodes[info_set] = node


        strategy = node.get_strategy(π1 if acting_player == 1 else π2)
        action_utils = np.zeros(NUM_ACTIONS)
        node_util = 0

        for action in range(NUM_ACTIONS):
            if state.is_invalid_raise(action):
                continue

            next_state = state.apply_action(action)

            if acting_player == 1: 
                action_utils[action] = self.cfr(next_state, traversing_player, π1 * strategy[action], π2)
            else:
                action_utils[action] = self.cfr(next_state, traversing_player, π1, π2 * strategy[action])
            
            node_util += strategy[action] * action_utils[action]

        if acting_player == traversing_player: 
            π_opponent = π2 if acting_player == 1 else π1
            for a in range(NUM_ACTIONS):                            
                regret = π_opponent * (action_utils[a] - node_util)
                node.regret_sum[a] += regret

        return node_util

        
        

if __name__ == "__main__":
    trainer = CFRTrainer()
    trainer.train(iterations=10000) 
    trainer.plot_average_game_value()