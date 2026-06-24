from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Optional
import queue

from player.main import PlayerManager, Player


@dataclass
class Score:
    """Represents a single dart throw.

    Attributes:
        base_value: The raw number hit on the board (1–20, or 25 for bull).
        is_double: True if the dart landed in the double ring.
        is_triple: True if the dart landed in the triple ring.
    """
    base_value: int
    is_double: bool = False
    is_triple: bool = False

    def __post_init__(self):
        """Validate that a throw cannot be both double and triple."""
        if self.is_double and self.is_triple:
            raise ValueError("A throw cannot be both double and triple.")

    @property
    def total(self) -> int:
        """Total score for this throw after applying multiplier."""
        if self.is_triple:
            return self.base_value * 3
        if self.is_double:
            return self.base_value * 2
        return self.base_value



CAMERA_INTERRUPT = object()
"""Sentinel pushed onto the throw queue to signal an abrupt end to the game."""


class BaseGame(ABC):
    """Abstract base class for all dart games."""

    def __init__(self, player_manager: PlayerManager, on_game_end: Optional[Callable] = None):
        self.player_manager = player_manager
        self._throw_queue: queue.Queue = queue.Queue()
        self._on_game_end = on_game_end

    def _flush_throw_queue(self):
        """Discard all pending items in the throw queue.

        Called when the game ends so any throws the camera already detected
        but the game loop hasn't processed yet are cleared out.
        """
        while not self._throw_queue.empty():
            try:
                self._throw_queue.get_nowait()
            except queue.Empty:
                break

    def _notify_game_end(self):
        """Flush the throw queue and call the on_game_end callback."""
        self._flush_throw_queue()
        if self._on_game_end:
            self._on_game_end()

    def receive_throw(self, score: Score):
        """Called by the camera system when a throw is detected.

        Args:
            score: The detected throw as a Score object.
        """
        self._throw_queue.put(score)

    def receive_interrupt(self):
        """Called by the camera system to abruptly end the game.

        Pushes CAMERA_INTERRUPT onto the queue. The game loop detects it
        and calls end().
        """
        self._throw_queue.put(CAMERA_INTERRUPT)

    def _wait_for_throw(self):
        """Block until a Score or CAMERA_INTERRUPT is received from the camera.

        Returns:
            A Score object, or CAMERA_INTERRUPT if the camera sent a stop signal.
        """
        return self._throw_queue.get()

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def end(self):
        pass

    @abstractmethod
    def current_player_round(self, player: Player):
        pass

    @abstractmethod
    def process_throw_score(self, score: Score):
        pass

    @abstractmethod
    def check_win(self):
        pass

    @abstractmethod
    def get_display_state(self):
        pass

