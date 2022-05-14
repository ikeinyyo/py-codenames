from bots.RandomBot import RandomBot
from codenames import Codenames

if __name__ == '__main__':
    bot = RandomBot()
    codenames = Codenames(bot, is_bot_captain=True)
    codenames.play()
