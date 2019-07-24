import asyncio
import json
import os
import subprocess
import sys
import urllib.parse, urllib.request

import config, user_config
from galaxy.api.plugin import Plugin, create_and_run_plugin
from galaxy.api.consts import Platform, LicenseType, LocalGameState
from galaxy.api.types import Authentication, Game, LocalGame, LicenseInfo, NextStep
from version import __version__

class PlayStation2Plugin(Plugin):
    def __init__(self, reader, writer, token):
        super().__init__(Platform.PlayStation2, __version__, reader, writer, token)
        self.games = []
        self.local_games_cache = self.local_games_list()

        
    async def authenticate(self, stored_credentials=None):
        return Authentication(user_id="userId", user_name="username")
        """
        username = None

        if stored_credentials:
            username = stored_credentials["username"]

        if username:
            return self.do_auth(username, store_username=False)
        else:
            username = user_config.roms_path
            PARAMS = {}
            return NextStep("web session", PARAMS)

        return self.do_auth(username, store_username=True)
        """

    """    
    async def pass_login_credentials(self, step, credentials, cookies):
        return self.do_auth(credentials["username"], store_username=False)
    
    def do_auth(self, username, store_username):
        if store_username:
            user_data = dict()
            user_data["username"] = username
            self.store_credentials(user_data)
        return Authentication(user_id="PCSX2 User", user_name=username)
    """

    async def launch_game(self, game_id):
        emu_path = user_config.emu_path
        no_gui = user_config.emu_no_gui
        fullscreen = user_config.emu_fullscreen
        
        for game in self.games:
            if str(game[1]) == game_id:
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

    async def install_game(self, game_id):
        pass

    async def uninstall_game(self, game_id):
        pass


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
            notify_list = get_state_changes(self.local_games_cache, new_local_games_list)
            self.local_games_cache = new_local_games_list
            for local_game_notify in notify_list:
                self.update_local_game_status(local_game_notify)

        asyncio.create_task(update_local_games())


    async def get_owned_games(self):
        self.games = get_games()
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



def get_games():
    # Use Giant Bomb api to search for roms (first result is used)
    # Only call for id and name, in json format, limited to 1 result
    query_url = "https://www.giantbomb.com/api/search/?api_key={}&field_list=id,name&format=json&limit=1&query={}&resources=game"
    paths = []
    results = []
    roms = []

    # Search through directory for iso or gz files (PS2 roms)
    for root, dirs, files in os.walk(user_config.roms_path):
        for file in files:
            if file.endswith(".iso") or file.endswith(".gz"):
                paths.append([os.path.join(root, file)])
                roms.append(os.path.splitext(os.path.basename(file))[0]) # Split name of file from it's path/extension

    # Retrieve the info for each iso/gz found
    for rom in roms:
        url = query_url.format(config.api_key, urllib.parse.quote(rom)) # Add in params to the above url
        response = urllib.request.urlopen(url)
        search_results = json.loads(response.read())
        results.append(
            [search_results["results"][0]["id"], search_results["results"][0]["name"]] # Add games in the form of list with id and name
        )

    for x,y in zip(paths, results):
        x.extend(y)

    return paths


def get_state_changes(old_list, new_list):
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


def main():
    create_and_run_plugin(PlayStation2Plugin, sys.argv)


# run plugin event loop
if __name__ == "__main__":
    main()