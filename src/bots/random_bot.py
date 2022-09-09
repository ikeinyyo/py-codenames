import random

from .bot_base import BotBase


class RandomBot(BotBase):
    def give_clue(self) -> str:
        return f"{'red' if self.is_red else 'blue'}clue {random.randint(2,5)}"

    def give_answer(self, clue: str) -> str:
        return random.choice(self._board.get_available_words())
