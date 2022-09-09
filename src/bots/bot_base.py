from abc import ABC, abstractmethod
from dataclasses import dataclass

from codenames.helpers.board import Board


@dataclass
class BotBase(ABC):
    _board: object = None
    is_captain: bool = False
    is_team_member: bool = False
    is_red: bool = False
    language: str = None

    def __init__(self, is_captain=False, is_team_member=False, language="es"):
        self._board = None
        self.is_captain = is_captain
        self.is_team_member = is_team_member
        self.is_red = None
        self.language = language

    def set_board(self, board: Board) -> None:
        self._board = board

    def set_blue_team(self) -> None:
        self.is_red = False

    def set_red_team(self) -> None:
        self.is_red = True

    @abstractmethod
    def give_clue(self) -> str:
        pass

    @abstractmethod
    def give_answer(self, clue: str) -> str:
        pass
