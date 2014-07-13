import random

class Team:
    
    def __init__(self,name):
        self.name = name
        self.lineup = {"pg": None, "sg": None, "sf": None,
                 "pf": None, "c": None}
        self.points = 0
        self.running_points = 0
        self.fouls = 0
        self.points_by_quarter = {}

class Stats:
    
    def __init__(self):
        self.points = 0
        self.three_pt_att = 0
        self.three_pt = 0
        self.two_pt_att = 0
        self.two_pt = 0
        self.turnovers = 0
        self.fouls = 0
        self.ft_att = 0
        self.ft = 0
        self.oreb = 0
        self.dreb = 0
    
    def total_reb(self):
        self.treb = self.oreb + self.dreb

class Player:
    
    def __init__(self):
        self.first = random.choice(["Jim", "Bob", "John", "Alan", "Tim", "Jack"])
        self.last = random.choice(["Smith", "Bryant", "Duncan", "Kurt", "James"])
        self.position = None
        self.usage = random.randrange(10, 30, 1)
        self.three_point_pct = random.randrange(0, 45, 1)
        self.two_point_pct = random.randrange(35, 70, 1)
        self.three_chance = random.randrange(0, 40, 1)
        self.ft_pct = random.randrange(60, 80, 1)
        self.stats = Stats()