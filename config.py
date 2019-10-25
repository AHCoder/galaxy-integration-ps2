import configparser
import textwrap


CONFIG_LOC = r"%LOCALAPPDATA%\GOG.com\Galaxy\Configuration\plugins\ps2\config.ini"

class Config:
    def __init__(self):
        self.cfg = configparser.ConfigParser(allow_no_value=True)
        self.cfg.set("DEFAULT", "; Make sure to use / instead of \ in file paths.")
        self.cfg["DEFAULT"]["roms_path"] = "C:/Games/PS2"
        self.cfg["DEFAULT"]["emu_path"] = "C:/Program Files (x86)/PCSX2 1.4.0/pcsx2.exe"
        self.cfg["DEFAULT"]["config_path"] = "C:/Documents/PCSX2/configs"
        self.cfg["DEFAULT"]["emu_fullscreen"] = False
        self.cfg["DEFAULT"]["emu_no_gui"] = False
        self.cfg["DEFAULT"]["emu_config"] = False
        self.cfg["DEFAULT"]["method"] = "default"
        self.cfg["DEFAULT"]["api_key"] = None
        
        self.cfg.add_section("Paths")
        self.cfg.set("Paths", textwrap.dedent(
                """\
                ; Set your roms folder, path to your pcsx2.exe and optional config path here
                ; To use the config feature, create a folder named "configs" inside "Documents/PCSX2" (the folder containing your bios, savestates etc.)
                ; Put the path to that folder down below
                ; To create settings for a game, copy the "inis" or "inis_1.4.0" folder into the "configs" folder and rename it to match the rom.
                ; Make sure that the renamed folders have the same name as the corresponding rom without the extension.
                ; eg. ROM: "Shadow of the Colossus.iso" | FOLDER: "Shadow of the Colossus"
                ; Without a specific config folder for a game, the default settings will be used.
                ; If you want to specify that PCSX2 does a full boot for a game follow the above instructions
                ; and simply add an empty file "fullboot.ini" to the rom folder in "configs"\
                """
            )
        )
        
        self.cfg.add_section("EmuSettings")
        self.cfg.set("EmuSettings", textwrap.dedent(
                """\
                ; emu_fullscreen: Set to True if you want to launch in fullscreen by default
                ; emu_no_gui: Set to True if you want to suppress the gui when launching a game
                ; emu_config: Set to True if you want to use game specific configurations\
                """
            )
        )
        
        self.cfg.add_section("Method")
        self.cfg.set("Method", textwrap.dedent(
                """\
                ; Decide which method you want to use when adding your games
                ; "default": your files have to be named exactly as they are in the PCSX2 database (if the name contains a ":", delete it)
                ; "giant": use the Giant Bomb API to search for the name of your files in their database (requires a Giant Bomb account for an API key)
                ; "iso": reads your iso files directly for the serial of the game and then matches the name to it (only adds all your games if they are all iso files)
                ; Also set your API key here if you are using the Giant Bomb method\
                """
            )
        )