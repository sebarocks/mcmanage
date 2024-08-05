import json
import urllib.parse

from fastapi import FastAPI, Request
from pocketbase import PocketBase
from pocketbase.stores.base_auth_store import BaseAuthStore
from pocketbase.models.record import Record
from datetime import datetime

from settings import my_settings
from activity import setActive
from db import Log


class ServerAuthStore(BaseAuthStore):

    def __init__( self, pb_auth : dict) -> None:
        base_token = pb_auth['token']
        base_model = Record.parse_expanded(pb_auth['model'])
        super().__init__(base_token, base_model)


def pbLoadCookie(cookie_str):
    cookie_decoded = urllib.parse.unquote(cookie_str)
    pb_auth = json.loads(cookie_decoded)
    auth_store = ServerAuthStore(pb_auth)
    pb = PocketBase(my_settings.pocketbase_url, auth_store=auth_store)
    return pb

def pbLoadUser(pb : PocketBase):
    user_id = pb.auth_store.base_model.id
    user = pb.collection("users").get_one(user_id)
    return user

def pbLoad(request : Request):
    try:
        cookie_str = request.cookies.get("pb_auth")
        pb = pbLoadCookie(cookie_str)
        user = pbLoadUser(pb)
        return pb, user
    except:
        return None, None


pbapi = FastAPI()


@pbapi.post("/start")
def start_server():
    pb, user = pbLoad(request)
    if user is not None:
        payload = { 'action': 'start', 'key': my_settings.ec2_key }
        r = requests.post(my_settings.get_status_url, data=json.dumps(payload))
        
        if r.status_code == 200:
            setActive()
        
        message = f"Usuario {user.username} solicito iniciar server desde IP: {req.client.host}. Respuesta: {r.status_code}"
        Log.write(message)
        return message
    else:
        raise HTTPException(status_code=401, detail="Usuario no autorizado")


@pbapi.post("/verify")
def verify(request: Request):
    pb, user = pbLoad(request)
    return user




