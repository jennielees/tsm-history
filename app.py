from flask import Flask, render_template, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from models import Match, Champion
from tsm import TSM_IDS
from analyse import get_players, get_last7

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///champions.db'
db = SQLAlchemy(app)


@app.route('/')
def index():
    matches = get_players()
    last7 = get_last7()
    return render_template('index.html', matches=matches, last7=last7,
                           tsm=TSM_IDS)


@app.route('/matches.json')
def matches():
    practices = Match.query.all()
    # filter_by(player_id=TSM_IDS[p]).\
    #                     filter(Match.timestamp > cutoff, 
    #                            Match.timestamp < m.timestamp)
    r = []
    for p in practices:
        d = {'player': TSM_IDS[p.player_id],
             'champion': Champion.query.get(p.champion_id),
             'timestamp': p.timestamp}
        r.append(d)
    return jsonify(r)


if __name__ == "__main__":
    app.run(port=5050, debug=True)
