import os
import yaml

filename = os.path.expandvars(r"%LOCALAPPDATA%\GOG.com\Galaxy\plugins\installed\ps2_1e814707-1fe3-4e1e-86fe-1b8d1b7fac2e\GameIndex.yaml")
test_dict = yaml.load(open(filename))
for key in test_dict:
    print(key)