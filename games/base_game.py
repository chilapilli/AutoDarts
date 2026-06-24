from abc import ABC, abstractmethod

class BaseGame(ABC):

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def end(self):
        pass

    @abstractmethod
    def process_throw(self, score):
        pass

    @abstractmethod
    def check_win(self):
        pass

    @abstractmethod
    def get_display_state(self):
        pass
