import itertools
import random
from operator import itemgetter

import fasttext.util
import numpy as np
from nltk.corpus import wordnet as wn
from scipy.spatial import distance

from .BotBase import BotBase


class HypernymBot(BotBase):
    def __init__(self, is_captain=False, is_team_member=False, language="es", wn_lang='spa'):
        super().__init__(is_captain, is_team_member, language)
        self.__model = self.__load_model()
        self.__lang = wn_lang

    def give_clue(self):
        return f"{'red' if self.is_red else 'blue'}clue {random.randint(2,5)}"

    def give_answer(self, clue):
        clue = str.lower(clue)
        tuple_of_word_with_distance_to_common_hypernym = list(map(lambda word: (word, self.__get_distance_to_first_common_hypernym(clue, word)), self._board.get_available_words()))
        tuple_of_word_with_distance_to_common_hypernym.sort(key = lambda w: -(np.sum(w[1]) + 0.001*(1/(1+distance.cosine(self.__model.get_word_vector(w[0]), self.__model.get_word_vector(clue))))))
        return tuple_of_word_with_distance_to_common_hypernym[0][0]

    def __get_hypernyms_of_synsets(self, synsets):
        hypernyms = list(map(lambda x: x.hypernyms(), synsets))
        return list(set(itertools.chain(*hypernyms)))

    def __get_path_similarity(self, synset1, synset2):
        return wn.path_similarity(synset1, synset2) or 0

    def __get_distance_to_first_common_hypernym(self, word1, word2):
        return self.__get_distance_to_first_common_hypernym_aux(wn.synsets(word1, lang=self.__lang),wn.synsets(word2, lang=self.__lang),  word1,word2)
       
    def __get_distance_to_first_common_hypernym_aux(self, hypernyms1, hypernyms2, word1, word2):
        ## Base case
        if len(set(hypernyms1).intersection(hypernyms2)) > 0 or not (self.__has_new_hypernyms(hypernyms1) or self.__has_new_hypernyms(hypernyms2)):
            hypernyms = list(set(hypernyms1).intersection(hypernyms2))
            distance_to_first_word = list(map(lambda x: max(list(map(lambda y: self.__get_path_similarity(x, y), wn.synsets(word1, lang=self.__lang)))), hypernyms))
            distance_to_second_word = list(map(lambda x: max(list(map(lambda y: self.__get_path_similarity(x, y), wn.synsets(word2, lang=self.__lang)))), hypernyms))
            possible_hypernyms = zip(np.add(distance_to_first_word, distance_to_second_word), distance_to_first_word, distance_to_second_word)
            max_value = max(possible_hypernyms, key=itemgetter(0), default=(0,0,0))
            return [max_value[1], max_value[2]]   
        
        return self.__get_distance_to_first_common_hypernym_aux(hypernyms1=list(set(hypernyms1 + self.__get_hypernyms_of_synsets(hypernyms1))), hypernyms2=list(set(hypernyms2 + self.__get_hypernyms_of_synsets(hypernyms2))), word1=word1, word2=word2)

    
    def __has_new_hypernyms(self, hypernyms_set):
        return len(hypernyms_set) != len(list(set(hypernyms_set + self.__get_hypernyms_of_synsets(hypernyms_set))))

    def __load_model(self):
        fasttext.util.download_model(
            self.language, if_exists='ignore')
        return fasttext.load_model(f"cc.{self.language}.300.bin")
