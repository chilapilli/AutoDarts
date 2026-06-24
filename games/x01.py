from base_game import BaseGame
from player import playerManager

class X01Game(BaseGame):

    def __init__(self, starting_score):
        self.starting_score = starting_score
        self.current_score = starting_score
        self.is_game_over = False

    def start(self):
        pass

    def end(self):
        pass


    def process_throw(self, score):
        pass

    def check_win(self):
        pass

    def get_display_state(self):
        pass
