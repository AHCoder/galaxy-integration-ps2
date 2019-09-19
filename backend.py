import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

import pycdlib
import user_config


class BackendClient:
    def __init__(self):
        self.paths = []
        self.results = []
        self.roms = []
        self.start_time = 0
        self.end_time = 0

    
    def _get_games_database(self) -> list:
        '''Returns a list of games with path, id, and name

        Used if the user chooses to pull from the PCSX2 games database
        by matching their files' names with the db
        '''
        database_records = self._parse_dbf()
        self._get_rom_names()

        for rom in self.roms:
            for record in database_records:
                if(rom == record[1].replace(":", "")):
                    self.results.append(
                        [
                            record[0],
                            record[1]
                        ]
                    )

        for x,y in zip(self.paths, self.results):
            x.extend(y)

        return self.paths


    def _parse_dbf(self) -> list:
        '''Returns a list of records in the PCSX2 database without duplicate names

        Use this when wanting to avoid duplicates (and when serial number isn't important)
        '''
        filename = os.path.expandvars(r"%LOCALAPPDATA%\GOG.com\Galaxy\plugins\installed\ps2_1e814707-1fe3-4e1e-86fe-1b8d1b7fac2e\GameIndex.txt")
        records = []
        serials = []
        names = []

        with open(filename, encoding="utf-8") as fh:                # Open GameIndex.txt
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

    def _parse_dbf_with_doubles(self) -> list:
        ''' Returns a list of records in the PCSX2 database
        
        Use this to get all serial-name pairs in the PCSX2 database irregardless whether the name is a duplicate
        '''
        filename = os.path.expandvars(r"%LOCALAPPDATA%\GOG.com\Galaxy\plugins\installed\ps2_1e814707-1fe3-4e1e-86fe-1b8d1b7fac2e\GameIndex.txt")       
        records = []
        serials = []
        names = []

        with open(filename, encoding="utf-8") as fh:                                 
            for line in fh:
                line = line.strip()                                
                if line.startswith("Name"):                 # Both checks here are removed, simply add the serial and name          
                    split_line = line.split("= ")
                    names.append(split_line[1])
                    serials.append(prev_line.split()[2])
                prev_line = line

        for serial, name in zip(serials, names):
            records.append([serial, name])

        return records

    
    def _get_games_giant_bomb(self) -> list:
        ''' Returns a list of games with path, id, and name

        Used if the user chooses to pull from Giant Bomb database
        The first result is used and only call for id and name, in json format, limited to 1 result
        '''
        query_url = "https://www.giantbomb.com/api/search/?api_key={}&field_list=id,name&format=json&limit=1&query={}&resources=game"
        self._get_rom_names()

        for rom in self.roms:
            url = query_url.format(user_config.api_key, urllib.parse.quote(rom))
            
            with urllib.request.urlopen(url) as response:
                search_results = json.loads(response.read())
                self.results.append(
                    [
                        search_results["results"][0]["id"],
                        search_results["results"][0]["name"]
                    ]
                )

        for x,y in zip(self.paths, self.results):
            x.extend(y)

        return self.paths


    def _get_games_read_iso(self) -> list:
        ''' Returns a list of games with path, id, and name

        Use this to read serials from iso's and match them to a name from the db
        '''
        database_records = self._parse_dbf_with_doubles()
        directory = user_config.roms_path
        iso = pycdlib.PyCdlib()
        serials = []

        # Get the serials by reading the iso's directly
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(".iso"):
                    try:
                        iso.open(os.path.join(root, file))
                        self.paths.append([os.path.join(root, file)])
                    except:
                        continue

                    for child in iso.list_children(iso_path='/'):
                        string = child.file_identifier().decode("utf-8")
                        if re.search(r"\w{4}_\d{3}\.\d{2}|$", string)[0]:
                            serials.append(string.replace("_", "-").replace(".", "").replace(";1", ""))
                            break
                    iso.close()

        # Match the serials to names
        for serial in serials:
            for record in database_records:
                if(serial == record[0]):
                    self.results.append(
                        [
                            record[0],
                            record[1]
                        ]
                    )

        for x,y in zip(self.paths, self.results):
            x.extend(y)

        return self.paths


    def _get_rom_names(self) -> None:
        ''' Returns none
        
        Appends the rom names and paths to their corresponding lists
        '''        
        for root, dirs, files in os.walk(user_config.roms_path):
            for file in files:
               if file.lower().endswith((".bin", ".gz", ".iso")):
                    self.paths.append([os.path.join(root, file)])
                    self.roms.append(os.path.splitext(os.path.basename(file))[0]) # Split name of file from it's path/extension


    def _get_state_changes(self, old_list, new_list) -> list:
        old_dict = {x.game_id: x.local_game_state for x in old_list}
        new_dict = {x.game_id: x.local_game_state for x in new_list}
        result = []
        # removed games
        result.extend(LocalGame(id, LocalGameState.None_) for id in old_dict.keys() - new_dict.keys())
        # added games
        result.extend(local_game for local_game in new_list if local_game.game_id in new_dict.keys() - old_dict.keys())
        # state changed
        result.extend(
            LocalGame(id, new_dict[id]) for id in new_dict.keys() & old_dict.keys() if new_dict[id] != old_dict[id]
            )
        return result


    def _set_session_start(self) -> None:
        ''' Sets the session start to the current time'''
        self.start_time = time.time()


    def _set_session_end(self) -> None:
        ''' Sets the session end to the current time'''
        self.end_time = time.time()


    def _get_session_duration(self) -> int:
        ''' Returns the duration of the game session in minutes as an int'''
        return int(round((self.end_time - self.start_time) / 60))
