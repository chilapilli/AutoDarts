import random
from venv import logger

class Player:
    """
    Represents a single dart player and tracks their match statistics.
    """

    def __init__(self, name, rounds_won=0):
        """
        Args:
            name: The player's display name.
            rounds_won: Number of rounds won so far, defaults to 0.
        """
        self.name = name
        self.rounds_won = rounds_won
        self.rank = float('inf')  # This will be set when players are ranked
        self.additional_attributes = {}  # Placeholder for any additional attributes, such as health, which only apply to certain game types.

    def __repr__(self):
        return f"{self.name}: won {self.rounds_won} rounds, ranked {self.rank}"

    def __str__(self):
        return f"{self.name}: won {self.rounds_won} rounds, ranked {self.rank}"

    def increment_rounds_won(self):
        """Increment the player's round win count by one."""
        self.rounds_won += 1
        logger.info(f"[Player]: {self.name}'s round incremented 1 to {self.rounds_won}.")

    def decrement_rounds_won(self):
        """Decrement the player's round win count by one.

        Raises:
            ValueError: If rounds_won is already 0.
        """
        if self.rounds_won > 0:
            self.rounds_won -= 1
            logger.info(f"[Player]: {self.name}'s round decremented 1 to {self.rounds_won}.")
        else:
            logger.error(f"[Player]: Attempted to decrement rounds won for {self.name} below zero.")  
            raise ValueError("Rounds won cannot be negative.")

    

class PlayerManager:
    """Manages a collection of Players for a session across multiple rounds.

    Accepts a list of players as a JSON list, creates corresponding Player
    objects, and handles turn order, removal, and ranking.
    """

    def __init__(self, players_json):
        """
        Args:
            players_json: List of dicts with 'name' and optional 'rounds_won' keys.
        """
        self.players = [Player(player['name'], player.get('rounds_won', 0)) for player in players_json]
        self.current_player_index = self.get_random_player_index()
        logger.info(f"[PlayerManager]: Initialized with players: {[player.name for player in self.players]}. Starting with player index {self.current_player_index} ({self.players[self.current_player_index].name}).")


    def __repr__(self):
        return(f"[PlayerManager]: with ranked players: \n {'\n'.join([str(player) for player in self.get_ranked_players()])}")

    def get_random_player_index(self):
        """Return a random valid index into the players list."""
        return random.randint(0, len(self.players) - 1)

    def get_current_player_object(self):
        """Return the Player whose turn it currently is."""
        return self.players[self.current_player_index]

    def get_next_player_object(self):
        """Return the Player who will throw next, without advancing the turn."""
        return self.players[(self.current_player_index + 1) % len(self.players)]

    def next_player(self):
        """Advance the turn to the next player, wrapping around to the start."""
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def remove_player(self, player_name):
        
        """Remove a player from the session by name and pick a new random current player.

        Args:
            player_name: Name of the player to remove (assumed unique).
        """

        self.players = [player for player in self.players if player.name != player_name]
        self.current_player_index = random.randint(0, len(self.players) - 1)
        logger.info(f"[PlayerManager]: Removed player {player_name}. New current player index is {self.current_player_index} ({self.players[self.current_player_index].name}).")

    def get_ranked_players(self):
        
        """Return players sorted by rounds won descending, with rank assigned.

        Players with equal rounds_won receive the same rank (dense ranking).

        Returns:
            List of Player objects with their rank attribute set.
        """

        sorted_players = sorted(self.players, key=lambda player: player.rounds_won, reverse=True)
        current_rank = 1
        previous_player_score = float('inf')

        for player_index in range(len(sorted_players)):

            if sorted_players[player_index].rounds_won != previous_player_score:
                sorted_players[player_index].rank = current_rank
                previous_player_score = sorted_players[player_index].rounds_won
            else:
                sorted_players[player_index].rank = current_rank - 1 # on the next time their score would be subtracted from current_rank, so we add 1 here to keep the same rank for equal scores
            current_rank += 1

        return sorted_players

if __name__ == "__main__":
    example_players_json = [
        {"name": "Alice", "rounds_won": 12},
        {"name": "Bob", "rounds_won": 4},       
        {"name": "Charlie", "rounds_won": 12},
        {"name": "David", "rounds_won": 7},
        {"name": "Eve", "rounds_won": 4}
    ]

    players = PlayerManager(example_players_json)
    players.get_current_player_object().increment_rounds_won()
    print(players)

    players.remove_player("Charlie")
    print(players)


