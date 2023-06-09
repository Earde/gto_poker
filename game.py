from player import Player
from position import Position


class Game:
    def __init__(self, players: [Player], table_name: str, ante: float, sb, bb):
        self.players = players
        self.table_name = table_name
        self.ante = ante
        self.sb = sb
        self.bb = bb

    def has_ante(self) -> bool:
        return self.ante > 0

    def get_effective_bb(self, hero: Player, dealer_fold: bool) -> float:
        max_bb = max([p.bb for p in self.players if p.hero is False])
        if hero.bb < max_bb:
            max_bb = hero.bb
        if hero.position != Position.DEALER and dealer_fold:
            max_bb_without_dealer = max([p.bb for p in self.players if p.position != Position.DEALER])
            if max_bb_without_dealer < max_bb:
                return max_bb_without_dealer
        return max_bb

    def get_hero(self) -> Player:
        hero = [p for p in self.players if p.hero]
        if len(hero) <= 0:
            return None
        return hero[0]

    def print(self):
        hero = self.get_hero()
        if hero is None:
            return
        print(f"Table name: {self.table_name}")
        print(f"Position: {hero.position}")
        print(f"Effective bb: {self.get_effective_bb(hero=hero, dealer_fold=False)}")
        print(f"Effective bb without dealer: {self.get_effective_bb(hero=hero, dealer_fold=True)}")
        if self.has_ante():
            print(f"With ante")
