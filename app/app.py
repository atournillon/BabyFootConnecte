# !/usr/bin/python
# coding: utf8

# Importation des packages
from flask import Flask, render_template, request,redirect,url_for, Markup
from flask_socketio import SocketIO, emit
from threading import Thread, Event
import time
import datetime
import logging as lg
import requests
import os
import numpy as np

lg.getLogger('socketio').setLevel(lg.ERROR)
lg.getLogger('engineio').setLevel(lg.ERROR)

# Custom package
import sys
sys.path.append('app/lib')
import interaction_database_app

# Initialisation de la log
t = datetime.datetime.now()
fn = 'logs/run_flask.{}.log'.format(t.strftime("%Y-%m-%d"))
lg.basicConfig(filename = fn,
               level = lg.INFO,
               filemode = 'a',
               format = '%(asctime)s\t%(levelname)s\t%(message)s',
               datefmt = '%Y-%m-%d %H:%M:%S'
               )


###############################
# Lancement app
###############################
app = Flask(__name__)

#Socket IO --> Real time data
socketio = SocketIO(app)
thread = Thread()
thread_stop_event = Event()

#INITIALISATION POUR LES TRAITEMENTS
#global score_b_thread, score_r_thread
#score_b_thread = 0
#score_r_thread = 0


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




@app.route('/')
def index():
    interaction_database_app.purge_live_match()
    return render_template('home.html')


@app.route('/players')
def players():
    players_stat = interaction_database_app.recup_players_stat()
    players_stat = players_stat[players_stat.index!=0]
    return render_template('players.html', players_table=players_stat)

@app.route('/player/<int:id_player>/')
def player(id_player):
    players_table = interaction_database_app.get_players().set_index('id_player')
    players_stat = interaction_database_app.recup_players_stat()
    return render_template('player.html', players_table = players_stat, id_player=id_player)

@app.route('/match_team', methods=['GET', 'POST'])
def match_team():
    interaction_database_app.purge_live_match()
    # show the form, it wasn't submitted
    players_table = interaction_database_app.get_players().set_index('id_player')
    lg.info("je lance")
    os.system('sh /home/pi/Documents/BabyFootConnecte/script_launch_capteurs_statistic.sh &')
    lg.info("je suis sorti du lancement")
    return render_template('match_team.html', players_table = players_table)


@app.route('/finmatch', methods=['GET', 'POST'])	
def finmatch():
    if request.method == 'POST':
        try:
            t = requests.get('http://localhost:3333/calcul_statistique')
            lg.info("je vais killer")
            os.system('sh /home/pi/Documents/BabyFootConnecte/kill_capteurs_statistic.sh')
            lg.info("terminé")
            print(t.status_code)

        except:
            lg.error("PAS DE RAFRAICHISSEMENT DES STATS")
            pass
        players_stat = interaction_database_app.recup_players_stat()
        livematch = interaction_database_app.recup_livematch()
        statsplayers = interaction_database_app.recup_players_stat()
        #legend = 
        line_labelsb1 = [i for i in np.arange(len(interaction_database_app.graphiques_players(livematch['b1'])[-10:]))+1]
        line_valuesb1 = interaction_database_app.graphiques_players(livematch['b1'])[-10:]
        line_labelsb2 = [i for i in np.arange(len(interaction_database_app.graphiques_players(livematch['b2'])[-10:]))+1]
        line_valuesb2 = interaction_database_app.graphiques_players(livematch['b2'])[-10:]
        line_labelsr1 = [i for i in np.arange(len(interaction_database_app.graphiques_players(livematch['r1'])[-10:]))+1]
        line_valuesr1 = interaction_database_app.graphiques_players(livematch['r1'])[-10:]	
        line_labelsr2 = [i for i in np.arange(len(interaction_database_app.graphiques_players(livematch['r2'])[-10:]))+1]
        line_valuesr2 = interaction_database_app.graphiques_players(livematch['r2'])[-10:]
        pie_labels = ['Victoires',u'Défaites']
        pie_valuesb1 = [int(statsplayers.loc[livematch['b1'],'match_win_count']),
            int(statsplayers.loc[livematch['b1'],'match_los_count'])]
        pie_valuesb2 = [int(statsplayers.loc[livematch['b2'],'match_win_count']),
            int(statsplayers.loc[livematch['b2'],'match_los_count'])]
        pie_valuesr1 = [int(statsplayers.loc[livematch['r1'],'match_win_count']),
            int(statsplayers.loc[livematch['r1'],'match_los_count'])]	
        pie_valuesr2 = [int(statsplayers.loc[livematch['r2'],'match_win_count']),
            int(statsplayers.loc[livematch['r2'],'match_los_count'])]			
        colors = ["rgba(78,211,94,0.6)", "rgba(227,18,18,0.6)"]
        return render_template('finmatch.html', players_table = players_stat,setb1=zip(pie_valuesb1,pie_labels,colors),setb2=zip(pie_valuesb2,pie_labels,colors),
		setr1=zip(pie_valuesr1,pie_labels,colors),setr2=zip(pie_valuesr2,pie_labels,colors),
		line_labelsb1=line_labelsb1,line_valuesb1=line_valuesb1,line_labelsb2=line_labelsb2,line_valuesb2=line_valuesb2,
		line_labelsr1=line_labelsr1,line_valuesr1=line_valuesr1,line_labelsr2=line_labelsr2,line_valuesr2=line_valuesr2,
		livematch = livematch,stats = statsplayers)
    else:
        players_stat = interaction_database_app.recup_players_stat()
        livematch = interaction_database_app.recup_livematch()
        statsplayers = interaction_database_app.recup_players_stat()
        line_labelsb1 = [i for i in np.arange(len(interaction_database_app.graphiques_players(livematch['b1'])))+1]
        line_valuesb1 = interaction_database_app.graphiques_players(livematch['b1'])
        line_labelsb2 = [i for i in np.arange(len(interaction_database_app.graphiques_players(livematch['b2'])[-10:]))+1]
        line_valuesb2 = interaction_database_app.graphiques_players(livematch['b2'])[-10:]
        line_labelsr1 = [i for i in np.arange(len(interaction_database_app.graphiques_players(livematch['r1'])[-10:]))+1]
        line_valuesr1 = interaction_database_app.graphiques_players(livematch['r1'])[-10:]
        line_labelsr2 = [i for i in np.arange(len(interaction_database_app.graphiques_players(livematch['r2'])))+1]
        line_valuesr2 = interaction_database_app.graphiques_players(livematch['r2'])	
        pie_labels = ['Victoires',u'Défaites']
        pie_valuesb1 = [int(statsplayers.loc[livematch['b1'],'match_win_count']),
            int(statsplayers.loc[livematch['b1'],'match_los_count'])]
        pie_valuesb2 = [int(statsplayers.loc[livematch['b2'],'match_win_count']),
            int(statsplayers.loc[livematch['b2'],'match_los_count'])]
        pie_valuesr1 = [int(statsplayers.loc[livematch['r1'],'match_win_count']),
            int(statsplayers.loc[livematch['r1'],'match_los_count'])]	
        pie_valuesr2 = [int(statsplayers.loc[livematch['r2'],'match_win_count']),
            int(statsplayers.loc[livematch['r2'],'match_los_count'])]			
        colors = ["rgba(78,211,94,0.6)", "rgba(227,18,18,0.6)"]
        return render_template('finmatch.html', players_table=players_stat,setb1=zip(pie_valuesb1,pie_labels,colors),setb2=zip(pie_valuesb2,pie_labels,colors),
		setr1=zip(pie_valuesr1,pie_labels,colors),setr2=zip(pie_valuesr2,pie_labels,colors),
		line_labelsb1=line_labelsb1,line_valuesb1=line_valuesb1,line_labelsb2=line_labelsb2,line_valuesb2=line_valuesb2,
		line_labelsr1=line_labelsr1,line_valuesr1=line_valuesr1,line_labelsr2=line_labelsr2,line_valuesr2=line_valuesr2,
		livematch = livematch,stats = statsplayers)

	
	
  
  
''' chemin pour enlever un but'''
@app.route('/perte_un_but', methods=['POST'])
def perte_un_but():
    interaction_database_app.perte_un_but()
    return 'ok'
    
''' chemin pour gamelle bleu'''
@app.route('/gamelle_bleu', methods=['POST'])
def gamelle_bleu():
    interaction_database_app.gamelle_bleu()
    time.sleep(2)
    return 'ok'
    
''' chemin pour gamelle rouge'''
@app.route('/gamelle_rouge', methods=['POST'])
def gamelle_rouge():
    interaction_database_app.gamelle_rouge()
    time.sleep(2)
    return 'ok'



@app.route('/livematch', methods=['GET','POST'])
def live_match():
    if request.method=='POST':
        b1_joueur = request.form.get('nom1')
        b2_joueur = request.form.get('nom2')
        r1_joueur = request.form.get('nom3')
        r2_joueur = request.form.get('nom4')

        interaction_database_app.init_prod_live_match(r1_joueur,r2_joueur,b1_joueur,b2_joueur)

        # Récupération des joueurs à partir des id
        df_joueurs_rouges = interaction_database_app.recup_prenom_nom(r1_joueur,r2_joueur)
        df_joueurs_bleus = interaction_database_app.recup_prenom_nom(b1_joueur, b2_joueur)

        return render_template('livematch.html',players_bleu=df_joueurs_bleus,players_rouge=df_joueurs_rouges)
    return redirect(url_for('index'))


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
    lg.info("Client disconnected")
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app.run(debug=True, host='0.0.0.0', port=5000,threaded=True))
