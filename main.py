import random

from helpers.console_toolkit import print_board


def create_board():
    board = {
        'red': ['llave', 'verde', 'fuerza', 'casino', 'hospital', 'robot', 'hechizo', 'rojo'],
        'blue': ['águila', 'miedo', 'mesa', 'playa', 'espalda', 'sonido', 'botella', 'hotel', 'alien'],
        'neutral': ['perro', 'topo', 'viento', 'manzana', 'ballena', 'tomate', 'piscina'],
        'murderer': ['camarero'],
        'selected': ['perro', 'miedo', 'mesa', 'llave']
    }
    board['words'] = board['red'] + board['blue'] + \
        board['neutral'] + board['murderer']
    random.shuffle(board['words'])
    return board


def main():
    board = create_board()
    word = ''
    while word != 'exit':
        print_board(board)
        word = input('Introduce una palabra: ')
        board['selected'].append(word)


if __name__ == '__main__':
    main()
