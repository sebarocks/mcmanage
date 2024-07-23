import ipaddress
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.wsgi import WSGIMiddleware
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from dns_updater import updateRecord
from wsgiproxy import HostProxy
from mc_utils import parseTime, MCTime
from db import read_ip, write_ip

class MySettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env',extra='allow')

class UpdateIP(BaseModel):
    nueva_ip: str
    clave: str

class UpdateState(BaseModel):
    accion: str
    clave: str

settings = MySettings()
app = FastAPI()

@app.get("/IP")
def get_ip():
    return read_ip()

@app.post("/IP/update")
def set_ip(req : UpdateIP):
    print(req)
    try:
        ipaddress.ip_address(req.nueva_ip)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de IP inválido")

    if req.clave == settings.master_key:
        write_ip(req.nueva_ip)
        updateRecord(req.nueva_ip, settings.linode_token)
        return {"es_valido": True, "nueva_ip": req.nueva_ip}
    else:
        raise HTTPException(status_code=401, detail="Clave inválida")

@app.get("/status")
def get_status():
    try: 
        r = requests.get(settings.get_status_url)
        return r.json()

    except requests.RequestException:
        raise HTTPException(status_code=500, detail="Servicio interno no disponible")

@app.post("/status")
def set_status(req : UpdateState): 

    r = requests.post(settings.get_status_url, 
        data={
            'action': req.accion,
            'key': req.clave,
            }
        )
    return r.status_code 

app.mount("/map", WSGIMiddleware(HostProxy(settings.dynmap_server)))

@app.get("/time")
def get_time():
    try: 
        r = requests.get(settings.dynmap_json_url)
        timestr = r.json()['servertime']
        return parseTime(timestr)

    except requests.RequestException:
        raise HTTPException(status_code=500, detail="Servicio interno no disponible")

@app.get("/players")
def get_players():
    try: 
        r = requests.get(settings.dynmap_json_url)
        players = r.json()['players']
        return [ player['name'] for player in players ]

    except requests.RequestException:
        raise HTTPException(status_code=500, detail="Servicio interno no disponible")

@app.get("/player/{name}")
def get_player_by_name(name : str):
    try: 
        r = requests.get(settings.dynmap_json_url)
        players = r.json()['players']
        for player in players:
            if player['name'] == name:
                return player
        raise HTTPException(status_code=404, detail="Jugador no encontrado")

    except requests.RequestException:
        raise HTTPException(status_code=500, detail="Servicio interno no disponible")
 