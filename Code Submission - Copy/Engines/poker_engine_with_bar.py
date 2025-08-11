import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from tqdm import tqdm
from pypokerengine.api.game import setup_config, start_poker
from Opponent_bots.sample_player_types import FishPlayer, HonestPlayer, RandomPlayer
from Opponent_bots.Rule_based_player import RuleBased
from Opponent_bots.Monte_carl_bot import MonteCarloBot
from CFRs.CFR_for_engine import CFREngine
from CFRs.CFRv2_for_engine import CFREngineV2
import cProfile

config = setup_config(max_round=1, initial_stack=1000, small_blind_amount=5)
#config.register_player(name="fish", algorithm=FishPlayer())
#config.register_player(name="CFRv1", algorithm=CFREngine())
config.register_player(name="Honest_player", algorithm=HonestPlayer())
#config.register_player(name="Rule-Based", algorithm=RuleBased())
#config.register_player(name="Random-Player", algorithm=RandomPlayer())
#config.register_player(name="Monte Carlo", algorithm=MonteCarloBot())
config.register_player(name="CFRv2", algorithm=CFREngineV2())
n_games = 100000  # Number of games to simulate
final_stack_totals = {}


for game_num in tqdm(range(n_games), desc="Simulating games"):
    game_result = start_poker(config, verbose=0)
    
    # Print per-game stacks
    print(f"\n--- Game {game_num + 1} Results ---")
    for player in game_result["players"]:
        name = player["name"]
        stack = player["stack"]
        print(f"Player {name} stack: {stack}")
        # Update cumulative stacks
        final_stack_totals[name] = final_stack_totals.get(name, 0) + stack
    
    # Calculate cumulative metrics
    current_games = game_num + 1
    total_hands = current_games * config.max_round
    initial_stack_per_game = config.initial_stack
    sb_amount = 5
    
    print(f"\nCumulative after {current_games} game(s):")
    for name, total_stack in final_stack_totals.items():
        total_profit = total_stack - (initial_stack_per_game * current_games)
        sb_per_hand = total_profit / (sb_amount * total_hands)
        print(f"Player {name}: {sb_per_hand:.2f} sb/h")