import json
from sqlalchemy import *
from base import DB

db = DB('sqlite:///champions.db')

IMG_BASE = 'http://ddragon.leagueoflegends.com/cdn/5.2.1/img/champion/'


class Champion(db.Model):
    __tablename__ = 'champions'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    @property
    def image(self):
        return '{}{}.png'.format(IMG_BASE, self.name)

    def __repr__(self):
        return self.name


class Match(db.Model):
    __tablename__ = 'matches'

    def __init__(self, *args, **kwargs):
        kwargs.update(dict(zip([c.key for c in inspect(Match).attrs], args)))
        super(Match, self).__init__(**kwargs)

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    player_id = Column(Integer, primary_key=True)
    champion_id = Column(Integer)
    win = Column(Boolean)

    def __repr__(self):
        return 'Match {}: P {} | C {} | Won: {}'.format(
            self.id, self.player_id, self.champion_id, self.win)


class CompetitionMatch(db.Model):
    __tablename__ = 'competitionmatches'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    roster = Column(Text)  # going to have to do this better than text
    win = Column(Boolean)
    opposition = Column(String(100))

    @property
    def won(self):
        return 'won' if self.win else 'lost'

    @property
    def players(self):
        return json.loads(self.roster)

    def __repr__(self):
        return '{} vs {} on {}'.format('TSM', self.opposition, self.timestamp)


if __name__ == '__main__':
    db.create_all()
