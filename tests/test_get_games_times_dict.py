import json
import os

from galaxy.api.types import GameTime

self_games = [
    ["", "id1", "name1"],
    ["", "id2", "name2"]
]

# Get the directory of this file and format it to
# have the path to the game times file
base_dir = os.path.dirname(os.path.realpath(__file__))
game_times_path = "{}/game_times.json".format(base_dir)

print(game_times_path)

# Check if the file exists
# If not create it with the default value of 0 minutes played
if not os.path.exists(game_times_path):
    game_times_dict = {}
    for game in self_games:
        entry = {}
        id = str(game[1])
        entry["name"] = game[2]
        entry["time_played"] = 0
        entry["last_time_played"] = 0
        game_times_dict[id] = entry

    print(game_times_dict)

    with open(game_times_path, "w") as game_times_file:
        json.dump(game_times_dict, game_times_file, indent=4)

# Once the file exists read it and return the game times    
game_times = {}

with open(game_times_path, "r") as game_times_file:
    parsed_game_times_file = json.load(game_times_file)
    print(parsed_game_times_file)
    for entry in parsed_game_times_file:
        game_id = entry
        time_played = int(parsed_game_times_file.get(entry).get("time_played"))
        last_time_played = int(parsed_game_times_file.get(entry).get("last_time_played"))
        print(game_id)
        print(time_played)
        print(last_time_played)
        game_times[game_id] = GameTime(
            game_id,
            time_played,
            last_time_played
        )

print(game_times)