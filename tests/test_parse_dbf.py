import os

filename = os.path.expandvars(r"%LOCALAPPDATA%\GOG.com\Galaxy\plugins\installed\ps2_1e814707-1fe3-4e1e-86fe-1b8d1b7fac2e\GameIndex.txt")
records = {}

with open(filename, encoding="utf-8") as fh:                
    for line in fh:
        line = line.strip()                                 
        if line.startswith("Name"):                         
            split_line = line.split("= ")                   # Split the line into "Name" and the name of the game
            if(False or split_line[1] not in records.values()):                    
                serial = prev_line.split()[2]
                name = split_line[1]
                records[serial] = name
        prev_line = line

with open("C:/Users/Ajnol/Desktop/test.txt", "a") as test_file:
    for key in records:
        test_file.writelines(key + " " + records.get(key) + "\n")