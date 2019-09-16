import asyncio
import json
import os
import subprocess
import sys
import time

import user_config
from backend import BackendClient
from galaxy.api.consts import LicenseType, LocalGameState, Platform
from galaxy.api.plugin import Plugin, create_and_run_plugin
from galaxy.api.types import (Authentication, Game, GameTime, LicenseInfo,
                              LocalGame)
from version import __version__


class PlayStation2Plugin(Plugin):
    def __init__(self, reader, writer, token):
        super().__init__(Platform.PlayStation2, __version__, reader, writer, token)

        self.backend_client = BackendClient()
        self.games = []
        self.local_games_cache = []

        self.running_game_id = ""
        self.proc = None

        self.create_task(self._update_local_games(), "Update local games")

        
    async def authenticate(self, stored_credentials=None):
        return self._do_auth()

        
    async def pass_login_credentials(self, step, credentials, cookies):
        return self._do_auth()


    def _do_auth(self):
        user_data = {}
        username = user_config.roms_path
        user_data["username"] = username
        self.store_credentials(user_data)
        return Authentication("pcsx2_user", user_data["username"])


    async def launch_game(self, game_id):
        self.running_game_id = game_id
        emu_path = user_config.emu_path
        no_gui = user_config.emu_no_gui
        fullscreen = user_config.emu_fullscreen
        config = user_config.emu_config
        config_folder = user_config.config_path

        self._launch_game(game_id, emu_path, no_gui, fullscreen, config, config_folder)
        self.backend_client._set_session_start()


    def _launch_game(self, game_id, emu_path, no_gui, fullscreen, config, config_folder):

        for game in self.games:
            if str(game[1]) == game_id:
                rom_file = os.path.splitext(os.path.basename(game[0]))[0]
                config_folder_game = config_folder + "/" + rom_file
                if config and os.path.isdir(config_folder_game):
                    config_arg = '--cfgpath=' + config_folder + "/" + rom_file
                    if no_gui and fullscreen:
                        self.proc = subprocess.Popen([emu_path, "--nogui", "--fullscreen", config_arg, game[0]])
                        break
                    if no_gui and not fullscreen:
                        self.proc = subprocess.Popen([emu_path, "--nogui", config_arg, game[0]])
                        break
                    if not no_gui and fullscreen:
                        self.proc = subprocess.Popen([emu_path, "--fullscreen", config_arg, game[0]])
                        break
                    self.proc = subprocess.Popen([emu_path, config_arg, game[0]])
                    break
                else:
                    if no_gui and fullscreen:
                        self.proc = subprocess.Popen([emu_path, "--nogui", "--fullscreen", game[0]])
                        break
                    if no_gui and not fullscreen:
                        self.proc = subprocess.Popen([emu_path, "--nogui", game[0]])
                        break
                    if not no_gui and fullscreen:
                        self.proc = subprocess.Popen([emu_path, "--fullscreen", game[0]])
                        break
                    self.proc = subprocess.Popen([emu_path, game[0]])
                    break

    # Only as placeholders so the feature is recognized
    async def install_game(self, game_id):
        pass

    async def uninstall_game(self, game_id):
        pass


    async def prepare_game_times_context(self, game_ids):
        return self.get_games_times_dict()

    
    async def get_game_time(self, game_id, context):
        game_time = context.get(game_id)
        return game_time


    def get_games_times_dict(self):
        '''
        Get the directory of this file and format it to
        have the path to the game times file
        '''
        base_dir = os.path.dirname(os.path.realpath(__file__))
        game_times_path = "{}/game_times.json".format(base_dir)

        '''
        Check if the file exists
        If not create it with the default value of 0 minutes played
        '''
        if not os.path.exists(game_times_path):
            game_times_dict = {}
            for game in self.games:
                entry = {}
                id = str(game[1])
                entry["name"] = game[2]
                entry["time_played"] = 0
                entry["last_time_played"] = 0
                game_times_dict[id] = entry

            with open(game_times_path, "w", encoding="utf-8") as game_times_file:
                json.dump(game_times_dict, game_times_file, indent=4)

        # Once the file exists read it and return the game times    
        game_times = {}

        with open(game_times_path, encoding="utf-8") as game_times_file:
            parsed_game_times_file = json.load(game_times_file)
            for entry in parsed_game_times_file:
                game_id = entry
                time_played = int(parsed_game_times_file.get(entry).get("time_played"))
                last_time_played = int(parsed_game_times_file.get(entry).get("last_time_played"))
                game_times[game_id] = GameTime(
                    game_id,
                    time_played,
                    last_time_played
                )

        return game_times


    def local_games_list(self):
        local_games = []
        for game in self.games:
            local_games.append(
                LocalGame(
                    str(game[1]),
                    LocalGameState.Installed
                )
            )
        return local_games


    def tick(self):
        try:
            if(self.proc.poll() is not None):
                self.backend_client._set_session_end()
                session_duration = self.backend_client._get_session_duration()
                last_time_played = int(time.time())
                self._update_game_time(self.running_game_id, session_duration, last_time_played)
                self.proc = None
        except AttributeError:
            pass

        self.create_task(self._update_local_games(), "Update local games")
        self._update_all_game_times()

    async def _update_local_games(self):
        loop = asyncio.get_running_loop()
        new_list = await loop.run_in_executor(None, self.local_games_list)
        notify_list = self.backend_client.get_state_changes(self.local_games_cache, new_list)
        self.local_games_cache = new_list
        for local_game_notify in notify_list:
            self.update_local_game_status(local_game_notify)

    async def _update_all_game_times(self):
        #loop = asyncio.get_running_loop()
        new_game_times = self.get_games_times_dict()
        for game_time in new_game_times:
            self.update_game_time(game_time)


    def _update_game_time(self, game_id, session_duration, last_time_played):
        ''' Update the game time of a single game '''
        base_dir = os.path.dirname(os.path.realpath(__file__))
        game_times_path = "{}/game_times.json".format(base_dir)

        with open(game_times_path, encoding="utf-8") as game_times_file:
            data = json.load(game_times_file)

        data[game_id]["time_played"] = data.get(game_id).get("time_played") + session_duration
        data[game_id]["last_time_played"] = last_time_played

        with open(game_times_path, "w", encoding="utf-8") as game_times_file:
            json.dump(data, game_times_file, indent=4)

        self.update_game_time(GameTime(game_id, data.get(game_id).get("time_played"), last_time_played))


    async def get_owned_games(self):
        method = user_config.method
        owned_games = []
        
        if(method == "default"):
            self.games = self.backend_client.get_games_database()
        elif(method == "giant"):
            self.games = self.backend_client.get_games_giant_bomb()
        else:
            self.games = self.backend_client.get_games_read_iso()
        
        for game in self.games:
            owned_games.append(
                Game(
                    str(game[1]),
                    game[2],
                    None,
                    LicenseInfo(LicenseType.SinglePurchase, None)
                )
            )
            
        return owned_games

    async def get_local_games(self):
        return self.local_games_cache


def main():
    create_and_run_plugin(PlayStation2Plugin, sys.argv)


# run plugin event loop
if __name__ == "__main__":
    main()
