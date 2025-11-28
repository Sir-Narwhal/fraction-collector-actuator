import logging
from pymodbus.client import ModbusTcpClient
from redis import Redis
from typing import Dict 
from asyncua import Client 


import string

def generate_wells(): 
    rows = list(string.ascii_uppercase[:8])
    cols = [f"{i:02d}" for i in range(1, 13)] 
    return [f"{r}{c}" for r in rows for c in cols]

class Biofrac(): 
    def __init__(self, settings: Dict[str, object]): 
        self.redis_client = Redis(settings['REDIS_CONNECTION_URL'])
        
        self.modbus_client = ModbusTcpClient(settings['MODBUS_CONNNECTION_URL'])
        try: 
            self.modbus_client.connect() 
        except Exception as ex: 
            logging.fatal(f"Unable to connect to MODBUS Client: {ex}")

        self.position = 0 
        self.plate = 0 
        self.orientation = 'serpentine'
        self.cid = '' 
    

    def advance(self): 
        '''
        '''
        
        # Advance Fraction collector 

        self.position += 1 
        if self.position == 96: 
            self.plate += 1

if __name__ == "__main__": 
    print(generate_wells()) 

        



