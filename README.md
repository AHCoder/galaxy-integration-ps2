# PlayStation 2 Integration for GOG Galaxy 2.0
A PS2 integration for GOG Galaxy 2.0

## Features
* Looks for iso and gz files in a folder you specify
* Supports launching games with PCSX2
* Supports the usage of game specific settings

## Installation and Config

Download this repository, name it "ps2_1e814707-1fe3-4e1e-86fe-1b8d1b7fac2e" and put it in %LOCALAPPDATA%\GOG.com\Galaxy\plugins\installed

* You can choose to use the local PCSX2 database or the Giant Bomb database for pulling ids and game names
* Open user_config.py in your installation folder and set your folder path for your roms and your emulator path etc.

### Local Database variant

1. Place a empty file name "config.py" in your installation folder

### Giant Bomb variant

1. When you have an account go here: https://www.giantbomb.com/api/
2. Place a file named "config.py" in your installation folder with a single line:
    * api_key = YOUR_KEY_GOES_HERE_IN_QUOTES i.e. api_key = "abcdefghijklmnopqrstuvwxyz"
    
### Game specific settings

1. Create a folder named "configs" inside "Documents/PCSX2" (the folder containing your bios, savestates etc.).
2. Put the path to that folder into user_config.py and enable the feature by setting emu_config = True
3. To create settings for a game, copy the "inis" or "inis_1.4.0" folder into the "configs" folder and rename it to match the rom.
   Make sure that the renamed folders have the same name as the corresponding rom without the extension.
   eg. ROM: "Shadow of the Colossus.iso" | FOLDER: "Shadow of the Colossus"
   Without a specific config folder for a game, the default settings will be used.
