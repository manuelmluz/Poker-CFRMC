
from collections import defaultdict



RANK_ORDER = {r: idx for idx, r in enumerate('23456789TJQKA')}

class SuitlessAbstractionHoleCards:
    
    @staticmethod
    def _ranks_only(cards):
        return [c[1] for c in cards]

    @staticmethod
    def card_strength(cards):
        c1, c2 = sorted(cards, key=lambda c: RANK_ORDER[c[1]], reverse=True)

        suited = c1[0] == c2[0]
        r1, r2 = c1[1], c2[1]
        
        return f"{r1}{r2}{'s' if suited else 'o'}"
        

    @staticmethod
    def abstract_info_set(game_state) -> str:
        return f"{SuitlessAbstractionHoleCards.card_strength(game_state.cards)} " \
               f"{game_state.community_cards} " \
               f"{game_state.round} " \
               f"{game_state.history} "

class SuitlessAbstractionHoleCommunity: 
    @staticmethod
    def abstract_community(community_cards):
        if not community_cards:
            return ''
        ranks = [c[1] for c in community_cards]
        sorted_ranks = sorted(ranks, key=lambda r: RANK_ORDER[r], reverse=True)
        return ''.join(sorted_ranks)

    @staticmethod
    def abstract_info_set(hole_cards, community_cards, history):
        return (
            f"{SuitlessAbstractionHoleCards.card_strength(hole_cards)} "
            f"{SuitlessAbstractionHoleCommunity.abstract_community(community_cards)} "
            f"{history}"
        )

