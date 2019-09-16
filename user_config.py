# Make sure to use / instead of \ in file paths.

# Set your roms folder here
roms_path = "C:/Games/PS2"

# Set the path to your pcsx2.exe here
emu_path = "C:/Programs/Emulators/PCSX2 1.4.0/pcsx2.exe"

# Set to True if you want to suppress the gui when launching a game
emu_no_gui = False

# Set to True if you want to launch in fullscreen by default
emu_fullscreen = False

'''
Decide which method you want to use when adding your games
"default": your files have to be named exactly as they are in the PCSX2 database (if the name contains a ":", delete it)
"giant": use the Giant Bomb API to search for the name of your files in their database (requires a Giant Bomb account for an API key)
"iso": reads your iso files directly for the serial of the game and then matches the name to it (only adds all your games if they are all iso files)
'''
method = "default"

# Set your API key here if you are using the Giant Bomb method
api_key = ""

# Set to True if you want to use game specific configurations
emu_config = False

'''
To use this feature, create a folder named "configs" inside "Documents/PCSX2" (the folder containing your bios, savestates etc.)
Put the path to that folder down below
To create settings for a game, copy the "inis" or "inis_1.4.0" folder into the "configs" folder and rename it to match the rom.
Make sure that the renamed folders have the same name as the corresponding rom without the extension.
eg. ROM: "Shadow of the Colossus.iso" | FOLDER: "Shadow of the Colossus"
Without a specific config folder for a game, the default settings will be used.
'''
config_path = "C:/Documents/PCSX2/configs"
