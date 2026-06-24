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

def simulate_camera(game, throws, send_interrupt=False):
    """Simulates a camera sending throw scores with a short delay between each.

    Args:
        send_interrupt: If True, sends a CAMERA_INTERRUPT after all throws to force-end the game.
    """
    for throw in throws:
        time.sleep(1)
        logging.info(f"[camera] detected throw: {throw}")
        game.receive_throw(throw)
    if send_interrupt:
        time.sleep(1)
        logging.info("[camera] sending interrupt signal.")
        game.receive_interrupt()


if __name__ == "__main__":

    initiate_logging()

    example_players = [
        {"name": "Alice", "rounds_won": 12},
        {"name": "Bob", "rounds_won": 4},
        {"name": "Charlie", "rounds_won": 12}
        # {"name": "David", "rounds_won": 7},
        # {"name": "Eve", "rounds_won": 4}
    ]

    session_player_manager = player.PlayerManager(example_players)

    starting_score = 80
    x01_game_session = games.X01Game(starting_score=starting_score, 
                                     playerManager=session_player_manager, 
                                     ends_on_double_to_win=False)

    fake_throws = [
        Score(20, is_triple=True),  
        Score(19, is_triple=True),  
        Score(10, is_double=True),  
        Score(15),                  
        Score(10, is_double=True),  
        Score(25),                  
        Score(20, is_double=True),  
    ]

    # camera runs in a background thread, game loop blocks on _wait_for_throw()
    # send_interrupt=True sends CAMERA_INTERRUPT via receive_interrupt() after all throws
    camera_thread = threading.Thread(target=simulate_camera, args=(x01_game_session, fake_throws), kwargs={"send_interrupt": True})
    camera_thread.start()

    x01_game_session.start()

    camera_thread.join()

    end_logging()