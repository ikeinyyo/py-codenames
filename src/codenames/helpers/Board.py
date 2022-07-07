from dataclasses import dataclass, field
import json
import os
import random
from enum import Enum
from typing import List

from termcolor import colored

from .exceptions import WordNotFoundException


@dataclass
class Board:
    class AnswerResponse(Enum):
        IS_CORRECT = 1
        IS_WRONG_TEAM = 2
        IS_NEUTRAL = 3
        RED_WIN = 4
        BLUE_WIN = 5
        LOSE = 6

    __words: List[str] = field(default_factory=list)
    __max_word_len: int = 0
    __words_to_show: List[str] = field(default_factory=list)

    def __init__(self, is_red_turn: bool, words: List[str] = None, language: str = "es"):
        if words and (not isinstance(words, list) or len(words) != 25):
            raise Exception(
                'The words parameter has to be a list with 25 strings.')
        self.__words = words if words else Board.__load_words(language)
        self.__create_board(is_red_turn)
        self.__max_word_len = max(
            list(map(len, self.__words))) + 2
        self.__words_to_show = list(
            map(lambda word: word.center(self.__max_word_len), self.__words))

    def show(self, show_color: bool, logs: List[str]) -> None:
        # TODO: Extract show to another class
        print(
            ' '.join([colored('Py-Codenames'.center((self.__max_word_len+1)*5-1), 'cyan'), 'Logs']))
        print(
            ' '.join([colored('=' * ((self.__max_word_len+1)*5-1), 'cyan'), logs[0]]))
        for line_index in range(5):
            print(' '.join([colored(word.upper(),
                                    self.__select_color(word, show_color),
                                    attrs=self.__select_attrs(word)
                                    )
                            for word in self.__words_to_show[line_index*5:line_index*5+5]] +
                           [logs[line_index+1]]))
        print(
            ' '.join([colored('=' * ((self.__max_word_len+1)*5-1), 'cyan'), logs[6]]))

    def get_available_words_per_team(self) -> dict:
        return {
            'red': [word for word in self.__red if not word in self.__selected_words],
            'blue': [word for word in self.__blue if not word in self.__selected_words],
            'neutral': [word for word in self.__neutral if not word in self.__selected_words],
            'murderer': [word for word in self.__murderer if not word in self.__selected_words]
        }

    def get_available_words(self) -> List[str]:
        return [word for word in self.__words if not word in self.__selected_words]

    def select_word(self, word: str, is_red_turn: bool) -> AnswerResponse:
        if not word in self.__words or word in self.__selected_words:
            raise WordNotFoundException(word)

        self.__selected_words.append(word)

        if all(word in self.__selected_words for word in self.__murderer):
            return self.AnswerResponse.LOSE
        if all(word in self.__selected_words for word in self.__red):
            return self.AnswerResponse.RED_WIN
        if all(word in self.__selected_words for word in self.__blue):
            return self.AnswerResponse.BLUE_WIN
        if word in self.__neutral:
            return self.AnswerResponse.IS_NEUTRAL
        if not word in (self.__red if is_red_turn else self.__blue):
            return self.AnswerResponse.IS_WRONG_TEAM
        return self.AnswerResponse.IS_CORRECT

    def __create_board(self, is_red_turn: bool) -> None:
        self.__red = self.__words[:9 if is_red_turn else 8]
        self.__blue = self.__words[9 if is_red_turn else 8:17]
        self.__neutral = self.__words[17:24]
        self.__murderer = [self.__words[-1]]
        self.__selected_words = []
        random.shuffle(self.__words)

<<<<<<< HEAD
    @ classmethod
    def __load_words(cls, language: str) -> List[str]:
        file_name = f"{os.path.dirname(__file__)}/../data/{language}.words.json"
        with open(file_name, 'r', encoding='utf-8') as in_file:
=======
    def __load_words(self, language):
        with open(f"{os.path.dirname(__file__)}/../data/{language}.words.json", encoding='utf8') as in_file:
>>>>>>> 2bc99f99607b2a71438b1e3114da9f7d362f35de
            words = json.load(in_file)['words']
            random.shuffle(words)
            return words[:25]

    def __select_attrs(self, word: str) -> List[str]:
        word = word.strip()
        if word in self.__selected_words:
            return ['reverse']
        return []

    def __select_color(self, word: str, show_color: bool) -> str:
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
