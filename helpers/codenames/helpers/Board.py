import json
import os
import random
from enum import Enum

from termcolor import colored, cprint

from .exceptions import WordNotFoundException


class Board:
    class AnswerResponse(Enum):
        IS_CORRECT = 1
        IS_INCORRECT = 2
        RED_WIN = 3
        BLUE_WIN = 4
        LOSE = 5

    def __init__(self, is_red_turn, words=None, language="es"):
        if words and (not isinstance(words, list) or len(words) != 25):
            raise Exception(
                'The words parameter has to be a list with 25 strings.')
        self.__words = words if words else self.__load_words(language)
        self.__create_board(is_red_turn)
        self.__max_word_len = max(
            list(map(lambda word: len(word), self.__words))) + 2
        self.__words_to_show = list(
            map(lambda word: word.center(self.__max_word_len), self.__words))

    def __create_board(self, is_red_turn):
        self.__red = self.__words[:9 if is_red_turn else 8]
        self.__blue = self.__words[9 if is_red_turn else 8:17]
        self.__neutral = self.__words[17:24]
        self.__murderer = [self.__words[-1]]
        self.__selected_words = []
        random.shuffle(self.__words)

    def __load_words(self, language):
        with open(f"{os.path.dirname(__file__)}/../data/{language}.words.json") as in_file:
            words = json.load(in_file)['words']
            random.shuffle(words)
            return words[:25]

    def __select_attrs(self, word):
        word = word.strip()
        if word in self.__selected_words:
            return ['reverse']
        return []

    def __select_color(self, word, show_color):
        word = word.strip()
        if not show_color and not word in self.__selected_words:
            return 'white'
        if word in self.__red:
            return 'red'
        if word in self.__blue:
            return 'blue'
        if word in self.__neutral:
            return 'yellow'
        return 'white'

    def show(self, show_color):
        cprint('Py-Codenames'.center(self.__max_word_len*5), 'cyan')
        cprint('=' * (self.__max_word_len*5+2), 'cyan')
        for i in range(5):
            print(' '.join(colored(word.upper(), self.__select_color(word, show_color), attrs=self.__select_attrs(word))
                           for word in self.__words_to_show[i*5:i*5+5]))
        cprint('=' * (self.__max_word_len*5+2), 'cyan')

    def select_word(self, word, is_red_turn):
        if not word in self.__words:
            raise WordNotFoundException(word)

        self.__selected_words.append(word)

        if all(elem in self.__selected_words for elem in self.__murderer):
            return self.AnswerResponse.LOSE
        if all(elem in self.__selected_words for elem in self.__red):
            return self.AnswerResponse.RED_WIN
        if all(elem in self.__selected_words for elem in self.__blue):
            return self.AnswerResponse.BLUE_WIN
        if not word in (self.__red if is_red_turn else self.__blue):
            return self.AnswerResponse.IS_INCORRECT
        return self.AnswerResponse.IS_CORRECT
