import itertools
import random
from typing import Any, Tuple, List

import fasttext.util
import numpy as np
from nltk.corpus import wordnet as wn
from scipy.spatial import distance

from .bot_base import BotBase


class HypernymBot(BotBase):
    __model: object = None
    __lang: str = None
    __regularization_factor: float = 0.001

    def __init__(self, is_captain: bool = False, is_team_member: bool = False,
                 lang: str = "es") -> None:
        super().__init__(is_captain, is_team_member, lang)
        self.__model = self.__load_model()
        self.__lang = HypernymBot.__language_converter(lang)

    def give_clue(self) -> str:
        return f"{'red' if self.is_red else 'blue'}clue {random.randint(2,5)}"

    def give_answer(self, clue: str) -> str:
        clue = str.lower(clue)
        tuple_word_and_distance_to_common_hypernym = list(map(
            lambda word: (
                word, self.__get_distance_to_first_common_hypernym(clue, word)),
            self._board.get_available_words()))
        tuple_word_and_distance_to_common_hypernym.sort(
            key=lambda w: self.__get_similarity_factor(w, clue))
        return tuple_word_and_distance_to_common_hypernym[0][0]

    def __get_distance_to_first_common_hypernym(self, word1: str, word2: str) -> float:
        synsets_word1 = self.__get_synsets(word1)
        synsets_word2 = self.__get_synsets(word2)
        hypernyms = self.__get_firsts_common_hypernyms(synsets_word1, synsets_word2)
        distance_first_word = HypernymBot.__get_path_similarity_between_all_synsets(
                                                              self.__get_synsets(word1), hypernyms)
        distance_second_word = HypernymBot.__get_path_similarity_between_all_synsets(
                                                              self.__get_synsets(word2), hypernyms)
        total_distance_by_hypernym = np.add(distance_first_word, distance_second_word)
        idx_max_value = np.argmax(total_distance_by_hypernym)
        return [distance_first_word[idx_max_value], distance_second_word[idx_max_value]]

    def __get_similarity_factor(self, tuple_word_similarity: Tuple[str, Tuple[float, float]],
                                clue: str) -> float:
        total_hypernym_similarity = np.sum(tuple_word_similarity[1])
        distance__between_words = distance.cosine(
            self.__model.get_word_vector(tuple_word_similarity[0]),
            self.__model.get_word_vector(clue))
        regularised_distance = self.__regularization_factor * \
            (1/(1+distance__between_words))
        return -(total_hypernym_similarity) + regularised_distance

    def __check_common_or_new_hypernyms(self, hypernyms1: List[object],
                                        hypernyms2: List[object]) -> bool:
        exist_common_hypernyms = len(set(hypernyms1).intersection(hypernyms2)) > 0
        exist_more_hypernyms = not (self.__has_new_hypernyms(hypernyms1)
                                    or self.__has_new_hypernyms(hypernyms2))
        return exist_common_hypernyms or exist_more_hypernyms

    def __get_firsts_common_hypernyms(self, hypernyms1: List[object],
                                      hypernyms2: List[object]) -> Tuple[float, float]:
        if not self.__check_common_or_new_hypernyms(hypernyms1, hypernyms2):
            hypernyms_first_word = HypernymBot.__get_hypernyms_of_synsets(hypernyms1)
            hypernyms_second_word = HypernymBot.__get_hypernyms_of_synsets(hypernyms2)
            return self.__get_firsts_common_hypernyms(hypernyms_first_word, hypernyms_second_word)

        return list(set(hypernyms1).intersection(hypernyms2))

    def __get_synsets(self, word: str) -> List[object]:
        return wn.synsets(word, lang=self.__lang)

    def __load_model(self) -> Any:
        fasttext.util.download_model(
            self.language, if_exists='ignore')
        return fasttext.load_model(f"cc.{self.language}.300.bin")

    @staticmethod
    def __get_path_similarity_between_all_synsets(synsets1: List[object],
                                                  synsets2:List[object]) -> float:
        matrix_of_distances = list(map(lambda word1:
                                list(map(lambda word2:
                                    HypernymBot.__get_path_similarity(word1, word2),
                                synsets1)),
                            synsets2))
        max_distance_to_each_hypernym = list(map(max, matrix_of_distances))
        return max_distance_to_each_hypernym

    @staticmethod
    def __has_new_hypernyms(hypernyms_set: List[object]) -> bool:
        return len(hypernyms_set) != len(HypernymBot.__get_hypernyms_of_synsets(hypernyms_set))

    @staticmethod
    def __language_converter(language: str) -> str:
        language_dictionary = {'es': 'spa', 'en': 'eng'}
        return language_dictionary[language]

    @staticmethod
    def __get_hypernyms_of_synsets(synsets: List[object]) -> List[object]:
        new_hypernyms = list(map(lambda x: x.hypernyms(), synsets))
        hypernyms = list(set(synsets + itertools.chain(*new_hypernyms)))
        return hypernyms

    @staticmethod
    def __get_path_similarity(synset1: object, synset2: object) -> float:
        return wn.path_similarity(synset1, synset2) or 0
