import random
import games
import player
import threading
import time
from games.base_game import Score
import logging


def initiate_logging():
    """Sets up logging configuration for the application."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info(f'Game session started at {time.strftime("%Y-%m-%d %H:%M:%S")}')

def end_logging():
    """Logs the end of the game session."""
    logging.info(f'Game session ended at {time.strftime("%Y-%m-%d %H:%M:%S")}')

def parse_score(user_input: str) -> Score | None:
    """Parse a user-typed throw into a Score object.

    Accepted formats (case-insensitive):
        20      single 20
        d20     double 20
        t20     triple 20
        25      outer bull
        50      inner bull
        0       miss

    Returns None if the input cannot be parsed.
    """
    s = user_input.strip().lower()
    try:
        if s.startswith('d'):
            return Score(base_value=int(s[1:]), is_double=True)
        elif s.startswith('t'):
            return Score(base_value=int(s[1:]), is_triple=True)
        else:
            return Score(base_value=int(s))
    except (ValueError, IndexError):
        return None


def interactive_camera(game):
    """Read throw scores from stdin and feed them into the game's throw queue.

    Blocks on input() until the user types a score or 'q' to quit.
    The game loop runs in the main thread; this function runs in a background thread.
    """
    print("Enter throws (e.g. 20, d20, t20, 25, 50, 0). Type 'q' to quit.")
    while not game.is_game_over:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            game.receive_interrupt()
            return

        if raw.lower() in ('q', 'quit'):
            game.receive_interrupt()
            return

        score = parse_score(raw)
        if score is None:
            print(f"  Unrecognised input '{raw}'. Try: 20  d20  t20  25  50  0  q")
            continue

        game.receive_throw(score)


def simulate_camera(game, throws, send_interrupt=False):
    """Simulates a camera sending throw scores with a short delay between each.

    Args:
        send_interrupt: If True, sends an INTERRUPT after all throws to force-end the game.
    """
    for throw in throws:
        time.sleep(random.uniform(0.001, 0.05))  # Simulate time taken for a throw to be detected
        logging.info(f"[camera] detected throw: {throw}")
        game.receive_throw(throw)
    if send_interrupt:
        time.sleep(1)
        logging.info("[camera] sending interrupt signal.")
        game.receive_interrupt()



# ------------------------------------------------------------------
# X01 Game Simulation Example
# ------------------------------------------------------------------

if __name__ == "__main__":

    initiate_logging()

    example_players = [
        {"name": "Ashley", "rounds_won": 0},
        {"name": "Matthew", "rounds_won": 0},
    ]

    session_player_manager = player.PlayerManager(example_players)

    starting_score = 201
    x01_game_session = games.X01Game(starting_score=starting_score, 
                                     playerManager=session_player_manager, 
                                     ends_on_double_to_win=False)

    fake_throws = [
        Score(base_value=20, is_double=False, is_triple=True),
        Score(base_value=8, is_double=True, is_triple=False),
        Score(base_value=10, is_double=False, is_triple=True), # 106 

        Score(base_value=5, is_double=False, is_triple=False),
        Score(base_value=25, is_double=True, is_triple=False),  
        Score(base_value=20, is_double=False, is_triple=False), # 75  

        Score(base_value=12, is_double=False, is_triple=True),
        Score(base_value=50, is_double=False, is_triple=False),
        Score(base_value=9, is_double=False, is_triple=False), # wins here

        # Score(base_value=0, is_double=False, is_triple=True),
        # Score(base_value=0, is_double=False, is_triple=True),
        # Score(base_value=0, is_double=False, is_triple=True),

        # Score(base_value=9, is_double=False, is_triple=True),
        # Score(base_value=10, is_double=False, is_triple=True),
        # Score(base_value=10, is_double=False, is_triple=True),

    ]

    # camera runs in a background thread, game loop blocks on _wait_for_throw()
    # send_interrupt=True sends INTERRUPT via receive_interrupt() after all throws
    # camera_thread = threading.Thread(target=simulate_camera, 
    #                                  args=(x01_game_session, fake_throws), 
    #                                  kwargs={"send_interrupt": False})
    
    camera_thread = threading.Thread(
        target=interactive_camera,
        args=(x01_game_session,),
        daemon=True,
    )
    camera_thread.start()

    x01_game_session.start()

    camera_thread.join() # this waits for the whole camera thread to finish before ending

    print(session_player_manager)

    end_logging()


# ------------------------------------------------------------------
# Killer Game Simulation
# ------------------------------------------------------------------
# Setup: 3 players, 3 shields each, no doubles required for anything.
# Designation: each player throws once to claim a number (1–20).
# Becoming killer: hit your own number 3 times.
# Eliminating: as killer, hit another player's number until their shields reach 0.
# NOTE: starting player is random — check the log to see who got which number.
# ------------------------------------------------------------------

# if __name__ == "__main__":

#     initiate_logging()

#     example_players = [
#         {"name": "Alice", "rounds_won": 4},
#         {"name": "Bob", "rounds_won": 2},
#         {"name": "Charlie", "rounds_won": 0},
#     ]

#     session_player_manager = player.PlayerManager(example_players)
#     killer_game_session = games.KillerGame(
#         playerManager=session_player_manager,
#         requires_hitting_double_to_be_a_killer=False,   # any hit on own number counts
#         requires_hitting_double_to_remove_shield=False,  # any hit removes a shield
#         shields_per_player=3,
#         allow_recovery_of_shields=False,
#     )

#     fake_throws = [
#         # ── Designation phase: each player claims a number ──────────────────
#         Score(base_value=7),   # 1st player → number 7

#         Score(base_value=50),  # not a valid number, rethrow
#         Score(base_value=3),   # 2rd player → number 3

#         Score(base_value=7),   # not a valid number, rethrow
#         Score(base_value=3),  #  not a valid number, rethrow
#         Score(base_value=18),   # 3rd player → number 18 

#         # ── Round 1 ─────────────────────────────────────────────────────────
        
#         Score(base_value= 0),               
#         Score(base_value= 7),             # hit
#         Score(base_value= 8),           

#         Score(base_value= 3),             # hit  
#         Score(base_value= 3),             # hit  
#         Score(base_value= 8),             # hits someone else, shouldnt count 

#         Score(base_value= 18),            # hit  
#         Score(base_value= 18),            # hit   
#         Score(base_value= 18),            # hit, becomes killer

#         # ── Round 2 ─────────────────────────────────────────────────────────

#         Score(base_value= 7),             # hit 
#         Score(base_value= 7),             # hit, becomes killer
#         Score(base_value= 7),             # takes his own shield

#         Score(base_value= 3),             # hit, becomes killer 
#         Score(base_value= 1),               
#         Score(base_value= 9),             

#         Score(base_value= 3),            # hits plater 2, counts               
#         Score(base_value= 3),            # hits plater 2, counts     
#         Score(base_value= 5),            # invalid number 

#         # ── Round 3 ─────────────────────────────────────────────────────────

#         # player 1
#         Score(base_value= 7),           # hits his own number, takes his own shield
#         Score(base_value= 7),           # hits his own number, takes his own shield, eliminated             
        
#         # player 2
#         Score(base_value= 18),           
#         Score(base_value= 18),          
#         Score(base_value= 18)          # player 2 eliminates player 3
#     ]

#     camera_thread = threading.Thread(
#         target=simulate_camera,
#         args=(killer_game_session, fake_throws),
#         kwargs={"send_interrupt": False},
#     )
#     camera_thread.start()

#     killer_game_session.start()
#     camera_thread.join()

#     print(session_player_manager)

#     end_logging()


# ------------------------------------------------------------------
# Fifty-One by Five Game Simulation
# ------------------------------------------------------------------

# if __name__ == "__main__":

#     initiate_logging()

#     example_players = [
#         {"name": "Alice", "rounds_won": 0},
#         {"name": "Bob", "rounds_won": 3},
#         {"name": "Charlie", "rounds_won": 1},
#         {"name": "David", "rounds_won": 2}
#     ]

#     session_player_manager = player.PlayerManager(example_players)


#     fifty_one_game_session = games.FiftyOneByFive(playerManager=session_player_manager)

#     fake_throws = [
#         # ---------- Round 1 ----------
#         # P1: 45 -> +9 (9)
#         Score(base_value=20, is_double=False, is_triple=False),
#         Score(base_value=20, is_double=False, is_triple=False),
#         Score(base_value=5,  is_double=False, is_triple=False),

#         # P2: 60 -> +12 (12)
#         Score(base_value=20, is_double=True, is_triple=False),
#         Score(base_value=20, is_double=False, is_triple=False),
#         Score(base_value=0,  is_double=False, is_triple=False),

#         # P3: 46 -> not divisible by 5 (0)
#         Score(base_value=20, is_double=False, is_triple=False),
#         Score(base_value=20, is_double=False, is_triple=False),
#         Score(base_value=6,  is_double=False, is_triple=False),

#         # P4: 50 -> +10 (10)
#         Score(base_value=20, is_double=False, is_triple=False),
#         Score(base_value=20, is_double=False, is_triple=False),
#         Score(base_value=10, is_double=False, is_triple=False),

#         # ---------- Round 2 ----------
#         # P1: 60 -> +12 (21)
#         Score(base_value=20, is_double=True, is_triple=False),
#         Score(base_value=20, is_double=False, is_triple=False),
#         Score(base_value=0,  is_double=False, is_triple=False),

#         # P2: 60 -> +12 (24)
#         Score(base_value=20, is_double=True, is_triple=False),
#         Score(base_value=20, is_double=False, is_triple=False),
#         Score(base_value=0,  is_double=False, is_triple=False),

#         # P3: 45 -> +9 (9)
#         Score(base_value=20, is_double=False, is_triple=False),
#         Score(base_value=20, is_double=False, is_triple=False),
#         Score(base_value=5,  is_double=False, is_triple=False),

#         # P4: 47 -> not divisible by 5 (10)
#         Score(base_value=20, is_double=False, is_triple=False),
#         Score(base_value=20, is_double=False, is_triple=False),
#         Score(base_value=7,  is_double=False, is_triple=False),

#         # ---------- Round 3 ----------
#         # P1: 60 -> +12 (33)
#         Score(base_value=20, is_double=True, is_triple=False),
#         Score(base_value=20, is_double=False, is_triple=False),
#         Score(base_value=0,  is_double=False, is_triple=False),

#         # P2: 60 -> +12 (36)
#         Score(base_value=20, is_double=True, is_triple=False),
#         Score(base_value=20, is_double=False, is_triple=False),
#         Score(base_value=0,  is_double=False, is_triple=False),

#         # P3: 60 -> +12 (21)
#         Score(base_value=20, is_double=True, is_triple=False),
#         Score(base_value=20, is_double=False, is_triple=False),
#         Score(base_value=0,  is_double=False, is_triple=False),

#         # P4: 60 -> +12 (22)
#         Score(base_value=20, is_double=True, is_triple=False),
#         Score(base_value=20, is_double=False, is_triple=False),
#         Score(base_value=0,  is_double=False, is_triple=False),

#         # ---------- Round 4 ----------
#         # P1: 60 -> +12 (45)
#         Score(base_value=20, is_double=True, is_triple=False),
#         Score(base_value=20, is_double=False, is_triple=False),
#         Score(base_value=0,  is_double=False, is_triple=False),

#         # P2: 60 -> +12 (48)
#         Score(base_value=20, is_double=True, is_triple=False),
#         Score(base_value=20, is_double=False, is_triple=False),
#         Score(base_value=0,  is_double=False, is_triple=False),

#         # P3: 55 -> +11 (32)
#         Score(base_value=20, is_double=False, is_triple=False),
#         Score(base_value=20, is_double=False, is_triple=False),
#         Score(base_value=15, is_double=False, is_triple=False),

#         # P4: 46 -> not divisible by 5 (22)
#         Score(base_value=20, is_double=False, is_triple=False),
#         Score(base_value=20, is_double=False, is_triple=False),
#         Score(base_value=6,  is_double=False, is_triple=False),

#         # ---------- Round 5 ----------
#         # P1: 40 -> +8 => would reach 53 -> BUST (stays 45)
#         Score(base_value=20, is_double=False, is_triple=False),
#         Score(base_value=20, is_double=False, is_triple=False),
#         Score(base_value=0,  is_double=False, is_triple=False),

#         # P2: 15 -> +3 (51) WIN
#         Score(base_value=5,  is_double=False, is_triple=False),
#         Score(base_value=5,  is_double=False, is_triple=False),
#         Score(base_value=5,  is_double=False, is_triple=False),
#     ]

#     camera_thread = threading.Thread(
#         target=simulate_camera,
#         args=(fifty_one_game_session, fake_throws),
#         kwargs={"send_interrupt": False},
#     )
#     camera_thread.start()

#     fifty_one_game_session.start()
#     camera_thread.join()

#     print(session_player_manager)

#     end_logging()


# ------------------------------------------------------------------
# Around the Clock Game Simulation (Time Based)
# ------------------------------------------------------------------

# if __name__ == "__main__":

#     initiate_logging()

#     example_players = [
#         {"name": "Ashley", "rounds_won": 3},
#         {"name": "Matthew", "rounds_won": 1},
#     ]

#     session_player_manager = player.PlayerManager(example_players)
#     around_the_clock_game_session = games.AroundTheClockGame(player_manager=session_player_manager,
#                                                              end_on_any_part_of_bull_to_win=False,
#                                                              end_on_outer_and_then_inner_bull_to_win=False,
#                                                              is_solo_round=False,
#                                                              only_count_doubles_as_hit=False,
#                                                              only_count_triples_as_hit=False)

#     fake_throws = [
#         Score(base_value=1, is_double=True), Score(base_value=2, is_double=True), Score(base_value=3, is_double=True), 
#         Score(base_value=4, is_double=True), Score(base_value=5, is_double=True), Score(base_value=6, is_double=True), 
#         Score(base_value=7, is_double=True), Score(base_value=8, is_double=True), Score(base_value=9, is_double=True),
#         Score(base_value=10, is_double=True), Score(base_value=11, is_double=True), Score(base_value=12, is_double=True),
#         Score(base_value=13, is_double=True), Score(base_value=14, is_double=True), Score(base_value=15, is_double=True),
#         Score(base_value=16, is_double=True), Score(base_value=17, is_double=True), Score(base_value=18, is_double=True),
#         Score(base_value=19, is_double=True), Score(base_value=20, is_double=True),  # hit double 20 to win
        
#         Score(base_value=1, is_double=True), Score(base_value=2, is_double=True), Score(base_value=3, is_double=True), 
#         Score(base_value=4, is_double=True), Score(base_value=5, is_double=True), Score(base_value=6, is_double=True), 
#         Score(base_value=7, is_double=True), Score(base_value=8, is_double=True), Score(base_value=9, is_double=True),
#         Score(base_value=10, is_double=True), Score(base_value=11, is_double=True), Score(base_value=12, is_double=True),
#         Score(base_value=13, is_double=True), Score(base_value=14, is_double=True), Score(base_value=15, is_double=True),
#         Score(base_value=16, is_double=True), Score(base_value=17, is_double=True), Score(base_value=18, is_double=True),
#         Score(base_value=19, is_double=True), Score(base_value=19, is_double=True), Score(base_value=20, is_double=False),
#         Score(base_value=20, is_double=True),  # hit double 20 to win
        
#     ]

#     # camera_thread = threading.Thread(
#     #     target=simulate_camera,
#     #     args=(around_the_clock_game_session, fake_throws),
#     #     kwargs={"send_interrupt": False},
#     # )
#     camera_thread = threading.Thread(
#         target=interactive_camera,
#         args=(around_the_clock_game_session,),
#         daemon=True,
#     )
#     camera_thread.start()

#     around_the_clock_game_session.start()
#     camera_thread.join()

#     print(session_player_manager)

#     end_logging()


# -------------------------------------------------------------------
# Around the Clock Game Simulation (Turn Based)
# -------------------------------------------------------------------

# if __name__ == "__main__":

#     initiate_logging()

#     example_players = [
#         {"name": "Ashley", "rounds_won": 1},
#         {"name": "Matthew", "rounds_won": 0},
#     ]

#     session_player_manager = player.PlayerManager(example_players)
#     around_the_clock_game_session = games.AroundTheClockGame(player_manager=session_player_manager,
#                                                              end_on_any_part_of_bull_to_win=False,
#                                                              end_on_outer_and_then_inner_bull_to_win=True,
#                                                              is_solo_round=False,
#                                                              only_count_doubles_as_hit=False,
#                                                              only_count_triples_as_hit=False,
#                                                              custom_end_of_sequence_number=19)

#     fake_throws = [
        
#         # p1 
#         Score(base_value=1, is_double=True), Score(base_value=2, is_double=True), Score(base_value=3, is_double=True), 
#         # p2
#         Score(base_value=1, is_double=True), Score(base_value=2, is_double=True), Score(base_value=3, is_double=True), 

#         # p1
#         Score(base_value=4, is_double=True), Score(base_value=5, is_double=True), Score(base_value=6, is_double=True), 
#         # p2
#         Score(base_value=4, is_double=True), Score(base_value=5, is_double=True), Score(base_value=6, is_double=True),          

#         #p1
#         Score(base_value=7, is_double=True), Score(base_value=8, is_double=True), Score(base_value=9, is_double=True),
#         #p2
#         Score(base_value=7, is_double=True), Score(base_value=8, is_double=True), Score(base_value=9, is_double=True),

#         #p1
#         Score(base_value=10, is_double=True), Score(base_value=11, is_double=True), Score(base_value=12, is_double=True),
#         #p2
#         Score(base_value=10, is_double=True), Score(base_value=11, is_double    =True), Score(base_value=12, is_double=True),

#         #p1
#         Score(base_value=13, is_double=True), Score(base_value=14, is_double=True), Score(base_value=15, is_double=True),
#         #p2
#         Score(base_value=13, is_double=True), Score(base_value=14, is_double=True), Score(base_value=15, is_double=True),

#         #p1
#         Score(base_value=16, is_double=True), Score(base_value=17, is_double=True), Score(base_value=18, is_double=True),
#         #p2
#         Score(base_value=16, is_double=True), Score(base_value=17, is_double=True), Score(base_value=18, is_double=True),

#         #p1
#         Score(base_value=19, is_double=True), Score(base_value=20, is_double=False), Score(base_value=15, is_double=True),  # hit double 20 to win
#         #p2
#         Score(base_value=19, is_double=True), Score(base_value=20, is_double=True), Score(base_value=25, is_double=False),  # hit double 20 to win

#         #p1
#         Score(base_value=25, is_double=False), Score(base_value=20, is_double=False), Score(base_value=20, is_double=True),  # hit double 20 to win
#         #p2
#         Score(base_value=25, is_double=False), Score(base_value=50, is_double=False)  # hit double 20 to win
#     ]

#     camera_thread = threading.Thread(
#         target=simulate_camera,
#         args=(around_the_clock_game_session, fake_throws),
#         kwargs={"send_interrupt": False},
#     )
#     camera_thread.start()

#     around_the_clock_game_session.start()
#     camera_thread.join()

#     print(session_player_manager)

#     end_logging()


# --------------------------------------------------------------------
# High-Low Game Simulation
# --------------------------------------------------------------------

# if __name__ == "__main__":
    
#     initiate_logging()

#     example_players = [
#         {"name": "Matthew", "rounds_won": 0},
#         {"name": "Ashley", "rounds_won": 0}
#     ]

#     session_player_manager = player.PlayerManager(example_players)
#     high_low_game_session = games.HighLowGame(player_manager=session_player_manager,
#                                               high_only=True,  # alternates between high and low rounds
#                                               total_lives=3)    # each player has 3 lives

#     camera_thread = threading.Thread(
#         target=interactive_camera,
#         args=(high_low_game_session,),
#         daemon=True,
#     )
#     camera_thread.start()

#     high_low_game_session.start()

#     # Game is over — if the input thread is still blocking on input(), prompt the user to exit.
#     if camera_thread.is_alive():
#         print("\nGame over! Press Enter to exit.")
#     camera_thread.join()

#     print(session_player_manager)

#     end_logging()
