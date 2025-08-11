# Monte Carlo code is from https://github.com/vdrumsta/playable_poker_bot



from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
import csv
import ast  
from pypokerengine.engine.poker_constants import PokerConstants as Const
from CFRs.CFR_V1.abstractions import SuitlessAbstractionHoleCommunity
from pypokerengine.utils.card_utils import _pick_unused_card, _fill_community_card, gen_cards
from pypokerengine.engine.hand_evaluator import HandEvaluator
import pandas as pd
import random

round_count_cfr = 0
BIG_BLIND = 10

df = pd.read_csv("training_data/cfr_training_data_clean.csv")

# needs to read cfr_training.txt 
# 
class CFREngine(BasePokerPlayer):  # Do not forget to make parent class as "BasePokerPlayer"
# MONTE CARLO FUNCTIONS:
    def __init__(self):
        super().__init__()
        self.wins = 0
        self.losses = 0

    def ActPass(self, valid_actions):
        #print('Pass')
        for act in valid_actions:
            if (act["action"] == 'call'):
                if (act["amount"] == 0):
                    return act["action"], act["amount"]
                break
        return 'fold', 0
   
    def ActCall(self, valid_actions):
       # print('Call')
        for act in valid_actions:
            if (act["action"] == 'call'):
                    return act["action"], act["amount"]
        return 'fold', 0
   
    def ActRaise_x1(self, valid_actions):
        #print('RaiseMin')
        for act in valid_actions:
            if (act["action"] == 'raise'):
                return act["action"], act["amount"]["min"]
        return self.ActCall(valid_actions)

    def ActRaise_x2(self, valid_actions):
        #print('RaiseMin')
        for act in valid_actions:
            if (act["action"] == 'raise'):
                return self.ActRaise(valid_actions, act["amount"]["min"]*2)

        return self.ActCall(valid_actions)
 
    def ActRaise(self, valid_actions, amount):
        #print('Raise')
        for act in valid_actions:
            if (act["action"] == 'raise'):
                if (amount >= act["amount"]["min"]):
                    if (amount <= act["amount"]["max"]):
                        return act["action"], amount
                    else:
                        return act["action"], act["amount"]["max"]
                elif (act["amount"]["min"] == -1):
                    return self.ActCall(valid_actions)
                else:
                    return act["action"], act["amount"]["min"]

    vChanceCall  = {'preflop': 0.13, 'flop': 0.3, 'turn': 0.4, 'river':0.7}
    vChanceRaise_x1  = {'preflop': 0.17, 'flop': 0.45, 'turn': 0.47, 'river':0.8}
    vChanceRaise_x2  = {'preflop': 0.20, 'flop': 0.55, 'turn': 0.47, 'river':0.9}
# BLUEPRINT FUNCTIONS:    
    @staticmethod
    def get_information_set_engine(round_state, hole_card, community_cards):
        """
        Combines the hole cards and all betting actions into a single string.
        For actions, each is abbreviated using the mapping:
          SMALLBLIND -> s, BIGBLIND -> b, CALL -> c, RAISE -> r, FOLD -> f

        information set is hole cards + actions taken from both sides
        """
        # Combine hole cards (e.g., ["HA","S4"] becomes "HAS4")
        concatenated_hole_cards = "".join(hole_card)

        cocatenated_community_cards = "".join(community_cards)
        
        # Retrieve all action histories from the round_state
        action_history = round_state.get("action_histories", {})
        only_action_history_preflop = action_history.get("preflop", [])
        only_action_history_flop = action_history.get("flop", [])
        only_action_history_turn = action_history.get("turn", [])
        only_action_history_river = action_history.get("river", [])

        # Extract actions from each street
        actions = [entry["action"] for entry in only_action_history_preflop]
        if only_action_history_flop:
            actions.extend([entry["action"] for entry in only_action_history_flop])
        if only_action_history_turn:
            actions.extend([entry["action"] for entry in only_action_history_turn])
        if only_action_history_river:
            actions.extend([entry["action"] for entry in only_action_history_river])
        
        # Map full action names to abbreviations
        action_map = {
            "SMALLBLIND": "",
            "BIGBLIND":   "",
            "CALL":       "c",
            "RAISE":      "r",
            "FOLD":       "f"
        }
        shortened_actions = [action_map.get(action, action) for action in actions]
        concatenated_actions = "".join(shortened_actions)
        
        # Combine the hole cards with the actions
        concatenated_history = concatenated_hole_cards + " " + cocatenated_community_cards + " " + concatenated_actions

        #print("this is what action looks like" + action) #just tells my next action aka the information set for the opponent, however it doesn't add the opponents action 

        
        return concatenated_history
    
    @staticmethod
    def information_set_to_abstracted_set(raw_information_set):
        parts = raw_information_set.split()
        hole_cards = parts[0]
        hole_cards_into_format = [hole_cards[:2], hole_cards[2:]]

        # Handle community cards + history 
        if len(parts) == 3:  
            community_part = parts[1]
            history = parts[2]
        else:  
            community_part = ""
            history = parts[1] if len(parts) > 1 else ""

        # Process community cards if present
        community_cards_into_format = []
        if community_part:
            community_cards_into_format = [
                community_part[i:i+2]
                for i in range(0, len(community_part), 2)
            ]

        abstracted_information_set = SuitlessAbstractionHoleCommunity.abstract_info_set(
            hole_cards_into_format,
            community_cards_into_format,
            history
        )
        return abstracted_information_set
    #print(information_set_to_abstracted_set("H7DQ DJSQD7 cc"))

    def get_strategy(df, search_key):
        search_key = str(search_key).strip()
        first_col = df.iloc[:, 0].astype(str).str.strip()  
        match = df[first_col == search_key]
        return match.iloc[0, 1] if not match.empty else None

    @staticmethod
    def select_action_from_strategy(strategy):
        # Handle case where no strategy exists for this information set
        if strategy is None:
            return CFREngine.no_information_set_strategy()
        
        try:          
            strategy_weights = ast.literal_eval(strategy)
            
            action_index = random.choices(
                range(3), 
                weights=strategy_weights,
                k=1
            )[0]
            
            return action_index
            
        except (SyntaxError, ValueError, TypeError) as e:
            print(f"Invalid strategy format: {e}. Using default strategy")
            return CFREngine.no_information_set_strategy()  # Fallback to default
        
    @staticmethod
    def no_information_set_strategy():
        #print("NOT CFR STRATEGY USED")
        # Example: Always call by default
        return "not blueprint"  # 0=fold, 1=call, 2=raise


    def action_to_engine(selected_action, valid_actions, round_state):
        #print("THIS IS THE SELECTED_ACTION", selected_action)
        try:
            if selected_action == 0:
                return valid_actions[0]["action"], valid_actions[0]["amount"]
            elif selected_action == 1:
                return valid_actions[1]["action"], valid_actions[1]["amount"]
            elif selected_action == 2:
                # Check if raise is actually allowed
                action = valid_actions[2]
                action["amount"] = 3 * BIG_BLIND

            return action["action"], action["amount"]
            
        except Exception as e:
            print(f"Error: {e}. Defaulting to fold.")
        return valid_actions[0]["action"], valid_actions[0]["amount"]
        
    
    #print(get_strategy(df, "98s TT5 rcrr"))

    def declare_action(self, valid_actions, hole_card, round_state):

        # BLUEPRINT
        community_cards = round_state["community_card"]
        #get the raw information set from engine
        raw_information_set = CFREngine.get_information_set_engine(round_state, hole_card, community_cards)
        #abstract it using the abstraction used in training 
        abstracted_information_set = CFREngine.information_set_to_abstracted_set(raw_information_set)
        #get the strategy looks like [0.9,0.1,0.1]
        strategy = CFREngine.get_strategy(df,abstracted_information_set)
        #select the specific action
        selected_action = CFREngine.select_action_from_strategy(strategy)
        #print(selected_action)

        if selected_action == "not blueprint":
            #use monte carlo
            win_rate = estimate_win_rate(50, self.players_remaining, hole_card, round_state['community_card'])

            if (win_rate > self.vChanceRaise_x2[round_state['street']]):
                return self.ActRaise_x2(valid_actions)
            if (win_rate > self.vChanceRaise_x1[round_state['street']]):
                return self.ActRaise_x1(valid_actions)
            elif (win_rate > self.vChanceCall[round_state['street']]):
                return self.ActCall(valid_actions)
            else:
                return self.ActPass(valid_actions)
        else:
            #use blueprint
            action, amount = CFREngine.action_to_engine(selected_action, valid_actions, round_state)
            return action,  amount

        #return action, amount   # action returned here is sent to the poker engine

    def receive_game_start_message(self, game_info):
        self.num_players = game_info['player_num']
        

    def receive_round_start_message(self, round_count, hole_card, seats):
        self.players_remaining = calculate_players_remaining(seats)
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        is_winner = self.uuid in [item['uuid'] for item in winners]
        self.wins += int(is_winner)
        self.losses += int(not is_winner)


        pass

#MONTE CARLO IMPLEMENTATION
def estimate_win_rate(nb_simulation, nb_player, hole_card, community_card=None):
    if not community_card: community_card = []

    # Make lists of Card objects out of the list of cards
    community_card = gen_cards(community_card)
    hole_card = gen_cards(hole_card)

    # Estimate the win count by doing a Monte Carlo simulation
    win_count = sum([montecarlo_simulation(nb_player, hole_card, community_card) for _ in range(nb_simulation)])
    return 1.0 * win_count / nb_simulation


def montecarlo_simulation(nb_player, hole_card, community_card):
    # Do a Monte Carlo simulation given the current state of the game by evaluating the hands
    community_card = _fill_community_card(community_card, used_card=hole_card + community_card)
    unused_cards = _pick_unused_card((nb_player - 1) * 2, hole_card + community_card)
    opponents_hole = [unused_cards[2 * i:2 * i + 2] for i in range(nb_player - 1)]
    opponents_score = [HandEvaluator.eval_hand(hole, community_card) for hole in opponents_hole]
    my_score = HandEvaluator.eval_hand(hole_card, community_card)
    return 1 if my_score >= max(opponents_score) else 0

def calculate_players_remaining(players):
    remaining_players = 0
    
    for player in players:
        if player['state'] == 'participating':
            remaining_players += 1

    return remaining_players

def clamp(num, min_value, max_value):
    return max(min(num, max_value), min_value)