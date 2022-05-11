import os

from termcolor import colored, cprint


def print_board(board):
    max_word_len = max(list(map(lambda word: len(word), board['words']))) + 2
    words = list(map(lambda word: word.center(
        max_word_len), board['words']))

    clear_console()
    cprint('Py-Codenames'.center(max_word_len*5), 'cyan')
    cprint('=' * (max_word_len*5+2), 'cyan')
    for i in range(5):
        print(' '.join(colored(word, __select_color(board, word), attrs=__select_attrs(board, word))
              for word in words[i*5:i*5+5]))
    cprint('=' * (max_word_len*5+2), 'cyan')


def clear_console():
    os.system('clear')


def __select_attrs(board, key):
    word = key.strip()
    if word in board['selected']:
        return ['reverse']
    return []


def __select_color(board, key):
    word = key.strip()
    if word in board['red']:
        return 'red'
    elif word in board['blue']:
        return 'blue'
    elif word in board['neutral']:
        return 'yellow'
    return 'white'
