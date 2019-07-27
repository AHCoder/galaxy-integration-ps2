import json
import os
import sys
import urllib.parse, urllib.request

import config, user_config

class BackendClient:
    def __init__(self):
        self.paths = []
        self.results = []
        self.roms = []

    
    # Used if the user chooses to pull from the PCSX2 games database
    def get_games_db(self):
        database_records = self.parse_dbf()

        self.get_rom_names()

        for rom in self.roms:
            for record in database_records:
                if(rom == record[1]):
                    self.results.append(
                        [record[0], record[1]]
                    )

        for x,y in zip(self.paths, self.results):
            x.extend(y)

        return self.paths


    def parse_dbf(self):
        filename = os.path.expandvars(r"%LOCALAPPDATA%\GOG.com\Galaxy\plugins\installed\ps2\GameIndex.txt")
        
        records = []
        serials = []
        names = []
        with open(filename) as fh:                                  # Open GameIndex.txt
            for line in fh:
                line = line.strip()                                 # For each line
                if line.startswith("Name"):                         # check if it starts with "Name"
                    split_line = line.split("= ")                   # Split the line into "Name" and the name of the game
                    if(split_line[1] not in names):                 # If the name isn't already in the list,
                        names.append(split_line[1])                 # add it
                        if prev_line.startswith("Serial"):          # Check if the line before started with "Serial"
                            serials.append(prev_line.split()[2])    # Only then add the corresponding serial
                prev_line = line

        for serial, name in zip(serials, names):
            records.append([serial, name])

        return records


    # Used if the user chooses to pull from Giant Bomb database
    # More potential here if GOG allows us to pull images etc.
    def get_games_gb(self):
        # Use Giant Bomb api to search for roms (first result is used)
        # Only call for id and name, in json format, limited to 1 result
        query_url = "https://www.giantbomb.com/api/search/?api_key={}&field_list=id,name&format=json&limit=1&query={}&resources=game"

        self.get_rom_names()

        # Retrieve the info for each iso/gz found
        for rom in self.roms:
            url = query_url.format(config.api_key, urllib.parse.quote(rom)) # Add in params to the above url
            response = urllib.request.urlopen(url)
            search_results = json.loads(response.read())
            self.results.append(
                [search_results["results"][0]["id"], search_results["results"][0]["name"]] # Add games in the form of list with id and name
            )

        for x,y in zip(self.paths, self.results):
            x.extend(y)

        return self.paths


    def get_rom_names(self):
        # Search through directory for iso or gz files (PS2 roms)
        for root, dirs, files in os.walk(user_config.roms_path):
            for file in files:
               if file.endswith(".iso") or file.endswith(".gz"):
                    self.paths.append([os.path.join(root, file)])
                    self.roms.append(os.path.splitext(os.path.basename(file))[0]) # Split name of file from it's path/extension


    def get_state_changes(self, old_list, new_list):
        old_dict = {x.game_id: x.local_game_state for x in old_list}
        new_dict = {x.game_id: x.local_game_state for x in new_list}
        result = []
        # removed games
        result.extend(LocalGame(id, LocalGameState.None_) for id in old_dict.keys() - new_dict.keys())
        # added games
        result.extend(local_game for local_game in new_list if local_game.game_id in new_dict.keys() - old_dict.keys())
        # state changed
        result.extend(LocalGame(id, new_dict[id]) for id in new_dict.keys() & old_dict.keys() if new_dict[id] != old_dict[id])
        return result