from .BotBase import BotBase
import random
import fasttext.util
from scipy.spatial import distance


class DistanceBot(BotBase):
    def __init__(self, is_captain=False, language="es"):
        super().__init__(is_captain, language)
        self.__model = self.__load_model()

    def give_clue(self):
        return f"{'red' if self.is_red else 'blue'}clue {random.randint(2,5)}"

    def give_answer(self, clue):
        word_vectors = [{'vector': self.__model.get_word_vector(
            word), 'word': word} for word in self._board.get_available_words()]
        clue_vector = self.__model.get_word_vector(clue)
        word_vectors.sort(key=lambda w: distance.cosine(
            w['vector'], clue_vector))
        return word_vectors[0]['word']

    def __load_model(self):
        fasttext.util.download_model(
            self.language, if_exists='ignore')
        return fasttext.load_model(f"cc.{self.language}.300.bin")
