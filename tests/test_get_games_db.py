import os

import user_config

paths = []
results = []
roms = []
records = []
serials = []
names = []

filename = os.path.expandvars(r"%LOCALAPPDATA%\GOG.com\Galaxy\plugins\installed\ps2\GameIndex.txt")
        
with open(filename) as fh:                                  # Open GameIndex.txt
    for line in fh:                                         # For each line
        line = line.strip()                                 
        if line.startswith("Name"):                         # check if it starts with "Name"
            split_line = line.split("= ")                   # Split the line into "Name" and the name of the game
            if(split_line[1] not in names):                 # If the name isn't already in the list,
                names.append(split_line[1])                 # add it
                if prev_line.startswith("Serial"):          # Check if the line before started with "Serial"
                    serials.append(prev_line.split()[2])    # Only then add the corresponding serial
        prev_line = line

for serial, name in zip(serials, names):
    records.append([serial, name])

print("Records:")
print(records[0][0], records[0][1])
print(len(records))

for root, dirs, files in os.walk(user_config.roms_path):
    for file in files:
        if file.endswith(".iso") or file.endswith(".gz"):
            paths.append([os.path.join(root, file)])
            roms.append(os.path.splitext(os.path.basename(file))[0])

print("Roms:")
print(roms[0])
print(len(roms))

for rom in roms:
    for record in records:
        if(rom == record[1]):
            results.append([record[0], record[1]])


print("Results:")
print(len(results))


for x,y in zip(paths, results):
    x.extend(y)

print("Paths:")
for path in paths:
    print(path)
