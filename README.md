# PlayStation 2 Integration for GOG Galaxy 2.0
A PS2 integration for GOG Galaxy 2.0

## Requirements
### A Giant Bomb account
* This is needed for the api key that makes the calls to the Giant Bomb database (for game ids and names)

## Features
* Looks for iso and gz files in a folder you specify
* Supports launching games with PCSX2

## Config
1. When you have an account go here: https://www.giantbomb.com/api/
2. Place a file named "config.py" in your installation folder with a single line:
    * api_key = YOUR_KEY_GOES_HERE_IN_QUOTES i.e. api_key = "abcdefghijklmnopqrstuvwxyz"
3. Open user_config.py in your installation folder and set your folder path for your roms and your emulator path
