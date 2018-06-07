""" TODO :
- Ameliorer NavBar
- Ajouter
"""


""" TODO :
- Ameliorer NavBar
- Ajouter
"""

from flask import Flask, render_template, request
import pandas as pd
import time
import datetime

from flask_socketio import SocketIO, emit
from flask import Flask, render_template
from threading import Thread, Event

import sqlite3 as lite

app = Flask(__name__)

#Socket IO --> Real time data
socketio = SocketIO(app)
thread = Thread()
thread_stop_event = Event()

#New thread to get live data from the SQLITE DB
class LiveScoreThread(Thread):
    def __init__(self):
        self.delay = 1 #Query the DB each 1 second
        super(LiveScoreThread, self).__init__()

    def scoreLiveMatch(self):
        """
        Query the DB to get the live score each second
        Ideally to be run in a separate thread?
        """
        #infinite loop
        while not thread_stop_event.isSet():
            score_b, score_r = getData()
            socketio.emit('livematch', {'score_b': score_b, 'score_r': score_r}, namespace='/test')
            time.sleep(self.delay)

    def run(self):
        self.scoreLiveMatch()

@app.route('/')
def index():
    purge_live_match()
    return render_template('home.html')

global score_b, score_r
score_b = 0
score_r = 0

# Retrieve data from database
def getData():
    try:
        conn_thr=lite.connect('data/PARC_DES_PRINCES.db')
        curs_thr=conn_thr.cursor()
        table = curs_thr.execute("SELECT * FROM PROD_LIVE_MATCH").fetchall()
        if len(table) == 0:
            return '/', '/'
        else:
            row = table[0] #Just one line in the table
            score_b = row[7]
            score_r = row[8]

        conn_thr.close()

    except:
        pass

    return score_b, score_r


def get_players():
    #Load Players Table
    conn = lite.connect('data/PARC_DES_PRINCES.db')
    query = "SELECT * FROM PROD_REF_PLAYERS"
    df_players = pd.read_sql(query, conn)
    conn.close()
    return df_players


players_table = get_players().set_index('id_player')
@app.route('/players')
def players():
    conn = lite.connect('data/PARC_DES_PRINCES.db')
    query = "SELECT * FROM PROD_STAT_PLAYERS LIMIT 5"
    players_stat= pd.read_sql(query, conn).set_index('id_player')
    conn.close()
    return render_template('players.html', players_table = players_stat)

@app.route('/player/<int:id_player>/')
def player(id_player):
    return render_template('player.html', players_table = players_table, id_player=id_player)


#Load Choix Equipe
@app.route('/match_team', methods=['GET', 'POST'])
#def match_team():
#    return render_template('match_team.html')

def match_team():
    if request.method == 'POST':
        # do stuff when the form is submitted

        # redirect to end the POST handling
        # the redirect can be to the same route or somewhere else
        return redirect(url_for('index'))

    # show the form, it wasn't submitted
    return render_template('match_team.html', players_table = players_table)

#  Initalisation de la fonction de vidage des tables
def purge_live_match():
    conn=lite.connect('data/PARC_DES_PRINCES.db')
    curs=conn.cursor()

    # Purge de la table contenant le live du match
    curs.execute("DELETE FROM PROD_LIVE_MATCH")
    conn.commit()
    conn.close()


#Function to insert data on PROD_LIVE_MATCH when livematch.html is loaded
def init_prod_live_match():
    conn=lite.connect('data/PARC_DES_PRINCES.db')
    curs=conn.cursor()
    id_match = int(time.mktime(datetime.datetime.now().timetuple()))
    b1 = 0
    b2 = 0
    r1 = 0
    r2 = 0
    score_b = 0
    score_r = 0
    curs.execute("INSERT INTO PROD_LIVE_MATCH values((?), (?), (?), (?), (?), datetime('now'), datetime('now'), (?), (?))", (id_match, b1, b2, r1, r2, score_b, score_r))
    conn.commit()
    conn.close()


@app.route('/livematch')
def live_match():
    init_prod_live_match()
    return render_template('livematch.html')

@socketio.on('connect', namespace='/test')
def test_connect():
    #Need visibility of the global thread object
    global thread
    print('Client connected')

    #Start the live score thread to get live data
    if not thread.isAlive():
        print("Starting Thread")
        thread = LiveScoreThread()
        thread.start()

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app.run(debug=True))
