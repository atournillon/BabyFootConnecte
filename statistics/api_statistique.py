#!/usr/bin/python
#coding: utf8

# BABY FOOT Connecté
# Programme pour : Stat des joeurs & Matchs + Score
# Juin 2017
#Others indicators : Match,Victoires,Défaites,Plus longue série de victoires,Buts marqués ,Bus encaissés ,Score moyen ,Score Meilleur match,Score pire défaite
#Adversaire favoris (plus de victoires) ,Adversaire redoutable (plus de défaites) ,Meilleur partenaire (plus de victoires) ,Pire partenaire (plus de défaites)



#Import librairies python
import pandas as pd
import numpy as np
import datetime

#Initialisation de SQLite
import sys
sys.path.append("data")
import fonction_database

sys.path.append("statistics/lib")
import fonction_statistiques

# Pour la partie API
from flask import Flask, Response, request
app = Flask(__name__)


# created a *threaded* video stream, allow the camera sensor to warmup,
@app.route('/calcul_statistique')
def calcul_statistique():
    ####################################""
    # Requêtage sur la table d'histo match
    conn, cur = fonction_database.fonction_connexion_sqllite()
    input_match_df = pd.read_sql_query(
        "select a.* from PROD_LIVE_MATCH_HISTO as a INNER JOIN (SELECT distinct id_match FROM PROD_LIVE_MATCH_HISTO WHERE score_b = 10 OR score_r = 10) as b ON a.id_match = b.id_match;",
        cur)
    fonction_database.fonction_connexion_sqllite_fermeture(conn, cur)

    ############ preprocessing ####################
    # compute dataframe with one row per match : id_match / start_time / end_time / duration / players_dom / players_etx /
    # winers / losers / score_win / score_los / score_diff / goal_per_min_win / goal_per_min_los
    ###############################################
    #### time_function
    columns_time = ['id_match', 'time_goal']
    match_time = fonction_statistiques.time_function(input_match_df[columns_time])

    #### match_players
    columns_players = ['id_match', 'b1', 'b2', 'r1', 'r2']
    match_players = fonction_statistiques.players_function(input_match_df[columns_players])

    #### match_results : winner_id1 / winner_id2 / losers_id1 / loser_id2 / goal_winners / goal_losers / goal_difference
    columns_results = ['id_match', 'b1', 'b2', 'r1', 'r2', 'score_b', 'score_r']
    match_results = fonction_statistiques.results_function(input_match_df[columns_results][
                                                               (input_match_df.score_b == 10) | (
                                                                           input_match_df.score_r == 10)].drop_duplicates())

    ############### join all parts ################
    # join all dataframe by id_match
    ###############################################
    resume_match_df = pd.concat([match_time, match_players, match_results], axis=1).reset_index()

    ######################################################################################
    ######################################################################################
    ########################### PLAYERS RESUME ###########################################
    ######################################################################################
    ######################################################################################
    # new dataframe with all players
    players = pd.unique(resume_match_df[['winner_id1', 'winner_id2', 'loser_id1', 'loser_id2']].values.ravel('K'))

    # Loop for each player ?
    col = ['match_count', 'match_win_count', 'match_los_count', 'game_time_sec', 'goals_win_count', 'goals_los_count']
    resume_players = pd.DataFrame(columns=col)

    for player in players:
        # keep only match played
        match = resume_match_df[
            player == resume_match_df[['winner_id1', 'winner_id2', 'loser_id1', 'loser_id2']].values]

        # generate stats
        match_count = match.shape[0]
        match_win_count = match[player == match[['winner_id1', 'winner_id2']].values].shape[0]
        match_los_count = match[player == match[['loser_id1', 'loser_id2']].values].shape[0]
        game_time_sec = match.time_duration.sum()
        goals_win_count = match[player == match[['winner_id1', 'winner_id2']].values].goal_winner.sum()
        goals_los_count = match[player == match[['loser_id1', 'loser_id2']].values].goal_loser.sum()

        # create temp dataframe for player
        resume_player = pd.DataFrame(np.array([[match_count, match_win_count, match_los_count, game_time_sec,
                                                goals_win_count, goals_los_count]]), index=[player], columns=col)

        # concat resume_player with resume_players
        resume_players = pd.concat([resume_players, resume_player], axis=0)

    # generate other stats
    resume_players['match_win_percent'] = resume_players.match_win_count / resume_players.match_count
    resume_players['goals_count'] = resume_players.goals_win_count + resume_players.goals_los_count
    resume_players['goal_per_minut'] = resume_players.goals_count / (resume_players.game_time_sec / 60)

    resume_players_df = resume_players.rename_axis("id_player").reset_index()

    # Jointure avec le référentiel joueur
    conn, cur = fonction_database.fonction_connexion_sqllite()
    ref_player = pd.read_sql_query("select * from PROD_REF_PLAYERS;", cur)
    fonction_database.fonction_connexion_sqllite_fermeture(conn, cur)

    resume_players_df_vf = pd.merge(ref_player, resume_players_df)

    conn, cur = fonction_database.fonction_connexion_sqllite()
    resume_players_df_vf.to_sql('PROD_STAT_PLAYERS', cur, index=False, if_exists='replace')
    fonction_database.fonction_connexion_sqllite_fermeture(conn, cur)

    return "ok"

# Lancement de l'app
if __name__ == '__main__':
    # Lancement de l'api flask
    app.run(debug=True, host='0.0.0.0', port=3333)
