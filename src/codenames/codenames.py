from dataclasses import dataclass, field
import random
from typing import List
import uuid
from datetime import datetime
from enum import Enum

from termcolor import colored, cprint
from console_toolkit.console_toolkit import clear_console

from .helpers.board import Board
from .helpers.state_machine import StateMachine


@dataclass
class Codenames:
    class States(Enum):
        ANSWER = "ANSWER"
        CLUE = "CLUE"
        CREATE_LOG = "CREATE_LOG"
        CHANGE_TEAM = "CHANGE_TEAM"
        WIN = "WIN"
        LOSE = "LOSE"
        FINISH = "FINISH"

    MAX_LOGS_LINES: int = 7

    __red_bot: object = None
    __blue_bot: object = None
    __is_red_turn: bool = random.randint(0, 1) == 1
    __logs: List[str] = field(default_factory=list)
    __log_history: bool = False
    __clue: str = None
    __ocurrencies: int = None
    __current_answers: int = None
    __current_bot: object = None

    def __init__(self, red_bot: object = None, blue_bot: object = None, words: List[str] = None,
                 log_history: bool = False, language: str = "es"):
        self.__red_bot = red_bot
        self.__blue_bot = blue_bot
        self.__log_history = log_history
        self.__logs = [" "] * self.MAX_LOGS_LINES
        self.__initialize_board(words, language)
        self.__initialize_state_machine()
        self.__initialize_clue()
        self.__initialize_history()

    def play(self) -> None:
        clear_console()
        self.__initialize_bots()
        self.__state_machine.run()

    def get_history(self) -> dict:
        return {
            'id': str(uuid.uuid4()),
            'datetime': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
            'game': self.__history
        }

    def __initialize_state_machine(self) -> None:
        self.__state_machine = StateMachine()
        self.__state_machine.add_state(self.States.CLUE, self.__clue_phase)
        self.__state_machine.add_state(
            self.States.CREATE_LOG, self.__add_history_step)
        self.__state_machine.add_state(self.States.ANSWER, self.__answer_phase)
        self.__state_machine.add_state(
            self.States.CHANGE_TEAM, self.__change_team)
        self.__state_machine.add_state(self.States.LOSE, self.__lose)
        self.__state_machine.add_state(self.States.WIN, self.__win)
        self.__state_machine.add_state(
            self.States.FINISH, None, end_state=True)
        self.__state_machine.set_start(self.States.CLUE)

    def __clue_phase(self) -> States:
        try:
            self.__show_board(True)
            clue = self.__get_clue()
            self.__log(f"? {clue}")
            self.__process_clue(clue)
            return (self.States.ANSWER if not self.__log_history or self.__current_bot.is_captain
                    else self.States.CREATE_LOG)
        except:
            return self.States.CLUE

    def __add_history_step(self) -> States:
        try:
            self.__show_board(True)
            self.__show_clue_message()
            words = input(colored(
                "Please, insert the words that bot should guess " +
                "with your clue (split by ','): ", 'cyan'))
            words = words.replace(' ', '').split(',')
            board = self.__board.get_available_words_per_team()

            if (len(words) != self.__ocurrencies or
                    not all(word in (board['red'] if self.__is_red_turn else
                                     board['blue']) for word in words)):
                raise Exception(
                    "The words list has to have the same length that the clue " +
                    "number and the words has to be in the correct team board.")

            self.__history.append({
                'team': 'red' if self.__is_red_turn else 'blue',
                'clue': self.__clue.lower(),
                'occurrencies': self.__ocurrencies,
                'words': words,
                'board': board
            })
            return self.States.ANSWER
        except:
            return self.States.CREATE_LOG

    def __answer_phase(self) -> States:
        try:
            self.__show_board(False)
            answer = self.__get_answer()
            return self.__process_answer(answer)
        except:
            return self.States.ANSWER

    def __change_team(self) -> States:
        self.__is_red_turn = not self.__is_red_turn
        self.__set_current_bot()
        self.__initialize_clue()
        return self.States.CLUE

    def __lose(self) -> States:
        return self.__end_game(self.__create_lose_message())

    def __win(self) -> States:
        return self.__end_game(self.__create_win_message())

    def __end_game(self, message: str) -> States:
        self.__show_board(True)
        print(message)
        Codenames.__show_farewell_message()
        return self.States.FINISH

    def __initialize_bots(self) -> None:
        if self.__red_bot:
            self.__red_bot.set_red_team()
        if self.__blue_bot:
            self.__blue_bot.set_blue_team()
        self.__set_current_bot()

    def __initialize_clue(self) -> None:
        self.__clue = ""
        self.__ocurrencies = 0
        self.__current_answers = 0

    def __initialize_board(self, words: List[str], language: str) -> None:
        self.__board = Board(self.__is_red_turn, words, language)
        self.__red_bot.set_board(self.__board)
        self.__blue_bot.set_board(self.__board)

    def __initialize_history(self) -> None:
        self.__history = []

    def __process_clue(self, clue: str) -> None:
        [clue, ocurrencies] = clue.split(' ')
        self.__clue = clue.upper()
        self.__ocurrencies = int(ocurrencies)

    def __show_board(self, show_colors: bool) -> None:
        clear_console()
        self.__board.show(show_colors, self.__logs)

    def __process_answer(self, answer: str) -> States:
        answer_reponse = self.__board.select_word(
            answer.lower(), self.__is_red_turn)
        self.__current_answers = self.__current_answers + 1
        # TODO: Refactor state management
        if answer_reponse == Board.AnswerResponse.LOSE:
            self.__log(answer, 'white')
            return self.States.LOSE
        if answer_reponse in (Board.AnswerResponse.RED_WIN, Board.AnswerResponse.BLUE_WIN):
            self.__is_red_turn = answer_reponse == Board.AnswerResponse.RED_WIN
            self.__log(answer)
            return self.States.WIN
        if answer_reponse == Board.AnswerResponse.IS_WRONG_TEAM:
            self.__log(answer, 'blue' if self.__is_red_turn else 'red')
            return self.States.CHANGE_TEAM
        if answer_reponse == Board.AnswerResponse.IS_NEUTRAL:
            self.__log(answer, "yellow")
            return self.States.CHANGE_TEAM
        if self.__current_answers >= self.__ocurrencies:
            self.__log(answer)
            return self.States.CHANGE_TEAM
        self.__log(answer)
        return self.States.ANSWER

    def __get_clue(self) -> str:
        if self.__current_bot.is_captain:
            return self.__current_bot.give_clue()
        return input(self.__create_request_clue_message())

    def __get_answer(self) -> str:
        if self.__current_bot.is_team_member:
            return self.__current_bot.give_answer(self.__clue)
        self.__show_clue_message()
        return input(self.__create_request_answer_message())

    def __set_current_bot(self) -> None:
        self.__current_bot = self.__red_bot if self.__is_red_turn else self.__blue_bot

    def __show_clue_message(self) -> None:
        cprint(' '.join([colored("Current clue:", 'cyan'),
                         colored(f"{self.__clue}",
                                 'red' if self.__is_red_turn else 'blue'),
                         colored(
                             f"[{self.__current_answers}/{self.__ocurrencies}]", 'cyan')
                         ]))

    def __create_request_clue_message(self) -> str:
        return colored(f"{'Red' if self.__is_red_turn else 'Blue'} captain, insert a clue: ",
                       'red' if self.__is_red_turn else 'blue')

    def __create_request_answer_message(self) -> str:
        return colored(f"{'Red' if self.__is_red_turn else 'Blue'} team, insert your awnser: ",
                       'red' if self.__is_red_turn else 'blue')

    @classmethod
    def __show_farewell_message(cls) -> str:
        return cprint("Thanks for play Py-Codenames!", 'cyan')

    def __create_win_message(self) -> str:
        return ' '.join([
            colored(f"{'Red' if self.__is_red_turn else 'Blue'} team has completed " +
                    f"the panel, so {'Red' if self.__is_red_turn else 'Blue'}",
                    'red' if self.__is_red_turn else 'blue'),
            colored("WIN",
                    'red' if self.__is_red_turn else 'blue', attrs=['reverse']),
            colored("the game!", 'red' if self.__is_red_turn else 'blue')])

    def __create_lose_message(self) -> str:
        return ' '.join([
            colored(f"{'Red' if self.__is_red_turn else 'Blue'} team has chosen " +
                    f"the murderer, so {'Red' if self.__is_red_turn else 'Blue'} team",
                    'red' if self.__is_red_turn else 'blue'),
            colored("LOSE",
                    'red' if self.__is_red_turn else 'blue', attrs=['reverse']),
            colored("the game!", 'red' if self.__is_red_turn else 'blue')])

    def __log(self, message: str, color: str = None) -> None:
        color = color if color else 'red' if self.__is_red_turn else 'blue'
        self.__logs.append(colored(message.upper(), color))
        self.__logs = self.__logs[-self.MAX_LOGS_LINES:]
