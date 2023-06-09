from pathlib import Path

import jsonpickle

from solution import Solution


class BrainModel:
    save_path = Path("C:\\Users\\earde\\Desktop\\brain")

    gametype: str = ""
    ante: bool = False
    bb: float = 0.0
    solutions: [Solution] = []
    preflop_actions: str = ""
    turn_actions: str = ""
    river_actions: str = ""
    board: str = ""

    def __init__(self, gametype: str, ante: bool, bb: float,
                 preflop_actions: str, turn_actions: str, river_actions: str, board: str):
        self.gametype = gametype
        self.ante = ante
        self.bb = bb
        self.preflop_actions = preflop_actions
        self.turn_actions = turn_actions
        self.river_actions = river_actions
        self.board = board

    def exists(self) -> bool:
        path = self.save_path.joinpath(f"{self.get_id()}.json")
        return path.exists()

    def save(self):
        path = self.save_path.joinpath(f"{self.get_id()}.json")
        with open(path, "w") as f:
            f.write(self.to_json())

    def set_solutions(self, solutions: [Solution]):
        self.solutions = solutions

    def get_id(self) -> str:
        return f"{self.ante}_{self.bb}_{self.preflop_actions}_{self.turn_actions}_{self.river_actions}_{self.board}"

    def to_json(self) -> str:
        return jsonpickle.encode(self)