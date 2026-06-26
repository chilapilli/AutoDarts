

from games import base_game
from player.main import Player
import logging


class AroundTheClockGame(base_game.BaseGame):
    
    def __init__(self, player_manager):
        super().__init__(player_manager)
        self.is_game_over = False
        self._winner = None
        self.player_manager = player_manager
        self._end_called = False
    
    def start(self):
        print('test')

    def end(self):
        pass

    def current_player_round(self, player: Player):
        pass

    def process_throw_score(self, score: base_game.Score):
        pass

    def check_win(self):
        pass

    def get_display_state(self):
        """
        this returns a dictionary of the current game state, which can be used to display the current game state on a screen or other display device. The exact contents of the dictionary will depend on the specific game being played.
        """
        pass
