import ipaddress
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.wsgi import WSGIMiddleware
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from dns_updater import updateRecord
from wsgiproxy import HostProxy

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
