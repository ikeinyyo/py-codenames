from abc import ABC, abstractmethod


class BotBase(ABC):
    def __init__(self):
        self._board = None

    def set_board(self, board):
        self._board = board

    @abstractmethod
    def give_clue(self, is_red_turn):
        pass

    @abstractmethod
    def give_answer(self, is_red_turn):
        pass
