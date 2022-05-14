class WordNotFoundException(Exception):
    def __init__(self, word):
        super().__init__(f"The word '{word}' doesn't exit on this board")
