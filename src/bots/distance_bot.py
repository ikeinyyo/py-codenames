import random
from typing import Any

from scipy.spatial import distance
import fasttext.util

from .bot_base import BotBase


class DistanceBot(BotBase):
    __model: object = None

    def __init__(self, is_captain=False, is_team_member=False, language="es"):
        super().__init__(is_captain, is_team_member, language)
        self.__model = self.__load_model()

    def give_clue(self) -> str:
        return f"{'red' if self.is_red else 'blue'}clue {random.randint(2,5)}"

    def give_answer(self, clue: str) -> str:
        word_vectors = [{'vector': self.__model.get_word_vector(
            word), 'word': word} for word in self._board.get_available_words()]
        clue_vector = self.__model.get_word_vector(clue)
        word_vectors.sort(key=lambda w: distance.cosine(
            w['vector'], clue_vector))
        return word_vectors[0]['word']

    def __load_model(self) -> Any:
        fasttext.util.download_model(
            self.language, if_exists='ignore')
        return fasttext.load_model(f"cc.{self.language}.300.bin")
