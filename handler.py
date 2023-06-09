import os
import re

from bs4 import BeautifulSoup

from game import Game
from player import Player
from position import Position


class Handler:
    def __init__(self):
        self.history_path = "C:\\Users\\earde\\AppData\\Local\\Holland Casino\\data\\HitBox\\History\\TempData"
        self.max_file_read = 4

    def get_newest_dir(self):
        if not os.path.exists(self.history_path):
            raise Exception(f"No games found in {self.history_path}")
        all_dirs = os.listdir(self.history_path)
        all_dirs = [os.path.join(self.history_path, d) for d in all_dirs]
        newest_dir = max(all_dirs, key=os.path.getmtime)
        newest_dir = os.path.join(newest_dir, "Data\\Tournaments")
        return newest_dir

    def get_newest_files(self, path) -> [str]:
        result = []
        for d in os.listdir(path):
            if "xml" in d:
                bd = os.path.join(path, d)
                result.append(bd)
        if len(result) == 0:
            print("No active games")
            return result
        result = sorted(result, key=os.path.getmtime, reverse=True)[:self.max_file_read]
        return result

    def get_bs(self, path) -> BeautifulSoup:
        with open(path, 'r') as f:
            data = f.read()
        bs_data = BeautifulSoup(data, "xml")
        return bs_data

    def get_digits(self, string) -> int:
        return int(re.sub("\\D", '', string))

    def get_games(self) -> [Game]:
        path = self.get_newest_dir()
        result = self.get_newest_files(path)

        games = []
        for r in result:
            bs = self.get_bs(r)
            bs_general = bs.find('general')
            bs_table_name = bs_general.find('tablename').text
            bs_table_name = str(self.get_digits(bs_table_name))[4:]
            bs_games = bs.find_all('game')
            if len(bs_games) <= 0:
                return []
            bs_game = bs_games.pop()
            # Get actions
            bs_actions = bs_game.find_all('action')
            ante = 0
            sb = 0
            sb_name = None
            bb = 0
            bb_name = None
            for a in bs_actions:
                size = self.get_digits(a.get('sum'))
                name = a.get('player')
                t = a.get('type')
                if t == '15':
                    ante = size
                elif t == '1':
                    sb = size
                    sb_name = name
                elif t == '2':
                    bb = size
                    bb_name = name
            # Get players
            bs_players = bs_game.find_all('player')
            players = []
            for p in bs_players:
                p_name = p.get('name')
                p_chips = p.get('chips')
                p_chips = self.get_digits(p_chips)
                position = Position.DEALER
                if p_name == sb_name:
                    position = Position.SMALL_BLIND
                elif p_name == bb_name:
                    position = Position.BIG_BLIND
                players.append(Player(chips=p_chips,
                                      bb_sum=bb,
                                      name=p_name,
                                      position=position))
            game = Game(players=players,
                        table_name=bs_table_name,
                        ante=ante,
                        sb=sb,
                        bb=bb)
            games.append(game)

        return games