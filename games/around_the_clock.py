

from .base_game import BaseGame, Score, INTERRUPT
from player.main import Player, PlayerManager
import logging, datetime


class AroundTheClockGame(BaseGame):
    
    def __init__(self, player_manager: PlayerManager,
                 end_on_any_part_of_bull_to_win: bool,
                 end_on_outer_and_then_inner_bull_to_win: bool,
                 is_solo_round: bool, # if set to False, the game will be played in a normal turn-based manner. If set to True, the game will be played in a solo run manner, where each player takes turns to complete the sequence as fast as possible.
                 only_count_doubles_as_hit: bool,
                 only_count_triples_as_hit: bool
                 ):
        
        super().__init__(player_manager)

        self.is_game_over = False
        self._winner = None
        self._end_called = False
        self._is_solo_round = is_solo_round
        self.player_manager = player_manager

        # Validate the game settings to ensure they are not contradictory
        if end_on_any_part_of_bull_to_win and end_on_outer_and_then_inner_bull_to_win:
            end_on_any_part_of_bull_to_win = False
            end_on_outer_and_then_inner_bull_to_win = True
            logging.debug("[Around the Clock]: Both end_on_any_part_of_bull_to_win and end_on_outer_and_then_inner_bull_to_win are set to True. Setting end_on_any_part_of_bull_to_win to False and end_on_outer_and_then_inner_bull_to_win to True.")

        if only_count_doubles_as_hit and only_count_triples_as_hit:
            only_count_doubles_as_hit = False
            only_count_triples_as_hit = True
            logging.debug("[Around the Clock]: Both only_count_doubles_as_hit and only_count_triples_as_hit are set to True. Setting only_count_doubles_as_hit to False and only_count_triples_as_hit to True.")

        self.end_on_any_part_of_bull_to_win = end_on_any_part_of_bull_to_win
        self.end_on_outer_and_then_inner_bull_to_win = end_on_outer_and_then_inner_bull_to_win
        self.only_count_doubles_as_hit = only_count_doubles_as_hit
        self.only_count_triples_as_hit = only_count_triples_as_hit

    
    def start(self):
        self._initialise_player_current_number()
        
        logging.info(f"""[Around the Clock]: Game settings:
                     - End on any part of bull to win: {self.end_on_any_part_of_bull_to_win}
                     - End on outer and then inner bull to win: {self.end_on_outer_and_then_inner_bull_to_win}
                     - Only count doubles as hit: {self.only_count_doubles_as_hit}
                     - Only count triples as hit: {self.only_count_triples_as_hit}
                     """)
        
        if self._is_solo_round:
            logging.info("[Around the Clock]: Starting solo run for all players.")
            self.complete_solo_run(end_on_any_part_of_bull_to_win=self.end_on_any_part_of_bull_to_win,
                                   end_on_outer_and_then_inner_bull_to_win=self.end_on_outer_and_then_inner_bull_to_win)
            
        else: 
            logging.info("[Around the Clock]: Starting turn-based run for all players.")
            self.turn_based_run(end_on_any_part_of_bull_to_win=self.end_on_any_part_of_bull_to_win,
                                end_on_outer_and_then_inner_bull_to_win=self.end_on_outer_and_then_inner_bull_to_win)


    def end(self):
        if self._end_called: 
            return
        self._end_called = True
        self.is_game_over = True
        
        logging.info("[Around the Clock]: Game terminated.")
        self._notify_game_end()

    def current_player_round(self, player: Player):
        """Round for 1 player in a turn-based game."""

        for i in range(3):
            logging.info(f"[Around the Clock]: {player.name}'s throw {i+1} of 3. Target number is {player.additional_attributes['around_the_clock_next_number']} {f'DOUBLE' if self.only_count_doubles_as_hit else ''} {f'TRIPLE' if self.only_count_triples_as_hit else ''} {f'ANY' if not self.only_count_doubles_as_hit and not self.only_count_triples_as_hit else ''}.")
            score = self._wait_for_throw()

            if score is INTERRUPT: 
                self.end()
                return 
            
            logging.info(f"[Around the Clock]: {player.name} threw {score.base_value} {f'DOUBLE' if score.is_double else ''} {f'TRIPLE' if score.is_triple else ''}, target is {player.additional_attributes['around_the_clock_next_number']} {f'DOUBLE' if self.only_count_doubles_as_hit else ''} {f'TRIPLE' if self.only_count_triples_as_hit else ''} {f'ANY' if not self.only_count_doubles_as_hit and not self.only_count_triples_as_hit else ''}.")
            if self._check_has_hit_next_target_number(player=player, 
                                                        score=score,
                                                        only_count_doubles_as_hit=self.only_count_doubles_as_hit,
                                                        only_count_triples_as_hit=self.only_count_triples_as_hit):
                
                self._increment_player_next_numbers(player=player, 
                                                    end_on_any_part_of_bull_to_win=self.end_on_any_part_of_bull_to_win,
                                                    end_on_outer_and_then_inner_bull_to_win=self.end_on_outer_and_then_inner_bull_to_win)
                
                player_current_number = player.additional_attributes["around_the_clock_current_number"]
                
                if player_current_number in [20, 25, 50]: # only check for win if the player has reached a winning number
                    self.is_game_over = self.check_finish_sequence(player=player,
                                                current_number=player_current_number, 
                                                end_on_any_part_of_bull_to_win=self.end_on_any_part_of_bull_to_win,
                                                end_on_outer_and_then_inner_bull_to_win=self.end_on_outer_and_then_inner_bull_to_win)
                
                    if self.is_game_over:
                        self.process_win(player=player, player_win_time_string=None)
                        self.end()
                        return

    def process_throw_score(self, score: Score):
        pass

    def check_win(self, player: Player):
        pass

    def check_finish_sequence(self, player: Player, 
                  current_number: int, 
                  end_on_any_part_of_bull_to_win: bool, 
                  end_on_outer_and_then_inner_bull_to_win: bool) -> bool:
        """
        Checks if the player has finished the sequence based on the game settings.
        """
        if (not end_on_any_part_of_bull_to_win) and (not end_on_outer_and_then_inner_bull_to_win) and (current_number == 20):
            logging.info(f"[Around the Clock]: Player {player.name} has finished the sequence on number {current_number}.")
            return True
        
        elif (end_on_any_part_of_bull_to_win) and current_number in [25, 50]:
            logging.info(f"[Around the Clock]: Player {player.name} has finished the sequence on number {current_number}.")
            return True

        elif (end_on_outer_and_then_inner_bull_to_win) and current_number == 50:
            logging.info(f"[Around the Clock]: Player {player.name} has finished the sequence on number {current_number}.")
            return True

        logging.info(f"[Around the Clock]: Player {player.name} has not finished the sequence on number {current_number}.")
        return False

    def process_win(self, player: Player, player_win_time_string: str = None):
        """Processes the win for the player, updating the game state and logging the win."""
        self.is_game_over = True 
        self._winner = player
        player.increment_rounds_won()
        logging.info(f"[Around the Clock]: Player {player.name} won {f"with time {player_win_time_string}" if player_win_time_string != None else ''}.")
    
    def get_display_state(self):
        """
        this returns a dictionary of the current game state, which can be used to display the current game state on a screen or other display device. The exact contents of the dictionary will depend on the specific game being played.
        """
        pass

    def turn_based_run(self, end_on_any_part_of_bull_to_win: bool, 
                       end_on_outer_and_then_inner_bull_to_win: bool):
        """Runs the game in a turn-based manner, where each player takes turns to throw until one player wins."""
        
        while not self.is_game_over:
            current_player = self.player_manager.get_current_player_object()
            logging.info(f"[Around the Clock]: {current_player.name}'s turn to throw.")

            self.current_player_round(player=current_player)
            if not self.is_game_over: 
                self.player_manager.next_player()

    def complete_solo_run(self, 
                          end_on_any_part_of_bull_to_win: bool, 
                          end_on_outer_and_then_inner_bull_to_win: bool
                          ):

        player_times = {} # dictionary with key as player object and value as time taken to complete the sequence

        while len(player_times.keys()) != len(self.player_manager.players): # ensures that all players have completed their solo run

            current_player = self.player_manager.get_current_player_object() 
            
            time_start = datetime.datetime.now()
            logging.info(f"[Around the Clock]: {current_player.name}'s turn to throw. Time started at {time_start.strftime('%Y-%m-%d %H:%M:%S')}.")

            self.player_solo_run(player=current_player,
                                 end_on_any_part_of_bull_to_win=end_on_any_part_of_bull_to_win,
                                 end_on_outer_and_then_inner_bull_to_win=end_on_outer_and_then_inner_bull_to_win,
                                 only_count_doubles_as_hit=self.only_count_doubles_as_hit,
                                 only_count_triples_as_hit=self.only_count_triples_as_hit)

            if self.is_game_over:
                return

            time_end = datetime.datetime.now()
            time_spent = time_end - time_start
            player_times[current_player] = time_spent
            logging.info(f"[Around the Clock]: {current_player.name}'s turn ended at {time_end.strftime('%Y-%m-%d %H:%M:%S')}, spent {self._format_timedelta(time_spent)} on their turn.")

            self.player_manager.next_player()

        logging.info(f"[Around the Clock]: All players have completed their turns.")
        winner_list = self.get_solo_run_winner_list(player_times=player_times) # there maybe ties, handle with list 
        for winner in winner_list:
            self.process_win(winner, player_win_time_string=self._format_timedelta(player_times[winner]))
        self.end()
    
    def get_solo_run_winner_list(self, player_times: dict) -> list[Player]:
      """Returns a list of players who have the best time in the solo run."""
      best_time = min(player_times.values())

      winner_list = [player for player, time_spent in player_times.items() if time_spent == best_time] 
      logging.info(f"[Around the Clock]: The winner(s) for the solo round are {', '.join([winner.name for winner in winner_list])}")

      return winner_list
            
    def player_solo_run(self, player: Player, 
                                only_count_doubles_as_hit: bool, 
                                only_count_triples_as_hit: bool,
                                end_on_any_part_of_bull_to_win: bool, 
                                end_on_outer_and_then_inner_bull_to_win: bool
                                ):
        """Runs a solo round for a single player, where the player throws until they complete the sequence or the game is interrupted."""

        logging.info(f"[Around the Clock]: {player.name} is starting their solo run.")

        has_completed_sequence = False
        while not has_completed_sequence:

            score = self._wait_for_throw()
            if score is INTERRUPT:
                self.end()
                return

            logging.info(f"[Around the Clock]: {player.name} threw {score.base_value} {f'DOUBLE' if score.is_double else ''} {f'TRIPLE' if score.is_triple else ''}, target is {player.additional_attributes["around_the_clock_next_number"]} {f"DOUBLE" if self.only_count_doubles_as_hit else ''} {f"TRIPLE" if self.only_count_triples_as_hit else ''}.")
            if self._check_has_hit_next_target_number(player = player,
                                                      score = score, 
                                                      only_count_doubles_as_hit = only_count_doubles_as_hit,
                                                      only_count_triples_as_hit = only_count_triples_as_hit):
                logging.info(f"[Around the Clock]: {player.name} hit the target number {player.additional_attributes["around_the_clock_next_number"]}.")

                self._increment_player_next_numbers(player=player,
                                                    end_on_any_part_of_bull_to_win=end_on_any_part_of_bull_to_win,
                                                    end_on_outer_and_then_inner_bull_to_win=end_on_outer_and_then_inner_bull_to_win)
                
                player_current_number = player.additional_attributes["around_the_clock_current_number"]
                logging.info(f"[Around the Clock]: {player.name}'s next target number is now {player.additional_attributes['around_the_clock_next_number']}.")

                if player_current_number in [20, 25, 50]: #winning numbers: 
                    has_completed_sequence = self.check_finish_sequence(player=player, current_number=player_current_number,
                                               end_on_any_part_of_bull_to_win=end_on_any_part_of_bull_to_win,
                                               end_on_outer_and_then_inner_bull_to_win=end_on_outer_and_then_inner_bull_to_win)

        logging.info(f"[Around the Clock]: {player.name} has finished the sequence.")

    def _check_has_hit_next_target_number(self,
                                          player: Player,
                                          score: Score,
                                          only_count_doubles_as_hit: bool,
                                          only_count_triples_as_hit) -> bool:
        """Checks if the player's throw has hit the next target number in the sequence, considering the game settings for doubles and triples."""
        target_number = player.additional_attributes["around_the_clock_next_number"]

        if only_count_doubles_as_hit and not score.is_double: 
            logging.info(f"[Around the Clock]: MISS - {player.name} threw {score.base_value} {f'DOUBLE' if score.is_double else ''} {f'TRIPLE' if score.is_triple else ''}, target is {target_number} DOUBLE. Only doubles count as hit.")
            return False
        
        if only_count_triples_as_hit and not score.is_triple: 
            logging.info(f"[Around the Clock]: MISS - {player.name} threw {score.base_value} {f'DOUBLE' if score.is_double else ''} {f'TRIPLE' if score.is_triple else ''}, target is {target_number} TRIPLE. Only triples count as hit.")
            return False
        
        if target_number != score.base_value:
            # A bull score (25/50) can only match if the target is also a bull; otherwise it's a miss.
            if not (score.base_value in [25, 50] and target_number in [25, 50]):
                logging.info(f"[Around the Clock]: MISS - {player.name} threw {score.base_value} {f'DOUBLE' if score.is_double else ''} {f'TRIPLE' if score.is_triple else ''}, target is {target_number}.")
                return False

        if (score.base_value == 25 or score.base_value == 50) and self.end_on_any_part_of_bull_to_win:
            logging.info(f"[Around the Clock]: HIT - {player.name} threw {score.base_value} {f'DOUBLE' if score.is_double else ''} {f'TRIPLE' if score.is_triple else ''}, target is {target_number} .")
            return True
        
        if (score.base_value == 25 or score.base_value == 50) and self.end_on_outer_and_then_inner_bull_to_win:
            if target_number == 25 and score.base_value == 25:
                logging.info(f"[Around the Clock]: HIT - {player.name} threw {score.base_value} {f'DOUBLE' if score.is_double else ''} {f'TRIPLE' if score.is_triple else ''}, target is {target_number}.")
                return True
            elif target_number == 50 and score.base_value == 50:
                logging.info(f"[Around the Clock]: HIT - {player.name} threw {score.base_value} {f'DOUBLE' if score.is_double else ''} {f'TRIPLE' if score.is_triple else ''}, target is {target_number}.")
                return True
            else:
                logging.info(f"[Around the Clock]: MISS - {player.name} threw {score.base_value} {f'DOUBLE' if score.is_double else ''} {f'TRIPLE' if score.is_triple else ''}, target is {target_number}.")
                return False

        logging.info(f"[Around the Clock]: HIT - {player.name} threw {score.base_value} {f'DOUBLE' if score.is_double else ''} {f'TRIPLE' if score.is_triple else ''}, target is {target_number}.") 
        return True     
        
    def _increment_player_next_numbers(self,
                                       player: Player,
                                       end_on_any_part_of_bull_to_win: bool,
                                       end_on_outer_and_then_inner_bull_to_win: bool):
        """Increments the player's current and next target numbers in the Around the Clock sequence based on the game settings."""
        existing_next_number = player.additional_attributes["around_the_clock_next_number"]
        next_number = existing_next_number

        current_number = existing_next_number

        if existing_next_number not in [20, 25, 50]: next_number = existing_next_number + 1
        elif end_on_any_part_of_bull_to_win: next_number = 25 # use check for score >= 25 to determine win later 
        elif end_on_outer_and_then_inner_bull_to_win: # need to first get 25, then 50

            if existing_next_number == 20: next_number = 25
            else: next_number = 50 

        player.additional_attributes["around_the_clock_current_number"] = current_number
        player.additional_attributes["around_the_clock_next_number"] = next_number
        
    def _format_timedelta(self, td: datetime.timedelta) -> str:
        """Format a timedelta as MM:SS.mmm."""
        total = td.total_seconds()
        return f"{int(total // 60):02d}:{int(total % 60):02d}.{td.microseconds // 1000:03d}"

    def _initialise_player_current_number(self):
        """Initialise the current and next target numbers for each player in the Around the Clock game."""
        
        for player in self.player_manager.players:
            player.additional_attributes["around_the_clock_current_number"] = 0
            player.additional_attributes["around_the_clock_next_number"] = 1
