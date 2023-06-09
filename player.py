class Player:
    def __init__(self, chips, bb_sum, name, position):
        self.bb = round(chips * 2 / bb_sum, 0) / 2
        self.hero = name == "HitBox"
        self.position = position
