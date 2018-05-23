""" TODO :
- Live Score
- Ameliorer NavBar
"""

from flask import Flask, render_template, request, url_for, redirect
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')

score_team_1 = 0
score_team_2 = 10

@app.route('/livematch')
def live_match():
    return render_template('livematch.html', score_team_1 = score_team_1, score_team_2 = score_team_2)

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

if __name__ == '__main__':
    app.run(debug=True)
