import requests
import json
import warnings

import activity

from urllib3.exceptions import InsecureRequestWarning

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


class ServerTap:

    @staticmethod
    def get_time():
        if not Aws.serverOn():
            return "Server Offline"
        
        world_uuid = my_settings.main_world_uuid
        auth_header = {'key': my_settings.servertap_key}

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=InsecureRequestWarning)
            r = requests.get(my_settings.servertap_url + '/worlds/' + world_uuid, headers=auth_header, timeout=3, verify = False)

        timestr = r.json()['time']
        return parseTime(timestr)

    @staticmethod
    def get_players():
        if not Aws.serverOn():
            return None

        auth_header = {'key': my_settings.servertap_key}

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=InsecureRequestWarning)
            r = requests.get(my_settings.servertap_url + '/players', headers=auth_header, timeout=3, verify = False)

        players = r.json()
        return [ player['displayName'] for player in players ]

    @staticmethod
    def get_player_info(name):
        if not Aws.serverOn():
            return None

        auth_header = {'key': my_settings.servertap_key}

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=InsecureRequestWarning)
            r = requests.get(my_settings.servertap_url + '/players', headers=auth_header, timeout=3, verify = False)
        
        players = r.json()

        for player in players:
            if player['displayName'] == name:
                return {
                    'name': player['displayName'],
                    'dimension': player['dimension'],
                    'location': player.get('location',[]),
                    'health': player.get('health',''),
                    'hunger': player.get('hunger',''),
                    'saturation': player.get('saturation','')
                }