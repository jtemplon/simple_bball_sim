import random
import csv
from models import *

"""This is a simple (quite silly actually) NBA sim based on a few principles"""
pos_to_player = {1: "pg", 2: "sg", 3: "sf", 4: "pf", 5: "c"}

def shooting_sequence(player, team):
    shot_type_val = random.random()*100
    shot_chance_val = random.random()*100
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

def rebounding_sequence(team):
    rebound_val = random.random()*100
    #this is a little schematic to weight rebounding to right pos
    rebound_range = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5]
    rebounder = random.choice(rebound_range)
    rebounding_pos = pos_to_player[rebounder]
    if rebound_val < 25.5:
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
        use_val = random.random()*100
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
        use_val = random.random()*100
        if use_val < (possessing_player.usage+10):
            res = shooting_sequence(possessing_player, possessing_team)
        elif use_val < 0.50:
            #should be a foul on O or D
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

possessing_team = None
clock_seconds = 2880

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

print home.lineup
print away.lineup

#jump ball
jump_val = random.random()
if jump_val > 0.50:
    possessing_team = away
else:
    possessing_team = home

while clock_seconds > 0:
    possessing_team, clock_seconds = run_possession(possessing_team, clock_seconds)

for t in teams:
    print t.name, t.points

for t in teams:
    for k in t.lineup.keys():
        p = t.lineup[k]
        print p.first, p.last, p.stats.__dict__