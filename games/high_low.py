from .base_game import BaseGame, Score, INTERRUPT
from player.main import Player, PlayerManager
import logging


class HighLowGame(BaseGame):
    

    def __init__(self, player_manager: PlayerManager):
        
        super().__init__(player_manager)
        self._end_called = False


    def start(self):
        print('test')

    def end(self):
        pass

    def current_player_round(self, player: Player):
        pass

    def process_throw_score(self, score: Score):
        pass

    def check_win(self):    
        pass

    def get_display_state(self):
        pass





