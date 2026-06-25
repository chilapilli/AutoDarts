
import logging

from .base_game import INTERRUPT, BaseGame, Score
from player.main import Player, PlayerManager


class KillerGame(BaseGame):
    def __init__(self,
                 playerManager: PlayerManager,
                 requires_hitting_double_to_be_a_killer: bool,
                    # if True, then one must hit the double THREE TIMES
                    # if False, then one can hit ANYWHERE on their number to count as ONE time

                 requires_hitting_double_to_remove_shield: bool,
                    # if True, then one must hit the double to remove a shield
                    # if False, hitting anywhere on that number removes the shield

                 shields_per_player: int,
                 allow_recovery_of_shields: bool = False
                    # if True, anyone hitting your own number after becoming a killer will recover a shield
                    # if False, then hitting your own number also removes your own shield
                 ):
        super().__init__(playerManager)

        self.player_manager = playerManager
        self.is_game_over = False
        self.designated_numbers_assigned = {}
        self.eliminated_player_indices = []
        self.shields_per_player = shields_per_player
        self.requires_hitting_double_to_be_a_killer = requires_hitting_double_to_be_a_killer
        self.requires_hitting_double_to_remove_shield = requires_hitting_double_to_remove_shield
        self.allow_recovery_of_shields = allow_recovery_of_shields


    def start(self):
        self._initialising_roles()
        self._initialising_shields(self.shields_per_player)
        self._determining_designated_number()

        while not self.is_game_over:
            idx = self.player_manager.current_player_index
            if idx not in self.eliminated_player_indices:
                current_player = self.player_manager.get_current_player_object()
                self.current_player_round(player=current_player)
                self.check_win()
            self.player_manager.next_player()


    def end(self):
        """Immediately terminate the game."""
        self.is_game_over = True
        logging.info("[Killer]: Game terminated.")
        self._notify_game_end()


    def check_win(self):
        if len(self.eliminated_player_indices) == len(self.player_manager.players) - 1:
            self.is_game_over = True
            winner_index = next(
                i for i in range(len(self.player_manager.players))
                if i not in self.eliminated_player_indices
            )
            winner = self.player_manager.players[winner_index]
            winner.increment_rounds_won()
            logging.info(f"[Killer]: Game Over. The winner is {winner.name}.")
            self.end()


    def current_player_round(self, player: Player):
        for _ in range(3):
            if self.is_game_over:
                return
            self.throw(player=player)
            if self.player_manager.players.index(player) in self.eliminated_player_indices:
                logging.info(f"[Killer]: {player.name} eliminated themselves.")
                return


    def throw(self, player: Player):
        score = self._wait_for_throw()
        if score is INTERRUPT:
            self.end()
            return

        if player.additional_attributes["is_killer"]:
            self.killer_throw(score=score, player=player,
                              allow_recovery_of_shields=self.allow_recovery_of_shields,
                              requires_hitting_double_to_remove_shield=self.requires_hitting_double_to_remove_shield)
        else:
            self.non_killer_throw(score=score, player=player,
                                  requires_hitting_double_to_be_a_killer=self.requires_hitting_double_to_be_a_killer)


    def process_throw_score(self, score: Score):
        pass


    def get_display_state(self):
        pass


    def killer_throw(self, score: Score, player: Player,
                     allow_recovery_of_shields: bool,
                     requires_hitting_double_to_remove_shield: bool):
        """Handles the throw of a killer, and eliminates the target if their shields reach zero."""
        score_value = score.base_value

        if score_value not in self.designated_numbers_assigned:
            logging.info(f"[Killer]: {player.name} hit {score_value}, which is not anyone's number.")
            return

        target: Player = self.designated_numbers_assigned[score_value]

        if target == player:
            self._handle_self_hit(score, player, allow_recovery_of_shields, requires_hitting_double_to_remove_shield)
        else:
            self._handle_opponent_hit(score, player, target, requires_hitting_double_to_remove_shield)

        self._check_and_apply_elimination(target)


    def _handle_self_hit(self, score: Score, player: Player,
                         allow_recovery_of_shields: bool,
                         requires_hitting_double_to_remove_shield: bool):
        """Apply the effect of a player hitting their own designated number."""
        if allow_recovery_of_shields:
            self._increment_shields(player)
            logging.info(f"[Killer]: {player.name} hit their own number, recovers 1 shield ({player.additional_attributes['shields']} remaining).")
        elif not requires_hitting_double_to_remove_shield or score.is_double:
            self._decrement_shields(player)
            logging.info(f"[Killer]: {player.name} hit their own number, loses 1 shield ({player.additional_attributes['shields']} remaining).")
        else:
            logging.info(f"[Killer]: {player.name} hit their own number but not on a double — no shield removed.")


    def _handle_opponent_hit(self, score: Score, player: Player, target: Player,
                             requires_hitting_double_to_remove_shield: bool):
        """Apply the effect of a player hitting another player's designated number."""
        if not requires_hitting_double_to_remove_shield or score.is_double:
            self._decrement_shields(target)
            logging.info(f"[Killer]: {player.name} hits {target.name}'s number — {target.name} has {target.additional_attributes['shields']} shields remaining.")
        else:
            logging.info(f"[Killer]: {player.name} hit {target.name}'s number but not on a double — no shield removed.")


    def _check_and_apply_elimination(self, player: Player):
        """Eliminate the player if their shields have reached zero."""
        if player.additional_attributes["shields"] <= 0:
            player_index = self.player_manager.players.index(player)
            if player_index not in self.eliminated_player_indices:
                self.eliminated_player_indices.append(player_index)
                logging.info(f"[Killer]: {player.name} is eliminated from the game.")


    def non_killer_throw(self, score: Score,
                         player: Player,
                         requires_hitting_double_to_be_a_killer: bool):
        """Process a throw from a non-killer player working toward becoming a killer."""
        if not self._hits_designated_number(score, player):
            logging.info(f"[Killer]: {player.name} did not hit their designated number {player.additional_attributes['killer_designated_number']}.")
            return

        if self._counts_as_killer_progress(score, requires_hitting_double_to_be_a_killer):
            self._apply_killer_progress(player)
        else:
            logging.info(f"[Killer]: {player.name} hit their designated number but not on a double — no progress made.")

        self._check_if_player_becomes_killer(player)


    def _hits_designated_number(self, score: Score, player: Player) -> bool:
        """Return True if the throw lands on the player's designated number."""
        return score.base_value == player.additional_attributes['killer_designated_number']


    def _counts_as_killer_progress(self, score: Score, requires_double: bool) -> bool:
        """Return True if the throw counts toward becoming a killer."""
        return not requires_double or score.is_double


    def _apply_killer_progress(self, player: Player):
        """Decrement the player's remaining hits needed to become a killer and log progress."""
        player.additional_attributes['killer_designated_number_hits_remaining'] -= 1
        remaining = player.additional_attributes['killer_designated_number_hits_remaining']
        logging.info(f"[Killer]: {player.name} hit their designated number — {remaining} hits remaining to become killer.")


    def _check_if_player_becomes_killer(self, player: Player):
        if player.additional_attributes['killer_designated_number_hits_remaining'] <= 0:
            player.additional_attributes['is_killer'] = True
            logging.info(f"[Killer]: {player.name} has become a killer.")


    def _increment_shields(self, player: Player):
        player.additional_attributes["shields"] += 1


    def _decrement_shields(self, player: Player):
        player.additional_attributes["shields"] -= 1


    def _initialising_shields(self, shields_per_player: int):
        for player in self.player_manager.players:
            player.additional_attributes['shields'] = shields_per_player
        logging.info(f"[Killer]: All players assigned {shields_per_player} shields.")


    def _initialising_roles(self):
        for player in self.player_manager.players:
            player.additional_attributes['is_killer'] = False


    def _determining_designated_number(self):
        assigned_count = 0

        while assigned_count < len(self.player_manager.players):
            score = self._wait_for_throw()
            if score is INTERRUPT:
                self.end()
                return

            while score.base_value in self.designated_numbers_assigned:
                logging.info(f"[Killer]: {score.base_value} has already been assigned to {self.designated_numbers_assigned[score.base_value].name}, a rethrow is initiated.")
                score = self._wait_for_throw()

            if score.base_value == 0 or score.base_value > 20:
                logging.info(f"[Killer]: {self.player_manager.get_current_player_object().name} did not hit a valid number (1-20).")
                continue

            current = self.player_manager.get_current_player_object()
            self.designated_numbers_assigned[score.base_value] = current
            current.additional_attributes['killer_designated_number'] = score.base_value
            current.additional_attributes['killer_designated_number_hits_remaining'] = 3
            assigned_count += 1
            logging.info(f"[Killer]: {current.name} is assigned number {score.base_value}.")
            self.player_manager.next_player()

        logging.info(f"[Killer]: Designation complete — {self.designated_numbers_assigned}")
