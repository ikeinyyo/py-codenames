from abc import ABC, abstractmethod


class BotBase(ABC):
    def __init__(self, is_captain=False, language="es"):
        self._board = None
        self.is_captain = is_captain
        self.is_red = None
        self.language = language

    def set_board(self, board):
        self._board = board

    def set_blue_team(self):
        self.is_red = False

    def set_red_team(self):
        self.is_red = True

    @abstractmethod
    def give_clue(self):
        pass

    @abstractmethod
    def give_answer(self, clue):
        pass
