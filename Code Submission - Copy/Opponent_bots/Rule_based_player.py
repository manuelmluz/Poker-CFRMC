from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
from pypokerengine.engine.hand_evaluator import HandEvaluator
import random

#COULD BE IMPROVED IF NEEDED

#Sample player types = Fishplayer, HonestPlayer
class RuleBased(BasePokerPlayer):  # Do not forget to make parent class as "BasePokerPlayer"
    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def pre_flop_range(self, hole_cards):
        #heuristics used:
        #play every pocket pair
        
        rank_order = "23456789TJQKA"
        #unpack the cards, rank and suit
        card1, card2 = hole_cards[0], hole_cards[1]
        suit1, suit2 = card1[0], card2[0]
        rank1, rank2 = card1[1:], card2[1:]

        #if its a pocket pair always play
        if rank1 == rank2:
            return True
        
        #if it has an ace always play
        pass
    
    def get_current_street(self,round_state):
        current_street = round_state["street"]
        return current_street
    
    def declare_action(self, valid_actions, hole_card, round_state):
        # SHOULD COMPUTE ESTIMATE_HOLE_CARD_WIN_RATE ONLY 1 TIME THEN RETURN THE LIST OF PLAYABLE HANDS, way faster

        # valid_actions format => [raise_action_info, call_action_info, fold_action_info]
        PREFLOP_RANGE_SIMULATIONS = 1000
        PREFLOP_RANGE_PERCENT_RANGE = 0.5 # only player top 50% of hands
        current_round = self.get_current_street(round_state)
        #if its preflop then use 50% of top hands
        win_rate=estimate_hole_card_win_rate(
            nb_simulation=PREFLOP_RANGE_SIMULATIONS,
            nb_player= 2,
            hole_card= gen_cards(hole_card),
            community_card= [])

        # evaluator of board for later rounds:
        if current_round in ["flop", "turn", "river"]:
            community_cards = round_state['community_card']
            pot_size = round_state["pot"]["main"]["amount"]
            hole_card_obj = gen_cards(hole_card)
            community_cards_obj = gen_cards(community_cards)
            hand_info = HandEvaluator.gen_hand_rank_info(hole_card_obj, community_cards_obj)
            strength = hand_info["hand"]["strength"]       
                # PREFLOP LOGIC:
                # always bet 3BB with preflop range
                # if hand not in preflop range
                #    always check when free, always pay for bb when in sb position if no raises ,or fold  
                     
        # preflop logic
        if current_round == "preflop":  # bet 3 Big blinds 
            if win_rate >= PREFLOP_RANGE_PERCENT_RANGE:
                action = valid_actions[2]
                action["amount"] = 3 * self.big_blind  # 3 BB
            else: 
                # check is free so always check
                if valid_actions[1]["amount"] == 0 or valid_actions[1]["amount"] <= 2 * self.small_blind:
                    action = valid_actions[1]
                else: 
                    action = valid_actions[0]
            # FLOP logic    
            # if hole cards connect with board e.g. pair, 2 pair ,3 card. straight etc 
            #   then bet
            # if board doesnt connect 
            #   check if possible else fold 
            #   
        elif current_round == "flop":
            #if board connects
            if strength in ["ONEPAIR", "TWOPAIR", "THREECARD", "STRAIGHT", "FLASH", "FULLHOUSE"]:
            #betting scheme 
                if pot_size <= 4 * self.big_blind:
                    action = valid_actions[2]
                    action["amount"] = 3 * self.big_blind
                else:
                    action = valid_actions[2]
                    action["amount"] = 0.5 * pot_size
            #if board doesnt connect
            else:
                if valid_actions[1]["amount"] == 0:
                    action = valid_actions[1]
                else:
                    action = valid_actions[0]
        # turn logic
        # if we hit we continue betting else check/ fold
        elif current_round == "turn":
            if strength in ["ONEPAIR", "TWOPAIR", "THREECARD", "STRAIGHT", "FLASH", "FULLHOUSE"]:
                action = valid_actions[2]
                action["amount"] = 0.5 * pot_size
            else:
                if valid_actions[1]["amount"] == 0:
                    action = valid_actions[1]
                else:
                    action = valid_actions[0]
        #river logic
        # if we hit we continue betting else check/ fold
        else:
            if strength in ["ONEPAIR", "TWOPAIR", "THREECARD", "STRAIGHT", "FLASH", "FULLHOUSE"]:
                action = valid_actions[2]
                action["amount"] = 0.5 * pot_size
            else:
                if valid_actions[1]["amount"] == 0:
                    action = valid_actions[1]
                else:
                    action = valid_actions[0]

        return action["action"], action["amount"]


    def receive_game_start_message(self, game_info):
        
        self.small_blind = game_info["rule"]["small_blind_amount"]
        self.big_blind = 2 * self.small_blind
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass