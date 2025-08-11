import random
from phevaluator.evaluator import evaluate_cards
from abstractions import SuitlessAbstractionHoleCommunity

# 0=preflop, 1=flop, 2=turn, 3=river , FINISH THE GAME EARLIER IF WANTED # wont work for preflop because the hand evaluator only works between 5 and 7 cards
ROUND_LIMIT = 1 #
SUIT_MAP = {'H': 'h', 'D': 'd', 'S': 's', 'C': 'c'}
ACTIONS = ("f", "c", "r")
MAX_RAISES_PER_ROUND = 2
RAISE_AMOUNT = 20

class GameState:
    DECK = [f"{s}{r}" for s in "HDSC" for r in "23456789TJQKA"]  # Class-level constant

    def __init__(self,acting_player,history, player1_hole_cards, player2_hole_cards, community_cards,
                 pot, round_number,pre_sampled_community , folded_player=None):
        self.acting_player = acting_player
        self.history = history
        self.player1_hole_cards = player1_hole_cards
        self.player2_hole_cards = player2_hole_cards
        self.community_cards = community_cards
        self.pot = pot
        self.round_number = round_number 
        self.pre_sampled_community = pre_sampled_community
        self.folded_player = folded_player
  
    def get_info_set(self):
        """
        ABSTRACTION STUFF: 
        

        return f"{''.join(hole_cards)}{self.round_number}{''.join(self.community_cards)}{self.history}"

        from abstractions import SuitlessAbstractionHoleCommunity  # Local import
        return SuitlessAbstractionHoleCommunity.abstract_info_set(
            hole_cards,  # Pass the correct player's hole cards
            self.community_cards,
            self.history

        from abstractions import SuitlessAbstractionHoleCards  # Local import
        return SuitlessAbstractionHoleCards.abstract_info_set(self)

        return RemoveCommunityCardsAbstraction.abstract_info_set(self)

        from abstractions import SuitlessAbstractionHoleCommunity  # Local import
        return SuitlessAbstractionSuitlessAbstractionHoleCommunity.abstract_info_set(self)

        """
        hole_cards = self.player1_hole_cards if self.acting_player == 1 else self.player2_hole_cards 

        return SuitlessAbstractionHoleCommunity.abstract_info_set(
            hole_cards,  # Pass the correct player's hole cards
            self.community_cards,
            self.history)
        
    def next_acting_player(self): # i think i need to implement this in apply_action
        """Simply alternates between players 1 and 2"""
        return 2 if self.acting_player == 1 else 1
            
        # alternate between player 1 and 2. then reset if round is over
        # read the history and determine it through that 
        
    def is_chance_node(self):
        #need to check if round is over
        #this will think when the game is done it will return true which it should not do
        if self.is_round_over() == True and self.round_number == 0: #WILL NEED TO EXPAND THIS FOR FULL GAME
            return True
        else:
            return False

    def sample_chance_outcome(self): # just changes community cards from the current state, not in apply action anymore
        target = {0: 3, 1: 4, 2: 5}.get(self.round_number, 0) #i think this might need to be #target = {1: 3, 2: 4, 3: 5}.get(self.round, 0), because i havent implement moving rounds yet
        current = len(self.community_cards)
        needed = max(0, target - current)

        new_community = list(self.community_cards)
        if needed > 0:
            self.community_cards += self.pre_sampled_community[current:target]  

        new_state = GameState(
            self.acting_player,
            self.history,
            self.player1_hole_cards,
            self.player2_hole_cards,
            self.community_cards,
            pot=self.pot,
            round_number=self.round_number + 1, # next round (should this be in apply action instead?)
            pre_sampled_community=self.pre_sampled_community
        )
        return new_state
        
    def is_round_over(self):
        # keep the existing fold‑safety check
        if self.history[-1:] == "f":
            return True

        # no actions yet → round obviously not finished
        if not self.history:
            return False

        # find where the *previous* round ended
        last_round_end = 0
        i = 0
        while i < len(self.history) - 1:
            if self.history[i:i + 2] in ("cc", "rc"):
                last_round_end = i + 2          # start of the current round
                i += 2                          # skip the pair we just matched
            else:
                i += 1

        current_round_actions = self.history[last_round_end:]

        # if current_round_actions is empty we completed a round
        if current_round_actions == "":
            return True

        # otherwise, the round ends only when its last two actions are cc or rc
        return (
            len(current_round_actions) >= 2
            and current_round_actions[-2:] in ("cc", "rc")
        )
    @classmethod
    def new_hand(cls):
        """
        FIXED_HOLE_CARDS = ["HA", "DA"]
        player1_hole_cards_str = FIXED_HOLE_CARDS.copy()

        player1_hole_cards_str = random.sample(cls.DECK, 2)
        remaining = [c for c in cls.DECK if c not in player1_hole_cards_str]
        """
        player1_hole_cards_str = random.sample(cls.DECK, 2)
        remaining = [c for c in cls.DECK if c not in player1_hole_cards_str]

        player2_hole_cards_str = random.sample(remaining, 2)
        remaining = [c for c in remaining if c not in player2_hole_cards_str]
        community_cards = random.sample(remaining, 5)

        return cls(
            acting_player = 1, # player 1 always starts , players are 1 and 2 
            history = "",
            player1_hole_cards = player1_hole_cards_str,
            player2_hole_cards = player2_hole_cards_str,
            community_cards = community_cards[:0], # initially no community cards, but maybe i should add it???
            pot = 15, 
            round_number = 0,
            pre_sampled_community=community_cards,
            folded_player= None

        )

    def is_terminal(self):
        if "f" in self.history:
            return True
        if self.round_number == ROUND_LIMIT:
            rounds_found = 0
            last_round_end = 0
            i = 0
            while i < len(self.history) - 1 and rounds_found < ROUND_LIMIT:
                if self.history[i:i+2] in ("cc", "rc"):
                    rounds_found += 1
                    last_round_end = i + 2
                    i += 2
                else:
                    i += 1
            river_actions = self.history[last_round_end:]
            return len(river_actions) >= 2 and river_actions[-2:] in ("cc", "rc")
        if self.round_number > ROUND_LIMIT:
            raise ValueError("round variable that is being used in is_terminal_state is greater than ROUND_LIMIT")
        return False     

    def _to_ph(self, cards):
        return [(c[1] + SUIT_MAP[c[0]]) for c in cards]
     
    def get_showdown_value(self, traversing_player): #its for the tranversing player, returns positive for traversing player when they win and vice versa
        #if its a fold
        #need to see if this is right
        #dont know if signs are correct
        if "f" in self.history: 
            return self.pot if self.folded_player != traversing_player else -self.pot 
        #this returns negative for a fold however CFR then has a negative sign why?
        #this seems like its just the oppositve right now so i could just switch signs??
        
        # Showdown case
        board = self._to_ph(self.community_cards)
        p1_cards = board + self._to_ph(self.player1_hole_cards)
        p2_cards = board + self._to_ph(self.player2_hole_cards)

        p1_score = evaluate_cards(*p1_cards)  # lower score = better hand
        p2_score = evaluate_cards(*p2_cards)

        # returns pot 
        if traversing_player == 1:
            if p1_score < p2_score:
                return self.pot   # Traversing player 1 wins  
            elif p1_score > p2_score:
                return -self.pot  # Traversing player 1 loses 
        else:  # traversing_player == 2
            if p2_score < p1_score:
                return self.pot   # Traversing player 2 wins
            elif p2_score > p1_score:
                return -self.pot  # Traversing player 2 loses

        return 0.0  # Split pot
            
    def is_invalid_raise(self,action): 
        if self.action_to_str(action) != "r":
            return False  # Only check raise actions
        
        last_round_end = 0
        for i in range(len(self.history)-1):
            if self.history[i:i+2] in ('cc', 'rc'):
                last_round_end = i + 2
        current_round_actions = self.history[last_round_end:]
        
        starting_player = (len(self.history) - len(current_round_actions)) % 2
        current_player_raises = 0
        for idx, act in enumerate(current_round_actions):
            acting_player = (starting_player + idx) % 2
            if acting_player == self.acting_player and act == 'r':
                current_player_raises += 1
                
        return current_player_raises >= MAX_RAISES_PER_ROUND  
    @staticmethod
    def action_to_str(action):
        return ACTIONS[action]  # Uses existing ACTIONS tuple ("f", "c", "r")  
    
    def apply_action(self, action ): 

        #dealing with folds:
        new_folded=None
        if action == 0:
            new_folded = self.acting_player

        # Calculate new pot
        new_pot = self.pot
        if action == 2:  # Raise
            new_pot += RAISE_AMOUNT 
        elif action == 1:  # Call
            new_pot += 10

        action_str = self.action_to_str(action)

        new_state = GameState(
            acting_player=self.next_acting_player(),  #rotate playing
            history=self.history + action_str,
            player1_hole_cards=self.player1_hole_cards.copy(),
            player2_hole_cards=self.player2_hole_cards.copy(),
            community_cards=self.community_cards.copy(),
            pot=new_pot,
            round_number=self.round_number,
            pre_sampled_community=self.pre_sampled_community,
            folded_player=new_folded,
            

        )
        return new_state