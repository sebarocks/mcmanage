import ipaddress
import requests
import json

import db
import pb_api
import activity

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from settings import my_settings
from cors import corsMiddleware
from dns_updater import updateRecord
from api_service import Dynmap, Aws

class UpdateIP(BaseModel):
    nueva_ip: str
    clave: str

class UpdateState(BaseModel):
    accion: str
    clave: str


app = FastAPI()

if my_settings.pb_enabled:
    app.mount("/pb", pb_api.pbapi)
    app.add_middleware(**corsMiddleware)
    db.Log.write("Pocketbase started")

if my_settings.activity_check_enabled:
    activity.scheduler.start()
    db.Log.write("Scheduler started")

# publico
@app.get("/IP")
def get_ip():
    return db.read_ip()

# privado. uso por AWS
@app.post("/IP/update")
def set_ip(req : UpdateIP):
    print(req)
    try:
        ipaddress.ip_address(req.nueva_ip)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de IP inválido")

    if req.clave == my_settings.master_key:
        db.write_ip(req.nueva_ip)
        updateRecord(req.nueva_ip, my_settings.linode_token)
        return {"es_valido": True, "nueva_ip": req.nueva_ip}
    else:
        raise HTTPException(status_code=401, detail="Clave inválida")

# publico
@app.get("/status")
def get_status():
    try: 
        return Aws.get_status()

    except requests.RequestException:
        raise HTTPException(status_code=500, detail="Servicio interno no disponible")

# privado. solo admin
@app.post("/status")
def set_status(req : UpdateState):

    payload = { 'action': req.accion, 'key': req.clave }

    r = requests.post(my_settings.get_status_url, data=json.dumps(payload))

    if r.status_code == 200 and req.accion == 'start':
        activity.setActive()

    return r.json()


# publico
@app.get("/time")
def get_time():
    try: 
        return Dynmap.get_time()
    except:
        raise HTTPException(status_code=500, detail="Servicio interno no disponible")

# publico
@app.get("/players")
def get_players():
    try: 
        return Dynmap.get_players()
    except:
        raise HTTPException(status_code=500, detail="Servicio interno no disponible")

# publico
@app.get("/player/{name}")
def get_player_by_name(name : str):
    try: 
        player = Dynmap.get_player(name)

        if player is None:
            raise HTTPException(status_code=404, detail="Jugador no encontrado")
        else:
            return player

    except requests.RequestException:
        raise HTTPException(status_code=500, detail="Servicio interno no disponible")
        
# publico
@app.get("/last")
def get_last():
    dif = activity.timeSinceLast()
    return f"Ultima actividad: Hace {dif.seconds // 3600}h {(dif.seconds % 3600) // 60}m"

# publico
@app.get("/offline")
def offline():
    return HTTPException(status_code=404, detail="Funcion no disponible")
