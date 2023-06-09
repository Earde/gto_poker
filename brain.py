import random
import time

import requests
import json

from brain_model import BrainModel
from move import Move
from position import Position
from solution import Solution


class Brain:
    def __init__(self):
        self.auth = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjg2Mjk5MzYyLCJpYXQiOjE2ODU3Mjg5NDAsImp0aSI6IjM1M2Y5MzQwN2IwZDQ5MjliZWJhNDc3Yzc5OTJkZDRmIiwicHVibGljX2lkIjoiYWNjX2FhY3V2cTBpaWMiLCJlbWFpbCI6ImVhcmRlbGJAZ21haWwuY29tIn0.41XJetKi7PJiZMKMUPK7XZEHLSu0OAghmOnqVsh3XSs"
        self.refresh = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTg0MzQwODk0MCwiaWF0IjoxNjg1NzI4OTQwLCJqdGkiOiI3ZWY0ODVlNWRkN2E0NDM1OTdhMWZkYWY0MDQ1MDljYSIsInB1YmxpY19pZCI6ImFjY19hYWN1dnEwaWljIiwiZW1haWwiOiJlYXJkZWxiQGdtYWlsLmNvbSJ9.sJsjElUVxx_IDXVmKBOa3hnhWFncQyVyQ3svokLuEow"
        self.client_id = '3c394db4-bf2c-42e1-b0e7-a6036ce5c61e'
        self.url = "https://gtowizard.com/api/v1/poker/solution/?"

    def get_header(self):
        return {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Host': 'gtowizard.com',
            'Origin': 'https://app.gtowizard.com',
            'Referer': 'https://app.gtowizard.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'TE': 'trailers',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0',
            'GWCLIENTID': self.client_id,
            'Authorization': f"Bearer {self.auth}"
        }

    def post_refresh(self):
        url = "https://gtowizard.com/api/v1/token/refresh/"
        headers = self.get_header()
        headers['Content-Length'] = '303'
        headers['Content-Type'] = 'application/json;charset=utf-8'

        data = {
            "refresh": self.refresh
        }

        r = requests.post(url, json=data, headers=headers)
        if r.status_code == 200:
            self.auth = r.json()['access']
        else:
            print("Error refreshing token")

    def get_next_actions(self,
                         bb: float,
                         ante=False,
                         first_try=True,
                         preflop_actions="",
                         turn_actions="",
                         river_actions="",
                         board=""):
        time.sleep(random.randint(500, 3000) / 1000.0)
        gametype = "SpinsGeneralV2_R225"
        if ante:
            gametype = "SpinsAnteGeneral_R225"

        brain_model = BrainModel(gametype=gametype, bb=bb, ante=ante, preflop_actions=preflop_actions,
                                 turn_actions=turn_actions, river_actions=river_actions, board=board)
        if brain_model.exists():
            return

        url = self.url + f"gametype={gametype}"
        bb_str = str(bb) + ".17" if ante else ""
        url += f"&depth={bb_str}"
        url += f"&stacks={bb_str}-{bb_str}-{bb_str}"
        url += f"&preflop_actions={preflop_actions}"
        url += f"&turn_actions={turn_actions}"
        url += f"&river_actions={river_actions}"
        url += f"&board={board}"
        url += f"&cache_change=2022-10-08T00:00Z"

        headers = self.get_header()

        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            json_data = r.json()
            if json_data['solutions'] is None:
                return
            solutions: [Solution] = []
            for solution in json_data['solutions']:
                action = solution['action']
                position = None
                if action['position'] == 'BTN':
                    position = Position.DEALER
                elif action['position'] == 'SB':
                    position = Position.SMALL_BLIND
                elif action['position'] == 'BB':
                    position = Position.BIG_BLIND
                if position is None:
                    raise Exception("Position not found")

                if action['code'] == 'F':
                    move = Move.FOLD
                elif action['code'] == 'C':
                    move = Move.CALL
                elif action['code'] == 'RAI' and action['allin']:
                    move = Move.ALL_IN
                elif action['code'].startswith('R'):
                    move = Move.RAISE
                elif action['code'] == 'X':
                    move = Move.CHECK
                else:
                    raise Exception("Move not found")

                betsize = action['betsize']

                pf_actions = preflop_actions
                if pf_actions == "":
                    pf_actions = action['code']
                else:
                    pf_actions += f"-{action['code']}"

                strategy = solution['strategy']
                evs = solution['evs']

                solution = Solution(position=position, move=move, betsize=betsize, strategy=strategy, evs=evs)
                solutions.append(solution)

                self.get_next_actions(bb=bb, ante=ante, first_try=False, preflop_actions=pf_actions,
                                      turn_actions=turn_actions, river_actions=river_actions)
            brain_model.set_solutions(solutions=solutions)
            brain_model.save()

        elif first_try:
            self.post_refresh()
            self.get_next_actions(bb=bb, ante=ante, first_try=False, preflop_actions=preflop_actions,
                                  turn_actions=turn_actions, river_actions=river_actions)
        elif r.status_code == 204 or r.status_code == 400:
            print(f"No solutions found for {brain_model.get_id()}")
        else:
            print("Error getting next actions")
            print(r.status_code)
            print(r.text)
