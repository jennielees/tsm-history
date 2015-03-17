from collections import defaultdict
from datetime import datetime, timedelta
from tsm import TSM_IDS
from models import Match, CompetitionMatch, Champion

TSM_NAMES = {i: k for k, i in TSM_IDS.iteritems()}


def won(match):
    return 'won' if match.win else 'lost'


def player(match):
    return TSM_NAMES.get(match.player_id)


def champion(match):
    return Champion.query.get(match.champion_id)


def get_matches():
    matches = []
    for m in CompetitionMatch.query.order_by('timestamp desc'):
        # print m.players
        cutoff = m.timestamp - timedelta(days=7)
        meta = {
            'timestamp': m.timestamp,
            'opponent': m.opposition,
            'won': won(m)
        }
        players = {}
        for p, c in m.players.iteritems():
            print "{}: {}".format(p, c)
            practices = Match.query.filter_by(player_id=TSM_IDS[p]).\
                filter(Match.timestamp > cutoff, 
                       Match.timestamp < m.timestamp)
            practice = defaultdict(lambda: 0)
            for match in practices:
                practice[match.champion_id] += 1
            players[p] = {Champion.query.get(c_id): n for c_id, n in
                          practice.iteritems()}
            for c_id, n in practice.iteritems():
                print "{} x {}".format(Champion.query.get(c_id), n),
        match = {
            'players': players,
            'meta': meta
        }
        matches.append(match)
    return matches


def get_last7():
    players = {}
    for p in TSM_IDS:
        players[p] = []

        cutoff = datetime.utcnow() - timedelta(days=7)
        practices = Match.query.filter_by(player_id=TSM_IDS[p]).\
            filter(Match.timestamp > cutoff)
        practice = defaultdict(lambda: 0)
        for match in practices:
            practice[match.champion_id] += 1
        champs = [(Champion.query.get(c_id), n) for c_id, n in
                  practice.iteritems()]
        champs = sorted(champs, key=lambda c: c[1], reverse=True)
        # for c_id, n in practice.iteritems():
        #     print "{} x {}".format(Champion.query.get(c_id), n),
        match = {
            'practiced': champs,
        }
        players[p].append(match)
    return players


def get_players():
    players = {}
    for p in TSM_IDS:
        players[p] = []
        for m in CompetitionMatch.query.order_by('timestamp desc'):
            # print m.players
            cutoff = m.timestamp - timedelta(days=7)
            meta = m
            played_ = m.players.get(p).replace(' ', '').replace("'", '')
            if played_ == 'LeBlanc':
                played_ = 'Leblanc'
            played = Champion.query.filter_by(name=played_).first()
            if played is None:
                print 'no match for {}'.format(played_)
            practices = Match.query.filter_by(player_id=TSM_IDS[p]).\
                filter(Match.timestamp > cutoff, 
                       Match.timestamp < m.timestamp)
            practice = defaultdict(lambda: 0)
            for match in practices:
                practice[match.champion_id] += 1
            champs = [(Champion.query.get(c_id), n) for c_id, n in
                      practice.iteritems()]
            champs = sorted(champs, key=lambda c: c[1], reverse=True)
            # for c_id, n in practice.iteritems():
            #     print "{} x {}".format(Champion.query.get(c_id), n),
            match = {
                'practiced': champs,
                'played': played,
                'meta': meta
            }
            players[p].append(match)
    return players
