# !/usr/bin/python
# coding: utf8

# Importation des packages
from flask import Flask, render_template, request,redirect,url_for
from flask_socketio import SocketIO, emit
from threading import Thread, Event
import time

# Custom package
import sys
sys.path.append('app/lib')
import interaction_database_app


# Lancement app
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
            score_b, score_r = interaction_database_app.getData()
            socketio.emit('livematch', {'score_b': score_b, 'score_r': score_r}, namespace='/test')
            time.sleep(self.delay)

    def run(self):
        self.scoreLiveMatch()



global score_b, score_r
score_b = 0
score_r = 0
players_table = interaction_database_app.get_players().set_index('id_player')

@app.route('/')
def index():
    interaction_database_app.purge_live_match()
    return render_template('home.html')

@app.route('/players')
def players():
    players_stat = interaction_database_app.recup_players_stat()
    return render_template('players.html', players_table = players_stat)

@app.route('/player/<int:id_player>/')
def player(id_player):
    return render_template('player.html', players_table = players_table, id_player=id_player)

@app.route('/match_team', methods=['GET', 'POST'])
def match_team():
    if request.method == 'POST':
        # do stuff when the form is submitted
        # redirect to end the POST handling
        # the redirect can be to the same route or somewhere else
        return redirect(url_for('index'))
    # show the form, it wasn't submitted
    return render_template('match_team.html', players_table = players_table)

@app.route('/livematch')
def live_match():
    interaction_database_app.init_prod_live_match()
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
