from collections import namedtuple
import requests

CHAMPS_URL = 'https://global.api.pvp.net/api/lol/static-data/na/v1.2/champion'

Champion = namedtuple('Champion', ['id', 'name'])


def get_champions(api_key):
    r = requests.get(CHAMPS_URL + '?api_key=' + api_key)
    r = r.json()
    champions = r.get('data')
    return {c.get('id'): k for k, c in champions.iteritems()}
