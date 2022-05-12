import random
from enum import Enum

from termcolor import colored, cprint

from helpers.console_toolkit.console_toolkit import clear_console

from .helpers.Board import Board
from .helpers.StateMachine import StateMachine


class Codenames:
    class States(Enum):
        ANSWER = "ANSWER"
        CLUE = "CLUE"
        CHANGE_TEAM = "CHANGE_TEAM"
        WIN = "WIN"
        LOSE = "LOSE"
        FINISH = "FINISH"

    def __init__(self, words=None, language="es"):
        self.__language = language
        self.__is_red_turn = random.randint(0, 1) == 1
        self.__board = Board(self.__is_red_turn, words, language)
        self.__initialize_state_machine()

        self.__clue = ""
        self.__ocurrencies = 0
        self.__current_answers = 0

    def __initialize_state_machine(self):
        self.__state_machine = StateMachine()
        self.__state_machine.add_state(self.States.CLUE, self.__give_clue)
        self.__state_machine.add_state(self.States.ANSWER, self.__give_answer)
        self.__state_machine.add_state(
            self.States.CHANGE_TEAM, self.__change_team)
        self.__state_machine.add_state(self.States.LOSE, self.__lose)
        self.__state_machine.add_state(self.States.WIN, self.__win)
        self.__state_machine.add_state(
            self.States.FINISH, None, end_state=True)
        self.__state_machine.set_start(self.States.CLUE)

    def __process_answer(self, answer):
        answer_reponse = self.__board.select_word(
            answer.lower(), self.__is_red_turn)
        self.__current_answers = self.__current_answers + 1

        if answer_reponse == Board.AnswerResponse.LOSE:
            return self.States.LOSE
        if answer_reponse == Board.AnswerResponse.RED_WIN:
            self.__is_red_turn = True
            return self.States.WIN
        if answer_reponse == Board.AnswerResponse.BLUE_WIN:
            self.__is_red_turn = False
            return self.States.WIN
        if answer_reponse == Board.AnswerResponse.IS_INCORRECT or self.__current_answers >= self.__ocurrencies:
            return self.States.CHANGE_TEAM
        return self.States.ANSWER

    def __show_board(self, show_colors):
        clear_console()
        self.__board.show(show_colors)

    def __give_clue(self):
        try:
            clear_console()
            self.__show_board(True)
            clue = input(colored(f"{'Red' if self.__is_red_turn else 'Blue'} captain, insert a clue: ",
                                 'red' if self.__is_red_turn else 'blue'))
            clue, ocurrencies = clue.split(' ')
            self.__clue = clue.upper()
            self.__ocurrencies = int(ocurrencies)
            return self.States.ANSWER
        except:
            return self.States.CLUE

    def __give_answer(self):
        try:
            self.__show_board(False)
            print(
                f"Current clue: {self.__clue} [{self.__current_answers}/{self.__ocurrencies}]")
            answer = input(colored(f"{'Red' if self.__is_red_turn else 'Blue'} team, insert your awnser: ",
                                   'red' if self.__is_red_turn else 'blue'))
            return self.__process_answer(answer)
        except:
            return self.States.ANSWER

    def __change_team(self):
        self.__is_red_turn = not self.__is_red_turn
        self.__current_answers = 0
        return self.States.CLUE

    def __lose(self):
        return self.__end_game(colored(f"{'Red' if self.__is_red_turn else 'Blue'} team choose the murderer. ",
                                       'red' if self.__is_red_turn else 'blue') +
                               colored(f"{'Red' if not self.__is_red_turn else 'Blue'} team win the game.",
                                       'red' if not self.__is_red_turn else 'blue'))

    def __win(self):
        return self.__end_game(colored(f"{'Red' if self.__is_red_turn else 'Blue'} win the game.",
                                       'red' if self.__is_red_turn else 'blue'))

    def __end_game(self, message):
        self.__show_board(True)
        print(message)
        print("Thanks for play Py-Codenames")
        return self.States.FINISH

    def play(self):
        self.__state_machine.run()
