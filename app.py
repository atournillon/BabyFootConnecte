""" TODO :
- Ameliorer NavBar
"""

from flask import Flask, render_template
import pandas as pd
import time

from flask_socketio import SocketIO, emit
from flask import Flask, render_template
from threading import Thread, Event

import sqlite3

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
        #infinite loop of magical random numbers
        print("Making random numbers")
        while not thread_stop_event.isSet():
            time_stamp, score_team_1, score_team_2 = getData()
            socketio.emit('livematch', {'score_team_1': score_team_1, 'score_team_2': score_team_2}, namespace='/test')
            print score_team_1
            time.sleep(self.delay)

    def run(self):
        self.scoreLiveMatch()

@app.route('/')
def index():
    return render_template('home.html')

# Retrieve data from database
def getData():
	conn=sqlite3.connect('data/baby_foot.db')
	curs=conn.cursor()

	for row in curs.execute("SELECT * FROM LIVE_MATCH ORDER BY time_stamp DESC LIMIT 1"):
		time_stamp = str(row[0])
		score_team_1 = row[1]
		score_team_2 = row[2]
	conn.close()
	return time_stamp, score_team_1, score_team_2

#Load Players Table
players_table = pd.read_csv('data/players.csv', sep = ';', index_col = 0)
@app.route('/players')
def players():
    return render_template('players.html', players_table = players_table)

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
    return render_template('match_team.html')


@app.route('/livematch')
def live_match():
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
