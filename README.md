# PlayStation 2 Integration for GOG Galaxy 2.0
A PS2 integration for GOG Galaxy 2.0

## Features
* Looks for bin, gz, and iso files in a folder you specify
* Supports launching games with PCSX2
* Supports the usage of game specific settings
* Supports manually editing time played, and game time tracking

## Installation and Config

Index               | Location
------------------- | --------
Installation folder | %LOCALAPPDATA%\GOG.com\Galaxy\plugins\installed
Game times file     | %LOCALAPPDATA%\GOG.com\Galaxy\Configuration\plugins\ps2\games_times.json
Config file         | %LOCALAPPDATA%\GOG.com\Galaxy\Configuration\plugins\ps2\config.ini

1. Download this repository, extract the folder from the zip, name it "ps2_1e814707-1fe3-4e1e-86fe-1b8d1b7fac2e" and put it in the installation folder

2. Decide whether to use the local PCSX2 database (default), the Giant Bomb API (requires an account) or reading your iso files directly for pulling ids and game names

    #### Local PCSX2 database method

    1. Name all your files exactly as they are in the database (it's stored in the installation folder as GameIndex.txt)
    2. If the name of the game has a ":" simply leave it out of your file name
    
    #### Giant Bomb method

    1. When you have an account go here: https://www.giantbomb.com/api/
    2. Set your API key at the authentication prompt when you connect the plugin (don't share this key with anyone)

3. Connect the integration within Galaxy
    
### Game specific settings

1. Create a folder named "configs" inside "Documents/PCSX2" (the folder containing your bios, savestates etc.).
2. Set the path to that folder at the authentication prompt and enable the feature by ticking per-game config
3. To create settings for a game, copy the "inis" or "inis_1.4.0" folder into the "configs" folder and rename it to match the rom.
   Make sure that the renamed folders have the same name as the corresponding rom without the extension.
   e.g. ROM: "Shadow of the Colossus.iso" | FOLDER: "Shadow of the Colossus"
   Without a specific config folder for a game, the default settings will be used.

### Game time
Adding game time manually is supported through editing

1. Open your installation folder after connecting the plugin and your games are added
2. Open the game times file, find the name of the game you want to edit and change the field time_played to what you want (in minutes)

Note:
The plugin tracks the PCSX2 process that is launched when you click on "play",
so only launch your roms from within Galaxy. Starting a game and then choosing another rom
from within PCSX2 itself will continue tracking game time for the first game.
   