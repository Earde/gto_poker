from move import Move
from position import Position


class Solution:
    strategy: [] = []
    evs: [] = []
    move: Move = None
    position: Position = None
    betsize: float = 0.0

    def __init__(self, strategy: [], evs: [], move: Move, position: Position, betsize: float):
        self.strategy = strategy
        self.evs = evs
        self.move = move
        self.position = position
        self.betsize = betsize
