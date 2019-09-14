import os

filename = os.path.expandvars(r"%LOCALAPPDATA%\GOG.com\Galaxy\plugins\installed\ps2_1e814707-1fe3-4e1e-86fe-1b8d1b7fac2e\GameIndex.txt")
        
records = []
serials = []
names = []
with open(filename, encoding="utf-8") as fh:                # Open GameIndex.txt
    for line in fh:                                         # For each line
        if line.startswith("Name"):                         # check if it starts with "Name"
            split_line = line.split("= ")                   # Split the line into "Name" and the name of the game
            if(split_line[1] not in names):                 # If the name isn't already in the list,
                names.append(split_line[1])                 # add it
                if prev_line.startswith("Serial"):          # Check if the line before started with "Serial"
                    serials.append(prev_line.split()[2])    # Only then add the corresponding serial
        prev_line = line

for serial, name in zip(serials, names):
    records.append([serial, name])

with open("C:/Users/Ajnol/Desktop/test.txt", "a") as test_file:
    for record in records:
        test_file.write(record[0] + " " + record[1])