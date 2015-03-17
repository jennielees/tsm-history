# Enter LCS matches

from datetime import datetime
import json
import requests
from bs4 import BeautifulSoup

from models import db, CompetitionMatch
from tsm import TSM_IDS


def commandline():
    while True:
        print "Enter details of TSM competition match:"

        when = raw_input("Date (YY-MM-DD): ")
        opponent = raw_input("Vs: ")

        players = {}
        for t in TSM_IDS:
            champ = raw_input("{}: ".format(t))
            players[t] = champ

        win = raw_input("Win (Y/N)? ")

        date = datetime.strptime(when, "%y-%m-%d")
        win = True if win.lower() == 'y' else False

        m = CompetitionMatch(timestamp=date,
                             roster=json.dumps(players),
                             win=win, opposition=opponent)
        db.session.add(m)
        db.session.commit()
        print
        print "Added match vs {} on {}".format(opponent, date)
        print


def teams(caption):
    team1 = caption.contents[0].text
    team2 = caption.contents[2].text
    return (team1, team2)

BASE_URL = 'http://lol.gamepedia.com/2015_NA_LCS_Spring/'
BASE_URL += 'Scoreboards/Round_Robin/Week_'


def bs():
    games = []
    for i in range(1, 8):
        t = requests.get(BASE_URL + str(i)).text
        soup = BeautifulSoup(t)
        headers = soup.find_all('h2')

        for h in headers:
            if not h.span or not h.span.text.startswith('Day'):
                continue
            tb = h.next_sibling.next_sibling.find_all('table')

            for t in tb:
                if not t.caption:
                    continue
                # teams
                (team1, team2) = teams(t.caption)
                opponent = None
                first = False
                if 'SoloMid' in team1:
                    opponent = team2
                    first = True
                if 'SoloMid' in team2:
                    opponent = team1
                if not opponent:
                    continue

                won = False
                # Slightly painful way to determine win
                for tr in t.find_all('tr'):
                    if tr.th and tr.th.text.strip() == team1:
                        s1 = tr.find_all('th')[1].text.strip()
                        s2 = tr.find_all('th')[2].text.strip()
                        team_1_won = int(s1) > int(s2)
                        if first and team_1_won:
                            won = True
                        if not first and not team_1_won:
                            won = True

                subtables = t.find_all('table')
                # this is sometimes [1] and sometimes [0]??
                s_i = 1
                if 'Date' not in subtables[1].text:
                    s_i = 0
                when = subtables[s_i].tr.td.contents[1].strip()
                when = datetime.strptime(when, '%Y-%m-%d')

                if first:
                    indexes = range(3, 12, 2)
                else:
                    indexes = range(15, 24, 2)
                players = {}
                for i in indexes:
                    c = subtables[s_i+1].contents[i]
                    champ_name = c.find_all('td')[0].a.get('title')
                    player_name = c.find_all('td')[1].text.strip()
                    players[player_name] = champ_name

                m = CompetitionMatch(timestamp=when,
                                     roster=json.dumps(players), win=won,
                                     opposition=opponent)
                print m
                db.session.add(m)
                games.append(m)
    return games
games = bs()
db.session.commit()
