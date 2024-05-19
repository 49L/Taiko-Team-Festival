import yadon
import json

players = []
overallrankings = yadon.ReadTable("overall")
users = yadon.ReadTable("users", named_columns=True)
maprankings = {}
mappool = yadon.ReadTable("mappool")
for id in mappool.keys():
    pick = mappool[id][0]
    pickrankings = yadon.ReadTable(pick) or {}
    maprankings[pick] = pickrankings

for seed in overallrankings.keys():
    username, avgrank, scoresum = overallrankings[seed]
    player = {"Name": username, "Seed": int(seed), "Map seeds": [], "Time zone": 0}
    for pick in maprankings.keys():
        pickrankings = maprankings[pick]
        for mapseed in pickrankings.keys():
            username2, score = pickrankings[mapseed]
            if username2 == username:
                player["Map seeds"].append(int(float(mapseed)))
                break
    
    for userid in users.keys():
        values = users[userid]
        if values["username"] == username:
            player["Time zone"] = int(values["timezone"]) if values["timezone"] else 0
            break
    players.append(player)

output = {"Players": players}
outputfile = open("ttf.json", "w")
outputfile.write(json.dumps(output))