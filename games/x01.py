from .base_game import BaseGame, Score, INTERRUPT
from player import PlayerManager
from player.main import Player
import logging


logging.basicConfig(level=logging.INFO)

class X01Game(BaseGame):

    """
    Logic for one round/ one session of X01 game
    """

    def __init__(self, starting_score: int, playerManager: PlayerManager, ends_on_double_to_win: bool = True):
        """
        Args:
            starting_score: The initial score for each player.
            playerManager: The manager for handling player-related operations.
            ends_on_double_to_win: Whether the game ends when a player hits a double.
        """
        super().__init__(playerManager) # need this so that _throw_queue is initialized in BaseGame 
        self.starting_score = starting_score
        self.current_score = starting_score
        self.is_game_over = False
        self.ends_on_double_to_win = ends_on_double_to_win
        self.player_manager = playerManager
        self._end_called = False


    def start(self):
        """
        Logic to start the X01 game session, handling player turns and ends when there is a winner.
        """
        self.set_player_starting_score() # set all players' starting score to the game starting score   
        self.is_game_over = False

        while not self.is_game_over:   
            current_player = self.player_manager.get_current_player_object() 
            logging.info(f"[X01]: New round, {current_player.name}'s turn. Current score: {current_player.additional_attributes['x01_current_score']}")
            self.current_player_round(current_player)
            
            if not self.is_game_over:
                self.player_manager.next_player()

        logging.info(f"[X01]: Game Terminated, winner: {current_player.name}.")
        self.end()  # Call the end method to handle game termination and notify any listeners


    def end(self):
        """Immediately terminate the game."""
        if self._end_called:
            return
        self._end_called = True
        self.is_game_over = True
        logging.info("[X01]: Game terminated.")
        self._notify_game_end()

    def current_player_round(self, player: Player):
        """
        Handle a single round for the current player, processing up to three throws.
        """

        for i in range(3):
            existing_score = player.additional_attributes['x01_current_score']
            score = self._wait_for_throw()

            if score is INTERRUPT:
                self.end()
                return

            self.check_win(score, existing_score) # if the game is won is_game_over is set to True
            
            if not self.is_game_over and self.is_valid_throw(score, existing_score):

                new_score = existing_score - self.process_throw_score(score) # updates scores
                player.additional_attributes['x01_current_score'] = new_score # updates that score also in the Player's attributes
                
                logging.info(f"[X01]: {player.name} scored {score.total}, new score: {new_score}")
                logging.info(f"[X01]: Game state is updated as {
                    self.get_display_state()
                }")
            

            elif not self.is_game_over and not self.is_valid_throw(score, existing_score):
                logging.info(f"[X01]: Invalid throw for player {player.name}: {score.total} cannot be scored from {existing_score}.")

            else:
                logging.info(f"[X01]: {player.name} scored {score.total}, new score: {existing_score - self.process_throw_score(score)}")
                logging.info(f"[X01]: {player.name} wins.")
                player.increment_rounds_won()
                break


    def process_throw_score(self, score_for_throw: Score):
        """
        Process the throw score and return the total score for that throw.
        """
        return score_for_throw.total


    def is_valid_throw(self, score: Score, current_score: int, ends_on_double_to_win: bool = True):
        """Check if the throw is valid based on the current score.

        Args:
            score: The Score object representing the throw.
            current_score: The player's current score before the throw.
            ends_on_double: Whether the game ends when a player hits a double.

        """

        # only the following three possibilities, otherwise either a bust, or not ending in a double when we require to end on a double        
        if score.total < current_score: 
            return True
        
        if ends_on_double_to_win and score.total == current_score and score.is_double: # ends the round
            return True
    
        if not ends_on_double_to_win and score.total == current_score: # ends the round
            return True

        return False

    def check_win(self, score: Score, current_score: int, ends_on_double_to_win: bool = True):
        """
        Check if the current throw results in a win for the player, updates is_game_over accordingly.
        """
        if score.total != current_score: 
            self.is_game_over = False

        elif score.total == current_score and ends_on_double_to_win and not score.is_double: # note the above if statement ensures that score.total == current_score, so we only need to check if it is a double or not
            self.is_game_over = False
            logging.info(f"Invalid throw: {score.total} cannot be scored from {current_score} because it does not end on a double.")

        else: 
            self.is_game_over = True

    def get_display_state(self):
        """Return a snapshot of the current game state for the display layer."""
        current_player = self.player_manager.get_current_player_object()
        next_player = self.player_manager.get_next_player_object()

        return {
            "game_type": "X01",
            "game_state": { 
            "current_player_name": current_player.name,
            "current_player_score": current_player.additional_attributes["x01_current_score"],
            "next_player_name": next_player.name,
            "next_player_score": next_player.additional_attributes["x01_current_score"],
            "all_player_scores": {player.name: player.additional_attributes["x01_current_score"]
                                  for player in self.player_manager.players},
            "leaderboard": self.player_manager.get_ranked_players()
        }}

    def set_player_starting_score(self):
        """
        Sets the additional_attributes['x01_current_score'] for each player to the starting score of the game.
        """
        for player in self.player_manager.players:
            player.additional_attributes['x01_current_score'] = self.starting_score


if __name__ == "__main__":
    pass
