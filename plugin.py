import asyncio
import subprocess
import sys
import os

import user_config
from backend import BackendClient
from galaxy.api.consts import LicenseType, LocalGameState, Platform
from galaxy.api.plugin import Plugin, create_and_run_plugin
from galaxy.api.types import Authentication, Game, GameTime, LicenseInfo, LocalGame
from version import __version__

class PlayStation2Plugin(Plugin):
    def __init__(self, reader, writer, token):
        super().__init__(Platform.PlayStation2, __version__, reader, writer, token)
        self.backend_client = BackendClient()
        self.games = []
        self.local_games_cache = self.local_games_list()

        
    async def authenticate(self, stored_credentials=None):
        return self.do_auth()

        
    async def pass_login_credentials(self, step, credentials, cookies):
        return self.do_auth()


    def do_auth(self):
        user_data = {}
        username = user_config.roms_path
        user_data["username"] = username
        self.store_credentials(user_data)
        return Authentication("pcsx2_user", user_data["username"])


    async def launch_game(self, game_id):
        emu_path = user_config.emu_path
        no_gui = user_config.emu_no_gui
        fullscreen = user_config.emu_fullscreen
        config = user_config.emu_config
        config_folder = user_config.config_path

        for game in self.games:
            if str(game[1]) == game_id:
                rom_file = os.path.splitext(os.path.basename(game[0]))[0]
                config_folder_game = config_folder + "/" + rom_file
                if config and os.path.isdir(config_folder_game):
                    config_arg = '--cfgpath=' + config_folder + "/" + rom_file
                    if no_gui and fullscreen:
                        subprocess.Popen([emu_path, "--nogui", "--fullscreen", config_arg, game[0]])
                        break
                    if no_gui and not fullscreen:
                        subprocess.Popen([emu_path, "--nogui", config_arg, game[0]])
                        break
                    if not no_gui and fullscreen:
                        subprocess.Popen([emu_path, "--fullscreen", config_arg, game[0]])
                        break
                    subprocess.Popen([emu_path, config_arg, game[0]])
                    break
                else:
                    if no_gui and fullscreen:
                        subprocess.Popen([emu_path, "--nogui", "--fullscreen", game[0]])
                        break
                    if no_gui and not fullscreen:
                        subprocess.Popen([emu_path, "--nogui", game[0]])
                        break
                    if not no_gui and fullscreen:
                        subprocess.Popen([emu_path, "--fullscreen", game[0]])
                        break
                    subprocess.Popen([emu_path, game[0]])
                    break
        return

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

        # Get the directory of this file and format it to
        # have the path to the game times file
        base_dir = os.path.dirname(os.path.realpath(__file__))
        game_times_path = "{}/game_times.txt".format(base_dir)

        # Check if the file exists
        # If not create it with the default value of 0 minutes played
        if not os.path.exists(game_times_path):
            game_times_list = []
            for game in self.games:
                entry = {}
                entry["game_id"] = str(game[1])
                entry["name"] = game[2]
                entry["time_played"] = 0
                entry["last_time_played"] = 0
                game_times_list.append(entry)

            with open(game_times_path, "w") as game_times_file:
                game_times_file.write(str(game_times_list))

        # Once the file exists read it and return the game times    
        game_times = {}

        with open(game_times_path, "r") as game_times_file:
            parsed_game_times_file = eval(game_times_file.read())
            for entry in parsed_game_times_file:
                game_id = entry["game_id"]
                time_played = int(entry["time_played"])
                last_time_played = int(entry["last_time_played"])
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

        async def update_local_games():
            loop = asyncio.get_running_loop()
            new_local_games_list = await loop.run_in_executor(None, self.local_games_list)
            notify_list = self.backend_client.get_state_changes(self.local_games_cache, new_local_games_list)
            self.local_games_cache = new_local_games_list
            for local_game_notify in notify_list:
                self.update_local_game_status(local_game_notify)

        asyncio.create_task(update_local_games())


    async def get_owned_games(self):
        if(user_config.use_database):
            self.games = self.backend_client.get_games_db()
        else:
            self.games = self.backend_client.get_games_gb()
        owned_games = []
        
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
