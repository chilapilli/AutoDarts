from .base_game import BaseGame, Score, INTERRUPT
from player.main import Player, PlayerManager
import logging


class HighLowGame(BaseGame):

    def __init__(self, player_manager: PlayerManager,
                 high_only: bool = False,
                 total_lives: int = 3):
        super().__init__(player_manager)
        self._end_called = False
        self.is_game_over = False
        self.high_only = high_only  # if False, alternates between high and low rounds
        self.total_lives = total_lives
        self.players_eliminated = []
        self.current_round_is_high_or_low = 'high_round'

    def start(self):
        self._initialize_player_scores()
        logging.info(f"[High-Low]: Game started with {len(self.player_manager.players)} players.")
        while not self.is_game_over:
            self.all_player_round()

    def end(self):
        if self._end_called:
            return
        self._end_called = True
        self.is_game_over = True
        logging.info("[High-Low]: Game terminated.")
        self._notify_game_end()

    def all_player_round(self):
        round_label = 'high' if self.current_round_is_high_or_low == 'high_round' else 'low'
        logging.info(f"[High-Low]: A {round_label} round is initiated.")

        all_player_scores_map = {}

        while (len(self.players_eliminated) + len(all_player_scores_map.keys())) < len(self.player_manager.players):
            current_player = self.player_manager.get_current_player_object()
            
            if self.is_game_over: return
            if current_player in self.players_eliminated: continue

            self.current_player_round(current_player)
            if self.is_game_over:
                return
            all_player_scores_map[current_player] = current_player.additional_attributes['high_low_current_round_score']
            self.player_manager.next_player()   

        self.process_elimination(all_player_scores_map)
        self.check_win()
        if not self.is_game_over:
            self.increment_round_type()

    def process_elimination(self, all_player_scores_map: dict):
        if not all_player_scores_map:
            return

        if self.current_round_is_high_or_low == 'high_round':
            critical_score = min(all_player_scores_map.values())
        else:
            critical_score = max(all_player_scores_map.values())

        losers = [player for player, score in all_player_scores_map.items() if score == critical_score]
        self.decrement_player_lives(losers)

    def decrement_player_lives(self, list_of_players_to_decrement: list[Player]):
        for player in list_of_players_to_decrement:
            player.additional_attributes["high_low_lives_remaining"] -= 1
            remaining = player.additional_attributes["high_low_lives_remaining"]
            logging.info(f"[High-Low]: {player.name} loses 1 life — {remaining} remaining.")
            if remaining == 0:
                self.players_eliminated.append(player)
                logging.info(f"[High-Low]: {player.name} has been eliminated.")

    def check_win(self):
        active = [p for p in self.player_manager.players if p not in self.players_eliminated]
        if len(active) == 1:
            winner = active[0]
            winner.increment_rounds_won()
            logging.info(f"[High-Low]: {winner.name} wins!")
            self.end()
        elif len(active) == 0:
            logging.info("[High-Low]: All players eliminated simultaneously — no winner.")
            self.end()

    def increment_round_type(self):
        if self.high_only:
            return
        if self.current_round_is_high_or_low == 'high_round':
            self.current_round_is_high_or_low = 'low_round'
        else:
            self.current_round_is_high_or_low = 'high_round'

    def current_player_round(self, player: Player):
        total_for_turn = 0
        for i in range(3):
            score = self._wait_for_throw()
            if score is INTERRUPT:
                self.end()
                return
            total_for_turn += score.total
            logging.info(f"[High-Low]: {player.name} threw {score.total} (throw {i+1}/3).")

        logging.info(f"[High-Low]: {player.name}'s round total: {total_for_turn}.")
        player.additional_attributes["high_low_current_round_score"] = total_for_turn

    def process_throw_score(self, score: Score):
        pass

    def get_display_state(self):
        pass

    def _initialize_player_scores(self):
        for player in self.player_manager.players:
            player.additional_attributes["high_low_current_round_score"] = 0
            player.additional_attributes["high_low_lives_remaining"] = self.total_lives
