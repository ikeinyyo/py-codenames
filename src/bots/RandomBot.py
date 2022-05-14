from .BotBase import BotBase
import random


class RandomBot(BotBase):
    def __init__(self):
        super().__init__()

    def give_clue(self, is_red_turn):
        return f"{'red' if is_red_turn else 'blue'}clue {random.randint(2,5)}"

    def give_answer(self, is_red_turn):
        words = self._board.get_available_words()
        return random.choice(words['red'] + words['blue'] + words['murderer'] + words['neutral'])
