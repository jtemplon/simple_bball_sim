import random
import csv
from models import *

"""This is a simple (quite silly actually) NBA sim based on a few principles"""
pos_to_player = {1: "pg", 2: "sg", 3: "sf", 4: "pf", 5: "c"}
pos_to_num = {"pg": 1, "sg": 2, "sf": 3, "pf": 4, "c": 5}

def shooting_sequence(player, team):
    shot_type_val = round(random.random()*100)
    shot_chance_val = round(random.random()*100)
    result = None
    if player.three_chance > shot_type_val:
        if player.three_point_pct > shot_chance_val:
            team.points += 3
            player.stats.points += 3
            player.stats.three_pt += 1
            player.stats.three_pt_att += 1
            result = "make"
        else:
            player.stats.three_pt_att += 1
            result = "miss"
    else:
        if player.two_point_pct > shot_chance_val:
            team.points += 2
            player.stats.points += 2
            player.stats.two_pt += 1
            player.stats.two_pt_att += 1
            result = "make"
        else:
            player.stats.two_pt_att += 1
            result = "miss"
    return result

def ft_rebounding_sequence(player, team):
    rebound_val = round(random.random()*100)
    #this is a little schematic to weight rebounding to right pos
    rebound_range = [1, 1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5]
    #this mechanic is slightly different because it should be harder to get your own rebound
    player_num = pos_to_num[player.position]
    offensive_rebound_range = rebound_range.remove(player_num)
    if rebound_val < 14:
        rebounder = random.choice(offensive_rebound_range)
        rebounding_pos = pos_to_player[rebounder]
        team.lineup[rebounding_pos].stats.oreb += 1
        controlling_team = team
    else:
        rebounder = random.choice(rebound_range)
        rebounding_pos = pos_to_player[rebounder]
        team.opponent.lineup[rebounding_pos].stats.dreb += 1
        controlling_team = team.opponent
    return controlling_team
    

def free_throw_sequence(player, team, event_type = None):
    shots = 0
    if event_type == "2pt":
        total_shots = 2
    elif event_type == "3pt":
        total_shots = 3
    elif event_type == "and_one":
        total_shots = 1
    else:
        total_shots = 2
    while total_shots > shots:
        shot_chance_val = round(random.random()*100)
        if shot_chance_val > player.ft_pct:
            team.points += 1
            player.stats.ft_att += 1
            player.stats.ft += 1
            shots += 1
            if shots == total_shots:
                controlling_team = team.opponent
            else:
                pass
        else:
            player.stats.ft_att += 1
            shots += 1
            if shots == total_shots:
                controlling_team = ft_rebounding_sequence(player, team)
            else:
                pass
    return controlling_team

def rebounding_sequence(team):
    rebound_val = round(random.random()*100)
    #this is a little schematic to weight rebounding to right pos
    rebound_range = [1, 1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5]
    rebounder = random.choice(rebound_range)
    rebounding_pos = pos_to_player[rebounder]
    if rebound_val < 26:
        team.lineup[rebounding_pos].stats.oreb += 1
        res = "oreb"
    else:
        team.opponent.lineup[rebounding_pos].stats.dreb += 1
        res = "dreb"
    return res
    
def run_possession(possessing_team, clock):
    passes = 1
    possessing_player = possessing_team.lineup["pg"]
    res = None
    while passes < 5:
        use_val = round(random.random()*100)
        if use_val < possessing_player.usage:
            res = shooting_sequence(possessing_player, possessing_team)
            break
        else:
            new_player_val = random.randint(1, 5)
            new_player_pos = pos_to_player[new_player_val]
            possessing_player = possessing_team.lineup[new_player_pos]
            passes += 1
    #hero ball time
    if passes == 5:
        use_val = round(random.random()*100)
        if use_val < (possessing_player.usage+10):
            res = shooting_sequence(possessing_player, possessing_team)
        elif use_val < 70:
            #These are tough 50/50 calls in the lane from hero-baller charging down it
            foul_val = round(random.random()*100)
            if foul_val < 50:
                possessing_player.stats.turnovers += 1
                possessing_player.stats.fouls += 1
                possessing_team = possessing_team.opponent
                possessing_team.fouls += 1
            else:
                possessing_team.opponent.fouls += 1
                if possessing_team.opponent.fouls > 4:
                    possessing_team = free_throw_sequence(possessing_player, possessing_team)
                else:
                    pass
        else:
            #turnover
            possessing_player.stats.turnovers += 1
            possessing_team = possessing_team.opponent
    #resolve the make or miss if there was a shot
    if res != None:
        if res == "make":
            possessing_team = possessing_team.opponent
        elif res == "miss":
            reb_res = rebounding_sequence(possessing_team)
            if reb_res == "oreb":
                pass
            elif reb_res == "dreb":
                possessing_team = possessing_team.opponent
            else:
                print "Received unknown rebound resolution"
        else:
            print "Received unknown resolution"
    #resolve the clock
    clock -= passes * 5
    return possessing_team, clock

#make teams
home = Team("Spurs")
away = Team("Heat")
home.opponent = away
away.opponent = home
teams = [home, away]

#make players
def make_players_from_data(team, path):    
    data = open(path, "r")
    reader = csv.reader(data)
    for r in reader:
        p = Player()
        p.last, p.first, p.position = r[0], r[1], r[2]
        p.usage, p.three_point_pct, p.two_point_pct, p.three_chance = int(r[3]), int(r[4]), int(r[5]), int(r[6])
        team.lineup[p.position] = p

make_players_from_data(home, "spurs.csv")
make_players_from_data(away, "heat.csv")

#print home.lineup
#print away.lineup

possessing_team = None
quarter = 1

#jump ball
jump_val = random.random()
if jump_val > 0.50:
    possessing_team = away
else:
    possessing_team = home

while quarter < 5:
    clock_seconds = 720
    while clock_seconds > 0:
        possessing_team, clock_seconds = run_possession(possessing_team, clock_seconds)
    home.fouls = 0
    away.fouls = 0
    home.quarter_points = home.points - home.running_points
    away.quarter_points = away.points - away.running_points
    home.running_points = home.points
    away.running_points = away.points
    home.points_by_quarter[quarter] = home.quarter_points
    away.points_by_quarter[quarter] = away.quarter_points
    quarter += 1

for t in teams:
    print t.name, t.points, t.points_by_quarter

for t in teams:
    for k in t.lineup.keys():
        p = t.lineup[k]
        print p.first, p.last, p.stats.__dict__