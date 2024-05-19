from random import randint, sample
from copy import deepcopy
import json

#Parameters used by the program
NB_PLAYERS = 128
NB_MAPS = 8
NB_SEEDS = 4

#Class representing a player
class Player :
    
    def __init__(self, name, seed, map_seeds, timezone) :
        self.name = name
        self.seed = seed
        self.map_seeds = map_seeds
        self.timezone = timezone

#Class representing a team (stores the list of players)
#Team.metric is the metric used by the balancing algorithm ; the metric is always positive and a metric of 0.0 is a perfectly balanced team (higher metric => less balanced)
#Team.metric can be any function with the team as its only argument satisfying the above conditions
class Team :
    
    def __init__(self, players) :
        self.players = players

    #This metric uses two values in equal proportions
    #Sum of the squares of the differences between the sum of seeds and the mean seeding value
    #Square of the difference between the sum of seeds on every map and the mean seeding value
    def team_seed_and_mean_distance(self) :
        distance = 0
        #Configure weighting of different seeds. Lower seeds are multiplied by a higher number because a good D seed relative to other D seeds has more impact than A seeds.
        seed_readjustment = [1.0, 1.0, 1.1, 1.2]
        mean = sum((NB_PLAYERS/NB_SEEDS * (2*i + 1)/2 + 1/2) * seed_readjustment[i] for i in range(NB_SEEDS))
        seed_total = 0
        for i in range(NB_MAPS) :
            seed_total_map = 0
            for player in self.players :
                seed_total_map += player.map_seeds[i] * seed_readjustment[(player.seed-1)//(NB_PLAYERS//NB_SEEDS)]
            distance += (seed_total_map - mean) ** 2
            seed_total += seed_total_map
        distance += (seed_total - mean * NB_MAPS) ** 2 * NB_MAPS
        return distance
    
    #Compute total time zone difference value for the team
    def team_timezone(team) :
        timezone = 0
        for i in range(NB_SEEDS - 1) :
            for j in range(i+1, NB_SEEDS) :
                timezone += abs(team.players[i].timezone - team.players[j].timezone)
        return timezone
    
    metric = team_seed_and_mean_distance
    timezone = team_timezone

#Parses the qualifier results file into data usable by this prgram
def open_qualifiers_file() :
    players = []
    with open("egts2022.json", encoding = 'utf-8') as file :
        data = json.load(file)
        i = 0
        for player in data["Players"] :
            name = player["Name"]
            seed = player["Seed"]
            map_seeds = player["Map seeds"]
            timezone = player["Time zone"]
            players.append(Player(name, seed, map_seeds, timezone))
            i += 1
    return players

#Create teams based off player seedings
def create_teams(players) :
    
    nb_teams = NB_PLAYERS // NB_SEEDS
    teams = [[] for i in range(nb_teams)]
    for i in range(NB_SEEDS) :
        for j in range(nb_teams) :
            index = j if i%2 == 0 else nb_teams - j - 1
            teams[index].append(players[nb_teams*i + j])
    return [Team(teams[i]) for i in range(nb_teams)]
    

#Swap players to reduce the metric of all teams until no swap can be performed
def balance_teams(teams) :
    
    #Check the player swap that reduces both metrics the most ; returns True if a swap was performed
    def check_swap(team_1, team_2) :
        
        #Swaps the players at index on both teams
        def swap(team_1, team_2, index) :
            
            team_1.players[index], team_2.players[index] = team_2.players[index], team_1.players[index]

            
        nb_players = len(team_1.players)
        distance = team_1.metric() + team_2.metric()
        index = -1
        for i in range(nb_players) :
            swap(team_1, team_2, i)
            if i != 0 :
                swap(team_1, team_2, i-1)
            new_distance = team_1.metric() + team_2.metric()
            if distance > new_distance :
                distance = new_distance
                index = i
        swap(team_1, team_2, nb_players - 1)
        if index != -1 :
            swap(team_1, team_2, index)
            return True
        return False

    
    nb_teams = NB_PLAYERS // NB_SEEDS
    swap = True
    while swap :
        swap = False
        for i in range(nb_teams - 1) :
            for j in range(i + 1, nb_teams) :
                swap = swap or check_swap(teams[i], teams[j])


#Swap players to reduce the time zone difference of all teams while keeping good metric until no swap can be performed
def balance_teams_timezone(teams, rate) :

    #Check the player swap that reduces time zone the most while keeping good metric ; returns True if a swap was performed
    def check_swap(team_1, team_2) :
        
        #Swaps the players at index on both teams
        def swap(team_1, team_2, index) :
            
            team_1.players[index], team_2.players[index] = team_2.players[index], team_1.players[index]

            
        nb_players = len(team_1.players)
        distance = team_1.metric() + team_2.metric()
        distance_timezone = team_1.timezone() + team_2.timezone()
        index = -1
        for i in range(nb_players) :
            swap(team_1, team_2, i)
            if i != 0 :
                swap(team_1, team_2, i-1)
            new_distance = team_1.metric() + team_2.metric()
            new_distance_timezone = team_1.timezone() + team_2.timezone()
            if  distance_timezone > new_distance_timezone and distance * rate > new_distance :
                distance = new_distance
                distance_timezone = new_distance_timezone
                index = i
        swap(team_1, team_2, nb_players - 1)
        if index != -1 :
            swap(team_1, team_2, index)
            return True
        return False

    
    nb_teams = NB_PLAYERS // NB_SEEDS
    swap = True
    while swap :
        swap = False
        for i in range(nb_teams - 1) :
            for j in range(i + 1, nb_teams) :
                swap = swap or check_swap(teams[i], teams[j])

#Find the best rate between 1% and 20% to balance teams according to metric and timezone
def compute_best_metric_and_timezone(teams) :
    best_metric = sum(team.metric() for team in teams)
    best_timezone = sum(team.timezone() for team in teams)
    for i in range (1, 21) :
        rate = 1 + 0.01 * i
        new_teams = deepcopy(teams)
        balance_teams_timezone(new_teams, rate)
        new_metric = sum(team.metric() for team in new_teams)
        new_timezone = sum(team.timezone() for team in new_teams)
        diff_metric = abs(best_metric - new_metric)
        diff_timezone = abs(best_timezone - new_timezone)
        if diff_timezone != 0 and diff_metric / diff_timezone < 50 : 
            balance_teams_timezone(teams, rate)
            best_metric = sum(team.metric() for team in teams)
            best_timezone = sum(team.timezone() for team in teams)

#Print players and metrics of all teams
def print_team_metrics(teams) :
    
    for team in teams :
        print([player.name for player in team.players], [player.seed for player in team.players], round(team.metric(),2), team.timezone())
    print("Metric total: " + str(round(sum(team.metric() for team in teams),2)))
    print("Time zone total: " + str(sum(team.timezone() for team in teams)))

#=========================================Main program=========================================
players = open_qualifiers_file()
teams = create_teams(players)
balance_teams(teams)
print("====Team balance before time zone consideration====")
print_team_metrics(teams)
compute_best_metric_and_timezone(teams)
print("\n====Team balance after time zone consideration====")
print_team_metrics(teams)