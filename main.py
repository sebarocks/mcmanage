import ipaddress
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from dns_updater import updateRecord

class MySettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env',extra='allow')

class UpdateIP(BaseModel):
    nueva_ip: str
    clave: str

settings = MySettings()
app = FastAPI()

def read_file():
    with open("ip.txt", "r") as archivo:
        contenido = archivo.read()
    return contenido

def write_file(ipstr):
    with open("ip.txt", "w") as archivo:
        contenido = archivo.write(ipstr)

@app.get("/IP")
def get_ip():
    return read_file()

@app.post("/IP/update")
def set_ip(req : UpdateIP):
    print(req)
    try:
        ipaddress.ip_address(req.nueva_ip)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de IP inválido")

    if req.clave == settings.master_key:
        write_file(req.nueva_ip)
        updateRecord(req.nueva_ip, settings.linode_token)
        return {"es_valido": True, "nueva_ip": req.nueva_ip}
    else:
        raise HTTPException(status_code=401, detail="Clave inválida")