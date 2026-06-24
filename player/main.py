import random

class Player:

    def __init__(self, name, rounds_won=0):
        self.name = name
        self.rounds_won = rounds_won
        self.rank = float('inf')  # This will be set when players are ranked
        self.additional_attributes = {}  # Placeholder for any additional attributes, such as health, which only apply to certain game types.
    
    def __repr__(self):
        return f"{self.name}: won {self.rounds_won} rounds, ranked {self.rank}"
        
    def increment_rounds_won(self):
        self.rounds_won += 1

    def decrement_rounds_won(self):
        if self.rounds_won > 0:
            self.rounds_won -= 1
        else: 
            raise ValueError("Rounds won cannot be negative.")

    

class PlayerManager:
    """
    Accepts list of players as json list, creates corresponding Player objects, and manages them.
    Maintains a current player index.
    """
    
    def __init__(self, players_json):
        self.players = [Player(player['name'], player.get('rounds_won', 0)) for player in players_json]
        self.current_player_index = self.get_random_player_index

    def get_random_player_index(self):
        return random.randint(0, len(self.players) - 1)
    
    def get_current_player_object(self):
        return self.players[self.current_player_index()]

    def get_next_player_object(self):
        return self.players[(self.current_player_index + 1) % len(self.players)]

    def next_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def remove_player(self, player_name):
        self.players = [player for player in self.players if player.name != player_name] # assuming web app checks for unique player names
        if self.current_player_index >= len(self.players):
            self.current_player_index = random.randint(len(self.players) - 1)
    
    def get_ranked_players(self):
        '''
        Returns a list of players sorted by rounds won in descending order.
        '''
        sorted_players = sorted(self.players, key=lambda player: player.rounds_won, reverse=True)
        current_rank = 1
        previous_player_score = float('inf')  
        for player_index in range(len(sorted_players)):
            if sorted_players[player_index].rounds_won != previous_player_score:
                sorted_players[player_index].rank = current_rank
                previous_player_score = sorted_players[player_index].rounds_won
            else: 
                sorted_players[player_index].rank = current_rank - 1
            current_rank += 1
        return sorted_players

if __name__ == "__main__":
    example_players_json = [
        {"name": "Alice", "rounds_won": 12},
        {"name": "Bob", "rounds_won": 4},       
        {"name": "Charlie", "rounds_won": 12},
        {"name": "David", "rounds_won": 7},
        {"name": "Eve", "rounds_won": 0}
    ]

    players = PlayerManager(example_players_json)
    players.get_current_player_object().increment_rounds_won()
    
    print([player for player in players.players])
    for player in players.get_ranked_players():
        print(f"{player}")


