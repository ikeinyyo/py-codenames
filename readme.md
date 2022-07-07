# Py-Codenames

Py-Codenames is an experiment to create an AI that can play the [Codenames](https://boardgamegeek.com/boardgame/178900/codenames) board game.

## About Codenames

This is the official description about Codenames on [Board Game Geek](https://boardgamegeek.com/boardgame/178900/codenames) website.

_The game is divided into red and blue, each side has a team leader, the team leader's goal is to lead their team to the final victory._

_At the beginning of the game, there will be 25 cards on the table with different words. Each card has a corresponding position, representing different colors._

_Only the team leader can see the color of the card. The team leader should prompt according to the words, let his team members find out the cards of their corresponding colors, and find out all the cards of their own colors to win._

## About Py-Codenames

The idea is to create an AI able to play Codenames as a team leader (to guess clues to the team), and as a member of the team (to try to choose the correct words).

## bot implementation

In this project, we test some NLP methods and other AI techniques to try to play Codenames.

Everybody can implement their own bot to play Codenames as a team leader or as a member team.

### How to implement your own bot?

There is an abstract class at `src/bots/BotBase.py` that able us to create a bot.

```py
class BotBase(ABC):
    # ...

    @abstractmethod
    def give_clue(self):
        pass

    @abstractmethod
    def give_answer(self, clue):
        pass
```

You have to implement this abstract class with your code to create a bot. Let me show you an example:

```py
from .BotBase import BotBase
import random


class RandomBot(BotBase):
    def __init__(self, is_captain=False, is_team_member=False, language="es"):
        super().__init__(is_captain, is_team_member, language)

    def give_clue(self):
        board_words = self._board.get_available_words_per_team()
        return f"{'red' if self.is_red else 'blue'}clue {random.randint(2,5)}"

    def give_answer(self, clue):
        return random.choice(self._board.get_available_words())
```

As you can see, the `BotBase` has a protected variable called `_board` that you can use to get the available words to choose the correct words as a team member or the available words per team to try to give a clue as a team leader.

Also, the `BotBase` has a public variable `_is_red` to indicate if the bot is from the Red or Blue team.

At the constructor method, you have to indicate the language and if the bot is a captain (team leader) or/and is bot is team member.

### How to run your bot?

Just you have to import your bot at `src/main.py`, create a bot instance, and pass the bot to the Codenames class.

```py
from bots.RandomBot import RandomBot
from bots.DistanceBot import DistanceBot
from codenames import Codenames

def run_game(log_game):
    red_bot = RandomBot(is_team_member=True, is_captain=True)
    blue_bot = DistanceBot(is_team_member=True)
    codenames = Codenames(
        red_bot=red_bot, blue_bot=blue_bot, log_history=log_game)
    codenames.play()
    if log_game:
        save_history(codenames.get_history())
```

### We are looking forward to your bot implementations

You can contribute to this project with your own bot implementations. Just create a Pull Request!

### Register games to train the new bots

You can register your games using the Py-Codenames application. Just run the application using the `--log` argument.

```py
python main.py --log
```

When the human give a clue, the application will ask about the words the bot should to guess. It will create a JSON file with the game history. Let me show you an example:

```json
{
    "id": "44aacbd6-6b8a-4b71-a1e8-a36426b15800",
    "datetime": "2022-06-03T16:10:53Z",
    "game": [
        {
            "team": "blue",
            "clue": "marvel",
            "occurrencies": 2,
            "words": [
                "hollywood",
                "superhéroe"
            ],
            "board": {
                "red": [
```

## Pylint

Tu run `pylint`, please use the following command:

```sh
# pylint <path>
pylint src/
```

## Authors

- [José Manuel Pinto](https://github.com/MrDevoid) - Cloud Analytics Consultant
- [Sergio Gallardo](https://github.com/ikeinyyo) - AI Specialist
