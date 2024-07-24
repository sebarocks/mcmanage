import json

IP_DB = "ip.txt"
LASTACTIVE_DB = "last.json"

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

authorized_starters = [
    'Seba',
    'Marfull',
    'Carlos',
    'Mike',
    'Benja',
    'Stay'
]