

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
        self._is_solo_round = is_solo_round
        self.is_game_over = False
        self._winner = None
        self.player_manager = player_manager
        self._end_called = False

        self.end_on_any_part_of_bull_to_win = end_on_any_part_of_bull_to_win
        self.end_on_outer_and_then_inner_bull_to_win = end_on_outer_and_then_inner_bull_to_win
        self.only_count_doubles_as_hit = only_count_doubles_as_hit
        self.only_count_triples_as_hit = only_count_triples_as_hit
    
    def start(self):
        self._initialise_player_current_number()
        if self._is_solo_round:
            self.complete_solo_run(end_on_any_part_of_bull_to_win=self.end_on_any_part_of_bull_to_win,
                                   end_on_outer_and_then_inner_bull_to_win=self.end_on_outer_and_then_inner_bull_to_win)

    def end(self):
        if self._end_called:
            return
        self._end_called = True
        self.is_game_over = True
        logging.info("[Around the Clock]: Game terminated.")
        self._notify_game_end()

    def current_player_round(self, player: Player):
        pass

    def process_throw_score(self, score: Score):
        pass

    def check_win(self, player: Player):
        pass

    def check_finish_sequence(self, player: Player, 
                  current_number: int, 
                  end_on_any_part_of_bull_to_win: bool, 
                  end_on_outer_and_then_inner_bull_to_win: bool) -> bool:
        logging.info(f"[Around the Clock]: Checking if player {player.name} has finished the sequence on number {current_number}.")
        
        if (not end_on_any_part_of_bull_to_win) and (not end_on_outer_and_then_inner_bull_to_win) and (current_number == 20):
            return True
        
        elif (end_on_any_part_of_bull_to_win) and current_number in [25, 50]:
            return True

        elif (end_on_outer_and_then_inner_bull_to_win) and current_number == 50:
            return True

        logging.info(f"[Around the Clock]: Player {player.name} has not finished the sequence on number {current_number}.")
        return False

    def process_win(self, player: Player, player_win_time_string: str = None):
            self.is_game_over = True 
            self._winner = player
            player.increment_rounds_won()
            logging.info(f"[Around the Clock]: Player {player.name} won with time {player_win_time_string}.")
        
    def get_display_state(self):
        """
        this returns a dictionary of the current game state, which can be used to display the current game state on a screen or other display device. The exact contents of the dictionary will depend on the specific game being played.
        """
        pass

    def complete_solo_run(self, 
                          end_on_any_part_of_bull_to_win: bool, 
                          end_on_outer_and_then_inner_bull_to_win: bool
                          ):
        
        logging.info("[Around the Clock]: Starting solo run for all players.")
        logging.info(f"""[Around the Clock]: Game settings:
                     - End on any part of bull to win: {end_on_any_part_of_bull_to_win}
                     - End on outer and then inner bull to win: {end_on_outer_and_then_inner_bull_to_win}
                     - Only count doubles as hit: {self.only_count_doubles_as_hit}
                     - Only count triples as hit: {self.only_count_triples_as_hit}
                     """)
        

        player_times = {}

        while len(player_times.keys()) != len(self.player_manager.players):

            current_player = self.player_manager.get_current_player_object()
            
            time_start = datetime.datetime.now()
            logging.info(f"[Around the Clock]: {current_player.name}'s turn to throw. Time started at {time_start.strftime('%Y-%m-%d %H:%M:%S')}.")

            self.player_solo_run(player=current_player,
                                 end_on_any_part_of_bull_to_win=end_on_any_part_of_bull_to_win,
                                 end_on_outer_and_then_inner_bull_to_win=end_on_outer_and_then_inner_bull_to_win,
                                 only_count_doubles_as_hit=self.only_count_doubles_as_hit,
                                 only_count_triples_as_hit=self.only_count_triples_as_hit)
            time_end = datetime.datetime.now()
            logging.info(f"[Around the Clock]: {current_player.name}'s turn ended at {time_end.strftime('%Y-%m-%d %H:%M:%S')}.")

            time_spent = time_end - time_start
            logging.info(f"[Around the Clock]: {current_player.name} spent {f"{int(time_spent.total_seconds() // 60):02d}:{int(time_spent.total_seconds() % 60):02d}.{time_spent.microseconds // 1000:03d}"} on their turn.")
            
            player_times[current_player] = time_spent
            self.player_manager.next_player()

        logging.info(f"[Around the Clock]: All players have completed their turns.")

        winner_list = self.get_solo_run_winner_list(player_times=player_times)
        for winner in winner_list:
            winner_time_spent = player_times[winner]
            self.process_win(winner, player_win_time_string=f"{int(winner_time_spent.total_seconds() // 60):02d}:{int(winner_time_spent.total_seconds() % 60):02d}.{winner_time_spent.microseconds // 1000:03d}")
    
    def get_solo_run_winner_list(self, player_times: dict) -> list[Player]:
      best_time = min(player_times.values())

      winner_list = [
        player for player, time_spent in player_times.items() if time_spent == best_time
      ]
      logging.info(f"[Around the Clock]: The winner(s) for the solo round are {', '.join([winner.name for winner in winner_list])}")

      return winner_list
            
    def player_solo_run(self, player: Player, 
                                only_count_doubles_as_hit: bool, 
                                only_count_triples_as_hit: bool,
                                end_on_any_part_of_bull_to_win: bool, 
                                end_on_outer_and_then_inner_bull_to_win: bool
                                ):
    

        logging.info(f"[Around the Clock]: {player.name} is starting their solo run.")

        has_completed_sequence = False
        while not has_completed_sequence:

            score = self._wait_for_throw()

            if score is INTERRUPT:
                self.end()
                return

            logging.info(f"[Around the Clock]: {player.name} threw {score.total}, target is {player.additional_attributes["around_the_clock_next_number"]}.")

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

        target_number = player.additional_attributes["around_the_clock_next_number"]

        if only_count_doubles_as_hit and not score.is_double: return False
        if only_count_triples_as_hit and not score.is_triple: return False
        if target_number != score.base_value: return False
        return True 
        
    def _increment_player_next_numbers(self,
                                       player: Player,
                                       end_on_any_part_of_bull_to_win: bool,
                                       end_on_outer_and_then_inner_bull_to_win: bool):

        existing_next_number = player.additional_attributes["around_the_clock_next_number"]
        next_number = existing_next_number

        current_number = existing_next_number

        if existing_next_number!= 20: 
            next_number = existing_next_number + 1

        elif end_on_any_part_of_bull_to_win:
            next_number = 25 # use check for score >= 25 to determine win later 
        
        elif end_on_outer_and_then_inner_bull_to_win: # need to first get 25, then 50

            if existing_next_number == 20: 
                next_number = 25

            else:
                next_number = 50 
        

        player.additional_attributes["around_the_clock_current_number"] = current_number
        player.additional_attributes["around_the_clock_next_number"] = next_number
        
    def _initialise_player_current_number(self):

        for player in self.player_manager.players:
            player.additional_attributes["around_the_clock_current_number"] = 0
            player.additional_attributes["around_the_clock_next_number"] = 1
