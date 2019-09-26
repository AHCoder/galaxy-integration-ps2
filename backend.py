import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

import pycdlib
import user_config
from definitions import PS2Game


class BackendClient:
    def __init__(self):
        self.games = []
        self.roms = {}
        self.start_time = 0
        self.end_time = 0

    
    def _get_games_database(self) -> list:
        ''' Returns a list of PS2Game objects with id, name, and path

        Used if the user chooses to pull from the PCSX2 games database
        by matching their files' names with the db
        '''
        database_records = self._parse_dbf(False)
        self._get_rom_names()

        for rom in self.roms:
            for key in database_records:
                if(rom == database_records.get(key).replace(":", "")):
                    self.games.append(
                        PS2Game(
                            str(key),
                            str(database_records.get(key)),
                            str(self.roms.get(rom))
                        )
                    )

        return self.games

    
    def _get_games_giant_bomb(self) -> list:
        ''' Returns a list of PS2Game objects with id, name, and path

        Used if the user chooses to pull from Giant Bomb database
        The first result is used and only call for id and name, in json format, limited to 1 result
        '''
        query_url = "https://www.giantbomb.com/api/search/?api_key={}&field_list=id,name&format=json&limit=1&query={}&resources=game"
        self._get_rom_names()

        for rom in self.roms:
            url = query_url.format(user_config.api_key, urllib.parse.quote(rom))
            
            with urllib.request.urlopen(url) as response:
                search_results = json.loads(response.read())
                self.games.append(
                    PS2Game(
                        str(search_results["results"][0]["id"]),
                        str(search_results["results"][0]["name"]),
                        str(self.roms.get(rom))
                    )
                )

        return self.games


    def _get_games_read_iso(self) -> list:
        ''' Returns a list of PS2Game objects with id, name, and path

        Use this to read serials from iso's and match them to a name from the db
        '''
        database_records = self._parse_dbf(True)
        iso = pycdlib.PyCdlib()

        # Get the serials by reading the iso's directly
        for root, dirs, files in os.walk(user_config.roms_path):
            for file in files:
                if file.lower().endswith(".iso"):
                    path = os.path.join(root, file)
                    try:
                        iso.open(path)
                    except:
                        continue

                    for child in iso.list_children(iso_path='/'):
                        string = child.file_identifier().decode("utf-8")
                        if re.search(r"\w{4}_\d{3}\.\d{2}|$", string)[0]:
                            parsed_serial = string.replace("_", "-").replace(".", "").replace(";1", "")
                            self.games.append(
                                PS2Game(
                                    str(parsed_serial),
                                    "",
                                    str(path)
                                )
                            )
                            break
                    iso.close()

        # Match the serials to names
        for game in self.games:
            for key in database_records:
                if(game.id == key):
                    game.name = str(database_records.get(key))

        return self.games


    def _get_rom_names(self) -> None:
        ''' Returns none
        
        Appends the rom names and paths to their corresponding lists
        '''        
        for root, dirs, files in os.walk(user_config.roms_path):
            for file in files:
               if file.lower().endswith((".bin", ".gz", ".iso")):
                    name = os.path.splitext(os.path.basename(file))[0] # Split name of file from it's path/extension
                    path = os.path.join(root, file)
                    self.roms[name] = path


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


    def _parse_dbf(self, allow_dups) -> dict:
        '''Returns a dictionary of records in the PCSX2 database

        :param allow_dups: allow duplicate names or not

        Use this to parse the PCSX2 database as a dictionary of records
        '''
        filename = os.path.expandvars(r"%LOCALAPPDATA%\GOG.com\Galaxy\plugins\installed\ps2_1e814707-1fe3-4e1e-86fe-1b8d1b7fac2e\GameIndex.txt")
        records = {}

        with open(filename, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line.startswith("Name"):
                    split_line = line.split("= ") # Split the line into "Name" and the name of the game
                    if(allow_dups or split_line[1] not in records.values()):
                        serial = prev_line.split()[2]
                        name = split_line[1]
                        records[serial] = name
                prev_line = line

        return records


    def _set_session_start(self) -> None:
        ''' Sets the session start to the current time'''
        self.start_time = time.time()


    def _set_session_end(self) -> None:
        ''' Sets the session end to the current time'''
        self.end_time = time.time()


    def _get_session_duration(self) -> int:
        ''' Returns the duration of the game session in minutes as an int'''
        return int(round((self.end_time - self.start_time) / 60))
