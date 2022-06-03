import argparse
import json
import os

from bots.DistanceBot import DistanceBot
from bots.RandomBot import RandomBot
from codenames import Codenames


def run_game(log_game):
    red_bot = RandomBot(is_team_member=True, is_captain=True)
    blue_bot = DistanceBot(is_team_member=True)
    codenames = Codenames(
        red_bot=red_bot, blue_bot=blue_bot, log_history=log_game)
    codenames.play()
    if log_game:
        save_history(codenames.get_history())


def save_history(historial):
    path = 'history'
    if not os.path.exists(path):
        os.makedirs(path)
    with open(os.path.join(path, f"{historial['id']}.json"), 'w') as out_file:
        json.dump(historial, out_file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--log', required=False, action="store_true")
    args = parser.parse_args()
    run_game(args.log)
