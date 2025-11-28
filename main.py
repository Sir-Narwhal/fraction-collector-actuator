import os
import string 

def get_settings(): 
    settings = {}

    settings["REDIS_CONNECTION_URL"] = os.environ.get("REDIS_CONNECTION_URL", "10.20.18.65")
    settings["MODBUS_CONNECTION_URL"] = os.environ.get("MODBUS_CONNECTION_URL","10.20.20.25") 
    
    return settings


if __name__ == "__main__": 
    rows = list(string.ascii_uppercase[:8])
    cols = [f"{i:02d}" for i in range(1, 13)] 

    wells = [] 
    for i, row in enumerate(rows): 
        if i > 0: 
            cols.reverse()
        wells.extend([f"{row}{c}" for c in cols])

    print(wells) 