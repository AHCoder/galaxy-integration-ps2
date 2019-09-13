import os
import re

import pycdlib
import user_config

filename = os.path.expandvars(r"%LOCALAPPDATA%\GOG.com\Galaxy\plugins\installed\ps2_1e814707-1fe3-4e1e-86fe-1b8d1b7fac2e\GameIndex.txt")        
records = []
serials = []
names = []
directory = user_config.roms_path
iso = pycdlib.PyCdlib()
paths = []
results = []
serials_test = []

with open(filename) as fh:                              # Open GameIndex.txt
    for line in fh:
        line = line.strip()                             # For each line
        if line.startswith("Name"):                     # check if it starts with "Name"
            split_line = line.split("= ")               # Split the line into "Name" and the name of the game
            names.append(split_line[1])                 # Add the name
            serials.append(prev_line.split()[2])        # Only then add the corresponding serial
        prev_line = line

for serial, name in zip(serials, names):
    records.append([serial, name])

database_records = records
print(len(database_records))

# Get the serials
for root, dirs, files in os.walk(directory):
    for file in files:
        if file.lower().endswith(".iso"):
            try:
                iso.open(os.path.join(root, file))
                paths.append([os.path.join(root, file)])
            except:
                print(f"Can't read {file}")
                continue

            for child in iso.list_children(iso_path='/'):
                string = child.file_identifier().decode("utf-8")

                if re.search(r"\w{4}_\d{3}\.\d{2}|$", string)[0]:
                    serials_test.append(string.replace("_", "-").replace(".", "").replace(";1", ""))
                    break

            iso.close()

# Match the serials to names
for serial in serials_test:
    print(serial)
    for record in database_records:
        if(serial == record[0]):
            print("entered block 2")
            results.append(
                [
                    record[0],
                    record[1]
                ]
            )

for x,y in zip(paths, results):
    x.extend(y)

print("Paths:")
for path in paths:
    print(path)
