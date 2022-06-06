import uuid
import random
from enum import Enum
from datetime import datetime

from console_toolkit.console_toolkit import clear_console
from termcolor import colored, cprint

from .helpers.Board import Board
from .helpers.StateMachine import StateMachine


class Codenames:
    class States(Enum):
        ANSWER = "ANSWER"
        CLUE = "CLUE"
        CREATE_LOG = "CREATE_LOG"
        CHANGE_TEAM = "CHANGE_TEAM"
        WIN = "WIN"
        LOSE = "LOSE"
        FINISH = "FINISH"

    MAX_LOGS_LINES = 7

    def __init__(self, red_bot=None, blue_bot=None, words=None, log_history=False, language="es"):
        self.__red_bot = red_bot
        self.__blue_bot = blue_bot
        self.__is_red_turn = random.randint(0, 1) == 1
        self.__logs = [" "] * self.MAX_LOGS_LINES
        self.__log_history = log_history
        self.__initialize_board(words, language)
        self.__initialize_state_machine()
        self.__initialize_clue()
        self.__initialize_history()

    def play(self):
        clear_console()
        self.__initialize_bots()
        self.__state_machine.run()

    def get_history(self):
        return {
            'id': str(uuid.uuid4()),
            'datetime': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
            'game': self.__history
        }

    def __initialize_state_machine(self):
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

    def __clue_phase(self):
        try:
            self.__show_board(True)
            clue = self.__get_clue()
            self.__log(f"? {clue}")
            self.__process_clue(clue)
            return self.States.ANSWER if not self.__log_history or self.__current_bot.is_captain else self.States.CREATE_LOG
        except:
            return self.States.CLUE

    def __add_history_step(self):
        try:
            self.__show_board(True)
            self.__show_clue_message()
            words = input(colored(
                "Please, insert the words that bot should guess with your clue (split by ','): ", 'cyan'))
            words = words.replace(' ', '').split(',')
            board = self.__board.get_available_words_per_team()

            if (len(words) != self.__ocurrencies or
                    not all(word in (board['red'] if self.__is_red_turn else board['blue']) for word in words)):
                raise Exception(
                    "The words list has to have the same length that the clue number and the words has to be in the correct team board.")

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

    def __initialize_history(self):
        self.__history = []

    def __process_clue(self, clue):
        [clue, ocurrencies] = clue.split(' ')
        self.__clue = clue.upper()
        self.__ocurrencies = int(ocurrencies)

    def __show_board(self, show_colors):
        clear_console()
        self.__board.show(show_colors, self.__logs)

    def __process_answer(self, answer):
        answer_reponse = self.__board.select_word(
            answer.lower(), self.__is_red_turn)
        self.__current_answers = self.__current_answers + 1
        # TODO: Refactor state management
        if answer_reponse == Board.AnswerResponse.LOSE:
            self.__log(answer, 'white')
            return self.States.LOSE
        if answer_reponse == Board.AnswerResponse.RED_WIN:
            self.__is_red_turn = True
            self.__log(answer)
            return self.States.WIN
        if answer_reponse == Board.AnswerResponse.BLUE_WIN:
            self.__is_red_turn = False
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

    def __get_clue(self):
        if self.__current_bot.is_captain:
            return self.__current_bot.give_clue()
        return input(self.__create_request_clue_message())

    def __get_answer(self):
        if self.__current_bot.is_team_member:
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

    def __log(self, message, color=None):
        color = color if color else 'red' if self.__is_red_turn else 'blue'
        self.__logs.append(colored(message.upper(), color))
        self.__logs = self.__logs[-self.MAX_LOGS_LINES:]
