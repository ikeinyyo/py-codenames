from bots.RandomBot import RandomBot
from bots.DistanceBot import DistanceBot
from codenames import Codenames

if __name__ == '__main__':
    red_bot = DistanceBot(is_captain=False)
    blue_bot = DistanceBot(is_captain=False)
    codenames = Codenames(
        red_bot=red_bot, blue_bot=blue_bot)
    codenames.play()
