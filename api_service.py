import requests
import json

from settings import my_settings
from mc_utils import parseTime

class Dynmap:

    @staticmethod
    def get_players():
        r = requests.get(my_settings.dynmap_json_url, timeout=3)
        players = r.json()['players']
        return [ player['name'] for player in players ]

    @staticmethod
    def get_player(name):
        r = requests.get(my_settings.dynmap_json_url, timeout=3)
        players = r.json()['players']
        for player in players:
            if player['name'] == name:
                return player
        return None

    @staticmethod
    def get_time():
        r = requests.get(my_settings.dynmap_json_url, timeout=3)
        timestr = r.json()['servertime']
        return parseTime(timestr)

class Aws:

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

        return r.json()
