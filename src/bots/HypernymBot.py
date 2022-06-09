from .BotBase import BotBase
import random
import itertools
import fasttext.util
from nltk.corpus import wordnet as wn
from scipy.spatial import distance
import numpy as np


class HypernymBot(BotBase):
    def __init__(self, is_captain=False, is_team_member=False, language="es"):
        super().__init__(is_captain, is_team_member, language)
        self.__model = self.__load_model()

    def give_clue(self):
        return f"{'red' if self.is_red else 'blue'}clue {random.randint(2,5)}"

    def give_answer(self, clue):
        clue = str.lower(clue)
        triple_list = list(map(lambda word: (word, self.__get_first_common_hypernym(clue, word)), self._board.get_available_words()))
        triple_list.sort(key = lambda w: -(np.sum(w[1]) + 0.001*(1/(1+distance.cosine(self.__model.get_word_vector(w[0]), self.__model.get_word_vector(clue))))))
        return triple_list[0][0]

    def __get_hypernyms_of_synsets(self, synsets):
        hypernyms = list(map(lambda x: x.hypernyms(), synsets))
        return list(set(itertools.chain(*hypernyms)))

    def __get_path_similarity(self, synset1, synset2):
        similarity = wn.path_similarity(synset1, synset2)
        similarity = similarity if similarity else 0
        return similarity


    def __get_first_common_hypernym(self, word1, word2, lang = 'spa'):
        try:
            temporal_hypernyms1 = self.__get_hypernyms_of_synsets(wn.synsets(word1, lang=lang))
            temporal_hypernyms2 = self.__get_hypernyms_of_synsets(wn.synsets(word2, lang=lang))
            hypernyms1 = list(set(temporal_hypernyms1))
            hypernyms2 = list(set(temporal_hypernyms2))
            while len(set(hypernyms1).intersection(hypernyms2))==0 and (len(temporal_hypernyms1)!=0 or len(temporal_hypernyms2)!=0):
                hypernyms1 = list(set(hypernyms1 + temporal_hypernyms1))
                hypernyms2 = list(set(hypernyms2 + temporal_hypernyms2))
                temporal_hypernyms1 = self.__get_hypernyms_of_synsets(temporal_hypernyms1)
                temporal_hypernyms2 = self.__get_hypernyms_of_synsets(temporal_hypernyms2)
            if len(set(hypernyms1).intersection(hypernyms2))!=0:
                hypernyms = list(set(hypernyms1).intersection(hypernyms2))
                possible_hypernyms = list(map(lambda x: max(list(map(lambda y: self.__get_path_similarity(x, y), wn.synsets(word1, lang=lang)))) + max(list(map(lambda y: self.__get_path_similarity(x, y), wn.synsets(word2, lang=lang)))),hypernyms))
                max_value = max(possible_hypernyms)
                similarity_to_word1 = max(list(map(lambda x: self.__get_path_similarity(hypernyms[possible_hypernyms.index(max_value)],x),wn.synsets(word1, lang=lang))))
                similarity_to_word2 = max(list(map(lambda x: self.__get_path_similarity(hypernyms[possible_hypernyms.index(max_value)],x),wn.synsets(word2, lang=lang))))
            else:
                similarity_to_word1 = 0
                similarity_to_word2 = 0
            return (similarity_to_word1, similarity_to_word2)
        except:
            return (0,0)
       
    def __load_model(self):
        fasttext.util.download_model(
            self.language, if_exists='ignore')
        return fasttext.load_model(f"cc.{self.language}.300.bin")
