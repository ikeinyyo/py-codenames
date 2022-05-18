from .BotBase import BotBase
import random


class RandomBot(BotBase):
    def __init__(self, is_captain=False):
        super().__init__(is_captain)

    def give_clue(self):
        return f"{'red' if self.is_red else 'blue'}clue {random.randint(2,5)}"

    def give_answer(self):
        return random.choice(self._board.get_available_words())
