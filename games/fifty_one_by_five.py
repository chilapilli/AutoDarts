from .base_game import BaseGame, Score, INTERRUPT
from player.main import Player
from player import PlayerManager
import logging

_SCORE_KEY = "51_by_5s_score"


class FiftyOneByFive(BaseGame):
    """51 by 5's dart game.

    Each turn a player throws 3 darts. The round total is only scored if it is
    divisible by 5, in which case the player earns total ÷ 5 points. A round
    that would push a player past 51 is a bust (0 points). First player to
    reach exactly 51 wins.
    """

    def __init__(self, playerManager: PlayerManager):
        super().__init__(playerManager)
        self.is_game_over = False
        self.player_manager = playerManager
        self._end_called = False
        self._winner: Player | None = None
        self._initialise_player_scores()

    def start(self):
        """Run the game loop until a player reaches 51 or an interrupt is received."""
        self.is_game_over = False

        while not self.is_game_over:
            current_player = self.player_manager.get_current_player_object()
            logging.info(
                f"[51 by 5's]: {current_player.name}'s turn. "
                f"Score: {current_player.additional_attributes[_SCORE_KEY]}."
            )
            self.current_player_round(current_player)
            if not self.is_game_over:
                self.player_manager.next_player()

        if self._winner:
            logging.info(f"[51 by 5's]: Game over. Winner: {self._winner.name}.")
        self.end()

    def end(self):
        """Terminate the game, flushing the throw queue and notifying listeners."""
        if self._end_called:
            return
        self._end_called = True
        self.is_game_over = True
        logging.info("[51 by 5's]: Game terminated.")
        self._notify_game_end()

    def current_player_round(self, player: Player):
        """Process one round (3 throws) for the given player."""
        round_total = 0

        for _ in range(3):
            score = self._wait_for_throw()
            if score is INTERRUPT:
                self.end()
                return
            logging.info(f"[51 by 5's]: {player.name} threw {score.total}.")
            round_total += score.total

        points = self.process_throw_score(score=Score(base_value=round_total), player=player)
        player.additional_attributes[_SCORE_KEY] += points
        self.check_win(player=player)

    def process_throw_score(self, score: Score, player: Player) -> int:
        """Return the points earned for a round total.

        Awards 0 if the total is not divisible by 5, or if it would push the
        player past 51 (bust). Otherwise awards total ÷ 5.
        """
        total = score.base_value
        current = player.additional_attributes[_SCORE_KEY]

        if total % 5 != 0:
            logging.info(
                f"[51 by 5's]: {player.name} scored {total} — not divisible by 5. "
                f"No points. Total: {current}."
            )
            return 0

        points = total // 5

        if points > 51 - current:
            logging.info(
                f"[51 by 5's]: {player.name} scored {total} — bust. "
                f"No points. Total: {current}."
            )
            return 0

        logging.info(
            f"[51 by 5's]: {player.name} scored {total} — +{points} points. "
            f"Total: {current + points}."
        )
        return points

    def check_win(self, player: Player):
        """Set the game as over if the player has reached exactly 51."""
        if player.additional_attributes[_SCORE_KEY] == 51:
            self.is_game_over = True
            self._winner = player
            player.increment_rounds_won()
            logging.info(f"[51 by 5's]: {player.name} reached 51 and wins!")

    def get_display_state(self) -> dict:
        """Return a snapshot of the current game state for the display layer."""
        current = self.player_manager.get_current_player_object()
        next_player = self.player_manager.get_next_player_object()

        return {
            "game_type": "51 by 5's",
            "game_state": {
                "current_player_name": current.name,
                "current_player_score": current.additional_attributes[_SCORE_KEY],
                "current_player_requires": 51 - current.additional_attributes[_SCORE_KEY],
                "next_player_name": next_player.name,
                "next_player_score": next_player.additional_attributes[_SCORE_KEY],
                "all_player_scores": {
                    player.name: player.additional_attributes[_SCORE_KEY]
                    for player in self.player_manager.players
                },
                "leaderboard": self.player_manager.get_ranked_players(),
            },
        }

    def _initialise_player_scores(self):
        """Set each player's starting score to 0."""
        for player in self.player_manager.players:
            player.additional_attributes[_SCORE_KEY] = 0
