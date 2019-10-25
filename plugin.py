import asyncio
import json
import os
import subprocess
import sys
import time

import config
from backend import AuthenticationServer
from galaxy.api.consts import LicenseType, LocalGameState, Platform
from galaxy.api.plugin import Plugin, create_and_run_plugin
from galaxy.api.types import (Authentication, Game, GameTime, LicenseInfo,
                              LocalGame, NextStep)
from PS2Client import PS2Client
from version import __version__


class PlayStation2Plugin(Plugin):
    def __init__(self, reader, writer, token):
        super().__init__(Platform.PlayStation2, __version__, reader, writer, token)
        self.config = config.Config()
        self.auth_server = AuthenticationServer()
        self.auth_server.start()
        self.games = []
        self.local_games_cache = []
        self.proc = None
        self.ps2_client = PS2Client(self)
        self.running_game_id = ""
        self.tick_count = 0


    def handshake_complete(self):
        self.create_task(self._update_local_games(), "Update local games")

        
    async def authenticate(self, stored_credentials=None):
        PARAMS = {
            "window_title": "Configure PS2 Integration",
            "window_width": 575,
            "window_height": 850,
            "start_uri": "http://localhost:" + str(self.auth_server.port),
            "end_uri_regex": ".*/end.*"
        }
        return NextStep("web_session", PARAMS)

        return self._do_auth()

        
    async def pass_login_credentials(self, step, credentials, cookies):
        return self._do_auth()


    def _do_auth(self) -> Authentication:
        user_data = {}
        self.config.cfg.read(os.path.expandvars(config.CONFIG_LOC))
        user_data["username"] = self.config.cfg.get("Paths", "roms_path")
        self.store_credentials(user_data)
        return Authentication("pcsx2_user", user_data["username"])


    async def launch_game(self, game_id):
        self.running_game_id = game_id
        self.config.cfg.read(os.path.expandvars(config.CONFIG_LOC))
        emu_path = self.config.cfg.get("Paths", "emu_path")
        config_folder = self.config.cfg.get("Paths", "config_path")
        fullscreen = self.config.cfg.getboolean("EmuSettings", "emu_fullscreen")
        no_gui = self.config.cfg.getboolean("EmuSettings", "emu_no_gui")
        config = self.config.cfg.getboolean("EmuSettings", "emu_config")

        self._launch_game(game_id, emu_path, no_gui, fullscreen, config, config_folder)
        self.ps2_client._set_session_start()


    def _launch_game(self, game_id, emu_path, no_gui, fullscreen, config, config_folder) -> None:
        ''' Returns None

        Interprets user configurated options and launches PCSX2 with the chosen rom
        '''
        for game in self.games:
            if game.id == game_id:
                rom_file = os.path.splitext(os.path.basename(game.path))[0]
                config_folder_game = config_folder + "/" + rom_file
                args = [emu_path]
                if config and os.path.isdir(config_folder_game):
                    config_arg = "--cfgpath=" + config_folder_game
                    args.append(config_arg)
                if fullscreen:
                    args.append("--fullscreen")
                if no_gui:
                    args.append("--nogui")
                if os.path.exists(os.path.join(config_folder_game, "fullboot.ini")):
                    args.append("--fullboot")
                args.append(game.path)
                self.proc = subprocess.Popen(args)
                break


    # Only as placeholders so the launch game feature is recognized
    async def install_game(self, game_id):
        pass

    async def uninstall_game(self, game_id):
        pass


    async def prepare_game_times_context(self, game_ids):
        return self._get_games_times_dict()

    
    async def get_game_time(self, game_id, context):
        game_time = context.get(game_id)
        return game_time


    def _get_games_times_dict(self) -> dict:
        ''' Returns a dict of GameTime objects
        
        Creates and reads the game_times.json file
        '''
        data = {}
        game_times = {}
        path = os.path.expandvars(r"%LOCALAPPDATA%\GOG.com\Galaxy\Configuration\plugins\ps2\game_times.json")
        
        # Check if the file exists, otherwise create it with defaults
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path))
            for game in self.games:
                data[game.id] = { "name": game.name, "time_played": 0, "last_time_played": None }

            with open(path, "w", encoding="utf-8") as game_times_file:
                json.dump(data, game_times_file, indent=4)
        
        # Now read it and return the game times
        with open(path, encoding="utf-8") as game_times_file:
            parsed_game_times_file = json.load(game_times_file)

        for entry in parsed_game_times_file:
            game_id = entry
            time_played = parsed_game_times_file.get(entry).get("time_played")
            last_time_played = parsed_game_times_file.get(entry).get("last_time_played")
            game_times[game_id] = GameTime(game_id, time_played, last_time_played)

        return game_times


    def _local_games_list(self) -> list:
        ''' Returns a list of LocalGame objects

        Goes through retrieved games and adds them as local games with default state of "Installed"
        '''
        local_games = []        
        for game in self.games:
            state = LocalGameState.Installed
            if self.running_game_id == game.id:
                state |= LocalGameState.Running

            local_games.append(
                LocalGame(
                    game.id,
                    state
                )
            )
        return local_games


    def tick(self):
        self._check_emu_status()
        self.create_task(self._update_local_games(), "Update local games")
        self.tick_count += 1

        if self.tick_count % 10 == 0:
            self.create_task(self._update_all_game_times(), "Update all game times")


    def _check_emu_status(self) -> None:
        try:
            if(self.proc.poll() is not None):
                self.ps2_client._set_session_end()
                session_duration = self.ps2_client._get_session_duration()
                last_time_played = int(time.time())
                self._update_game_time(self.running_game_id, session_duration, last_time_played)
                self.proc = None
        except AttributeError:
            pass


    async def _update_local_games(self) -> None:
        loop = asyncio.get_running_loop()
        new_list = await loop.run_in_executor(None, self._local_games_list)
        notify_list = self.ps2_client._get_state_changes(self.local_games_cache, new_list)
        self.local_games_cache = new_list
        for local_game_notify in notify_list:
            self.update_local_game_status(local_game_notify)


    async def _update_all_game_times(self) -> None:
        await asyncio.sleep(60) # Leave time for Galaxy to fetch games before updating times
        loop = asyncio.get_running_loop()
        new_game_times = await loop.run_in_executor(None, self._get_games_times_dict)
        for game_time in new_game_times:
            self.update_game_time(new_game_times[game_time])


    def _update_game_time(self, game_id, session_duration, last_time_played) -> None:
        ''' Returns None 
        
        Update the game time of a single game
        '''
        path = os.path.expandvars(r"%LOCALAPPDATA%\GOG.com\Galaxy\Configuration\plugins\ps2\game_times.json")

        with open(path, encoding="utf-8") as game_times_file:
            data = json.load(game_times_file)

        data[game_id]["time_played"] = data.get(game_id).get("time_played") + session_duration
        data[game_id]["last_time_played"] = last_time_played

        with open(path, "w", encoding="utf-8") as game_times_file:
            json.dump(data, game_times_file, indent=4)

        self.update_game_time(GameTime(game_id, data.get(game_id).get("time_played"), last_time_played))


    async def get_owned_games(self):
        self.config.cfg.read(os.path.expandvars(config.CONFIG_LOC))
        method = self.config.cfg.get("Method", "method")
        owned_games = []
        
        if(method == "default"):
            self.games = self.ps2_client._get_games_database()
        elif(method == "giant"):
            self.games = self.ps2_client._get_games_giant_bomb()
        else:
            self.games = self.ps2_client._get_games_read_iso()
        
        for game in self.games:
            owned_games.append(
                Game(
                    game.id,
                    game.name,
                    None,
                    LicenseInfo(LicenseType.SinglePurchase, None)
                )
            )   
        return owned_games

    async def get_local_games(self):
        return self.local_games_cache

    async def shutdown(self):
        self.auth_server.httpd.shutdown()


def main():
    create_and_run_plugin(PlayStation2Plugin, sys.argv)


# run plugin event loop
if __name__ == "__main__":
    main()
