# PlayStation 2 Integration for GOG Galaxy 2.0
A PS2 integration for GOG Galaxy 2.0

## Features
* Looks for iso and gz files in a folder you specify
* Supports launching games with PCSX2

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
