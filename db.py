def read_ip():
    with open("ip.txt", "r") as archivo:
        contenido = archivo.read()
    return contenido

def write_ip(ipstr):
    with open("ip.txt", "w") as archivo:
        contenido = archivo.write(ipstr)