import os
import subprocess
import user_config

emu_path = user_config.emu_path
no_gui = user_config.emu_no_gui
fullscreen = user_config.emu_fullscreen
config = user_config.emu_config
config_folder = user_config.config_path
path = "F:/Games/PS2/Athens 2004/Athens 2004.gz"

rom_file = os.path.splitext(os.path.basename(path))[0]
config_folder_game = config_folder + "/" + rom_file
args = [emu_path]
if config and os.path.isdir(config_folder_game):
    config_arg = "--cfgpath=" + config_folder + "/" + rom_file
    args.append(config_arg)
if fullscreen:
    args.append("--fullscreen")
if no_gui:
    args.append("--nogui")
args.append(path)
print(args)
subprocess.Popen(args)