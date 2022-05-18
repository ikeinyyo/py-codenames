from bots.RandomBot import RandomBot
from codenames import Codenames

if __name__ == '__main__':
    red_bot = RandomBot(is_captain=True)
    blue_bot = RandomBot(is_captain=True)
    codenames = Codenames(
        red_bot=red_bot, blue_bot=blue_bot)
    codenames.play()
