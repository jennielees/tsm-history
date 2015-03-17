import requests
import time
import os
from datetime import datetime

# Issues with HTTPS not relevant for test project
import warnings
warnings.filterwarnings("ignore")

from champions import get_champions
from models import Match, Champion, db

DEV_API_KEY = os.environ.get('LOL_API_KEY')

TSM_IDS = {
    'Dyrus': 5908,
    'Santorin': 57029179,  # HotGuy6Pack
    'WildTurtle': 18991200,  # Turtle the Cat: WildTurtle is 521955
    'Bjergsen': 49159160,
    'Lustboy': 56917699
}

MATCH_URL = 'https://na.api.pvp.net/api/lol/na/v2.2/matchhistory/'


def save_champions():
    if not DEV_API_KEY:
        print 'No API key!'
        raise Exception("No API key!")
    champs = get_champions(DEV_API_KEY)
    for c in champs:
        champion = Champion(id=c, name=champs[c])
        db.session.add(champion)


def load_stored_matches():
    matches = Match.query.all()
    return {m.id: m for m in matches}


def extract_played(matches):
    results = []
    for m in matches:
        id = m.get('matchId')
        timestamp = datetime.fromtimestamp(m.get('matchCreation') / 1000)
        player = m.get('participants')[0]
        champion_id = player.get('championId')
        win = player.get('stats').get('winner') 
        summoner_id = m.get('participantIdentities')[0]['player']['summonerId']
        m = Match(id, timestamp, summoner_id, champion_id, win)
        results.append(m)
    return results


def get_tsm_games():
    if not DEV_API_KEY:
        print 'No API key!'
        raise Exception("No API key!")
    matches = load_stored_matches()
    api_calls = 0
    for player, summoner_id in TSM_IDS.iteritems():
        index = 0
        while index < 1000:
            url = '{}{}?rankedQueues=RANKED_SOLO_5x5&api_key={}'.format(
                MATCH_URL, summoner_id, DEV_API_KEY)
            url = '{}&beginIndex={}&endIndex={}'.format(index, index+15)
            try:
                api_calls += 1
                r = requests.get(url)
                r = r.json()
                if r.get('matches') is None:
                    break
                games = extract_played(r.get('matches'))
                games = filter(lambda g: g.id not in matches, games)
                map(db.session.add, games)
                db.session.commit()
                print "Saved {} ({}) matches for {}".format(15, index, player)
                index += 15
                if api_calls < 500:
                    time.sleep(1)
                else:
                    time.sleep(10 * 60)
                    api_calls = 0
            except Exception as e:
                # Probably some issue with index
                print "Error retrieving matches for {}, index {}".format(
                    player, index)
                print e
                break

if __name__ == "__main__":
    save_champions()
    db.session.commit()
    get_tsm_games()
