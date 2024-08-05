import requests
import json

import db

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

from settings import my_settings


# Setea server como activo
def setActive():
    now = datetime.utcnow()
    db.write_lastactive(now.isoformat())
    db.Log.write("server marked as active")


# Cada 1 minuto o cada 5 minutos
def checkPlayers():    
    players = get_players()
    db.Log.write(len(players) + " players online")

    if len(players) > 0:
        now = datetime.utcnow()
        db.write_lastactive(now.isoformat())

# Accion apaga server si
def checkActivity():

    now = datetime.utcnow()
    cutoff_time = now - timedelta(hours=3)
    last_active = db.read_lastactive()

    if datetime.fromisoformat(last_active) < cutoff_time:
        db.Log.write("server inactivo :/ apagando...")
        payload = { 'action': 'stop', 'key': my_settings.ec2_key }
        r = requests.post(my_settings.get_status_url, data=json.dumps(payload))
        db.Log.write(r.json())
    else:
        db.Log.write("last activity: ", last_active)

def timeSinceActivity():
    now = datetime.utcnow()
    last = datetime.fromisoformat(db.read_lastactive())
    dif = now - last
    return dif


scheduler = BackgroundScheduler()
scheduler.add_job(checkActivity, trigger='interval', hours=1)
scheduler.add_job(checkPlayers, trigger='interval', minutes=5)

