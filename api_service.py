import requests
import json

from settings import my_settings

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