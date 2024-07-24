import ipaddress
import requests
import json

import db

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.wsgi import WSGIMiddleware
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from datetime import datetime, timedelta
from wsgiproxy import HostProxy
from apscheduler.schedulers.background import BackgroundScheduler

from dns_updater import updateRecord
from mc_utils import parseTime, MCTime


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
    return db.read_ip()

@app.post("/IP/update")
def set_ip(req : UpdateIP):
    print(req)
    try:
        ipaddress.ip_address(req.nueva_ip)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de IP inválido")

    if req.clave == settings.master_key:
        db.write_ip(req.nueva_ip)
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

    payload = { 'action': req.accion, 'key': req.clave }

    r = requests.post(settings.get_status_url, data=json.dumps(payload))

    return r.json()

app.mount("/map", WSGIMiddleware(HostProxy(settings.dynmap_server)))

@app.get("/time")
def get_time():
    try: 
        r = requests.get(settings.dynmap_json_url, timeout=3)
        timestr = r.json()['servertime']
        return parseTime(timestr)

    except requests.RequestException:
        raise HTTPException(status_code=500, detail="Servicio interno no disponible")

@app.get("/players")
def get_players():
    try: 
        r = requests.get(settings.dynmap_json_url, timeout=3)
        players = r.json()['players']
        return [ player['name'] for player in players ]

    except requests.RequestException:
        raise HTTPException(status_code=500, detail="Servicio interno no disponible")

@app.get("/player/{name}")
def get_player_by_name(name : str):
    try: 
        r = requests.get(settings.dynmap_json_url, timeout=3)
        players = r.json()['players']
        for player in players:
            if player['name'] == name:
                return player
        raise HTTPException(status_code=404, detail="Jugador no encontrado")

    except requests.RequestException:
        raise HTTPException(status_code=500, detail="Servicio interno no disponible")

@app.get("/start_mc")
def start_server(req : Request, user : str):

    if user in db.authorized_starters:
        payload = { 'action': 'start', 'key': settings.ec2_key }
        r = requests.post(settings.get_status_url, data=json.dumps(payload))
        return f"Usuario {user} solicito iniciar server desde IP: {req.client.host}. Respuesta: {r.status_code}"
    else:
        raise HTTPException(status_code=401, detail="Usuario no autorizado")


# Cada 1 minuto o cada 5 minutos
def checkPlayers():
    now = datetime.utcnow()
    try:
        players = get_players()
        print(len(players),"players online")

        if len(players) > 0:
            db.write_lastactive(now.isoformat())
    except:
        return

# Accion apaga server si
def checkActivity():

    now = datetime.utcnow()
    cutoff_time = now - timedelta(hours=3)
    last_active = db.read_lastactive()

    if datetime.fromisoformat(last_active) < cutoff_time:
        print("server inactivo :/ apagando...")
        payload = { 'action': 'stop', 'key': settings.ec2_key }
        r = requests.post(settings.get_status_url, data=json.dumps(payload))
        print(r.json())
    else:
        print("last activity:",last_active)

scheduler = BackgroundScheduler()
scheduler.add_job(checkActivity, trigger='interval', hours=1)
scheduler.add_job(checkPlayers, trigger='interval', minutes=1)

# Inicie el scheduler en segundo plano
scheduler.start()