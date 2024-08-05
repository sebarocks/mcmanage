import json
from datetime import datetime

IP_DB = "db/ip.txt"
LASTACTIVE_DB = "db/last.json"
LOG_DB = "db/log.txt"

def read_ip():
    with open(IP_DB, "r") as archivo:
        contenido = archivo.read()
    return contenido

def write_ip(ipstr):
    with open(IP_DB, "w") as archivo:
        contenido = archivo.write(ipstr)

def read_lastactive():
    with open(LASTACTIVE_DB, 'r') as f:
        return json.load(f)

def write_lastactive(data):
    with open(LASTACTIVE_DB, 'w') as f:
        json.dump(data, f, indent=4)

class Log:

    @staticmethod
    def read():
        with open(LOG_DB, "r") as archivo:
            contenido = archivo.read()
        return contenido

    @staticmethod
    def write(str):
        nowstr = datetime.utcnow().isoformat()
        with open(LOG_DB, "a") as archivo:
            contenido = archivo.write(f"[{nowstr}] {str} \n")


authorized_starters = [
    'Seba',
    'Marfull',
    'Carlos',
    'Mike',
    'Benja',
    'Stay'
]