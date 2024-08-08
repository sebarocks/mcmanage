import requests
import json

import activity

from settings import my_settings
from mc_utils import parseTime
from db import Log

class Dynmap:

    @staticmethod
    def get_players():
        if not Aws.serverOn():
            return []
        
        r = requests.get(my_settings.dynmap_json_url, timeout=3)
        players = r.json()['players']
        return [ player['name'] for player in players ]

    @staticmethod
    def get_player(name):
        if not Aws.serverOn():
            return None

        r = requests.get(my_settings.dynmap_json_url, timeout=3)
        players = r.json()['players']
        for player in players:
            if player['name'] == name:
                return player
        return None

    @staticmethod
    def get_time():
        if not Aws.serverOn():
            return "Server Offline"
        
        r = requests.get(my_settings.dynmap_json_url, timeout=3)
        timestr = r.json()['servertime']
        return parseTime(timestr)

class Aws:

    @classmethod
    def serverOn(cls):
        try:
            status = cls.get_status()
            return status['instanceState'] == 'running'
        except Exception as e:
            Log.write(e.args)
            return false

    @staticmethod
    def get_status():
        r = requests.get(my_settings.get_status_url)
        return r.json()

    @staticmethod
    def start_server():
        payload = { 'action': 'start', 'key': my_settings.ec2_key }
        r = requests.post(my_settings.get_status_url, data=json.dumps(payload))

        if r.status_code == 200:
            activity.setActive()

        return r
