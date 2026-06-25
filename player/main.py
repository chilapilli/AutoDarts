import random
import logging
logger = logging.getLogger(__name__)

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

        additional_info = "\n            ".join([f"{key}: {value}" for key, value in self.additional_attributes.items()]) if self.additional_attributes else "None" 
        out_string = f"""
        ------------------------------------------
        Name:       {self.name}
        Rounds Won: {self.rounds_won}
        Ranking   : {self.rank}
        Additional Info: 
            {additional_info}
        ------------------------------------------
        """

        return out_string

    def increment_rounds_won(self):
        """Increment the player's round win count by one."""
        self.rounds_won += 1
        logger.info(f"[Player]: {self.name}'s round incremented to {self.rounds_won}.")

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
        ranked = self.get_ranked_players()
        lines = [f"  #{info['rank']} {name}: {info['won']} wins   ---     additional info '{info.get('additional_info', '')}'" for name, info in ranked.items()]
        return "[PlayerManager]: ranked players:\n" + "\n".join(lines)

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
            Json of Player objects with their rank attribute set, e.g., 

                {'Alice': {'won': 12, 'rank': 1}, 
                'Charlie': {'won': 12, 'rank': 1}, 
                'David': {'won': 7, 'rank': 3}, 
                'Bob': {'won': 4, 'rank': 4}, 
                'Eve': {'won': 4, 'rank': 4}}
        """

        sorted_players = sorted(self.players, key=lambda player: player.rounds_won, reverse=True)
        current_rank = 1

        for i, player in enumerate(sorted_players):
            if i == 0 or player.rounds_won != sorted_players[i - 1].rounds_won:
                current_rank = i + 1
            player.rank = current_rank

        sorted_players = {
            player.name: {
                'won': player.rounds_won, 
                'rank': player.rank,
                'additional_info': player.additional_attributes
            }
            for player in sorted_players
        }

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
    print(players.get_ranked_players())

