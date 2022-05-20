import random
from enum import Enum

from console_toolkit.console_toolkit import clear_console
from termcolor import colored, cprint

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

    def __init__(self, red_bot=None, blue_bot=None, words=None, language="es"):
        self.__red_bot = red_bot
        self.__blue_bot = blue_bot
        self.__is_red_turn = random.randint(0, 1) == 1
        self.__initialize_board(words, language)
        self.__initialize_state_machine()
        self.__initialize_clue()

    def play(self):
        clear_console()
        self.__initialize_bots()
        self.__state_machine.run()

    def __initialize_state_machine(self):
        self.__state_machine = StateMachine()
        self.__state_machine.add_state(self.States.CLUE, self.__clue_phase)
        self.__state_machine.add_state(self.States.ANSWER, self.__answer_phase)
        self.__state_machine.add_state(
            self.States.CHANGE_TEAM, self.__change_team)
        self.__state_machine.add_state(self.States.LOSE, self.__lose)
        self.__state_machine.add_state(self.States.WIN, self.__win)
        self.__state_machine.add_state(
            self.States.FINISH, None, end_state=True)
        self.__state_machine.set_start(self.States.CLUE)

    def __clue_phase(self):
        try:
            self.__show_board(True)
            clue = self.__get_clue()
            self.__process_clue(clue)
            return self.States.ANSWER
        except:
            return self.States.CLUE

    def __answer_phase(self):
        try:
            self.__show_board(False)
            answer = self.__get_answer()
            return self.__process_answer(answer)
        except:
            return self.States.ANSWER

    def __change_team(self):
        self.__is_red_turn = not self.__is_red_turn
        self.__set_current_bot()
        self.__initialize_clue()
        return self.States.CLUE

    def __lose(self):
        return self.__end_game(self.__create_lose_message())

    def __win(self):
        return self.__end_game(self.__create_win_message())

    def __end_game(self, message):
        self.__show_board(True)
        print(message)
        self.__show_farewell_message()
        return self.States.FINISH

    def __initialize_bots(self):
        if self.__red_bot:
            self.__red_bot.set_red_team()
        if self.__blue_bot:
            self.__blue_bot.set_blue_team()
        self.__set_current_bot()

    def __initialize_clue(self):
        self.__clue = ""
        self.__ocurrencies = 0
        self.__current_answers = 0

    def __initialize_board(self, words, language):
        self.__board = Board(self.__is_red_turn, words, language)
        self.__red_bot.set_board(self.__board)
        self.__blue_bot.set_board(self.__board)

    def __process_clue(self, clue):
        [clue, ocurrencies] = clue.split(' ')
        self.__clue = clue.upper()
        self.__ocurrencies = int(ocurrencies)

    def __show_board(self, show_colors):
        clear_console()
        self.__board.show(show_colors)

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

    def __get_clue(self):
        if self.__current_bot.is_captain:
            return self.__current_bot.give_clue()
        return input(self.__create_request_clue_message())

    def __get_answer(self):
        if not self.__current_bot.is_captain:
            return self.__current_bot.give_answer(self.__clue)
        self.__show_clue_message()
        return input(self.__create_request_answer_message())

    def __set_current_bot(self):
        self.__current_bot = self.__red_bot if self.__is_red_turn else self.__blue_bot

    def __show_clue_message(self):
        cprint(' '.join([colored("Current clue:", 'cyan'),
                         colored(f"{self.__clue}",
                                 'red' if self.__is_red_turn else 'blue'),
                        colored(
                            f"[{self.__current_answers}/{self.__ocurrencies}]", 'cyan')
                         ]))

    def __create_request_clue_message(self):
        return colored(f"{'Red' if self.__is_red_turn else 'Blue'} captain, insert a clue: ",
                       'red' if self.__is_red_turn else 'blue')

    def __create_request_answer_message(self):
        return colored(f"{'Red' if self.__is_red_turn else 'Blue'} team, insert your awnser: ",
                       'red' if self.__is_red_turn else 'blue')

    def __show_farewell_message(self):
        return cprint("Thanks for play Py-Codenames!", 'cyan')

    def __create_win_message(self):
        return ' '.join([
            colored(f"{'Red' if self.__is_red_turn else 'Blue'} team has completed the panel, so {'Red' if self.__is_red_turn else 'Blue'}",
                    'red' if self.__is_red_turn else 'blue'),
            colored(f"WIN",
                    'red' if self.__is_red_turn else 'blue', attrs=['reverse']),
            colored(f"the game!", 'red' if self.__is_red_turn else 'blue')])

    def __create_lose_message(self):
        return ' '.join([
            colored(f"{'Red' if self.__is_red_turn else 'Blue'} team has chosen the murderer, so {'Red' if self.__is_red_turn else 'Blue'} team",
                    'red' if self.__is_red_turn else 'blue'),
            colored(f"LOSE",
                    'red' if self.__is_red_turn else 'blue', attrs=['reverse']),
            colored(f"the game!", 'red' if self.__is_red_turn else 'blue')])
