from .BotBase import BotBase
import random


class RandomBot(BotBase):
    def __init__(self, is_captain=False, language="es"):
        super().__init__(is_captain, language)

    def give_clue(self):
        return f"{'red' if self.is_red else 'blue'}clue {random.randint(2,5)}"

    def give_answer(self, clue):
        return random.choice(self._board.get_available_words())
