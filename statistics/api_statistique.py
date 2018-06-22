#!/usr/bin/python
# coding: utf8


# BABY FOOT Connecté
# Programme pour : Stat des joeurs & Matchs + Score
# Juin 2017
# Others indicators : Match,Victoires,Défaites,Plus longue série de victoires,Buts marqués ,Bus encaissés ,Score moyen ,Score Meilleur match,Score pire défaite
# Adversaire favoris (plus de victoires) ,Adversaire redoutable (plus de défaites) ,Meilleur partenaire (plus de victoires) ,Pire partenaire (plus de défaites)


# Import librairies python
import pandas as pd
import numpy as np
import datetime
import logging as lg

t = datetime.datetime.now()
fn = 'logs/run_statistique.{}.log'.format(t.strftime("%Y-%m-%d"))

lg.basicConfig(filename = fn,
               level = lg.DEBUG,
               filemode = 'a',
               format = '%(asctime)s\t%(levelname)s\t%(message)s',
               datefmt = '%Y-%m-%d %H:%M:%S'
               )


# Initialisation de SQLite
import sys
sys.path.append("data")
import fonction_database
sys.path.append("statistics/lib")
import fonction_statistiques

# Pour la partie API
from flask import Flask, Response, request
app = Flask(__name__)
lg.info("LANCEMENT API STATISTIQUE")

# Import du référentiel joueur
lg.info("Récupération de la liste des users dans le referentiel")
cur, conn = fonction_database.fonction_connexion_sqllite()
ref_player = pd.read_sql_query("select * from PROD_REF_PLAYERS;", conn)
fonction_database.fonction_connexion_sqllite_fermeture(cur, conn)
lg.info("Récupération de la liste des users dans le referentiel - OK")

# created a *threaded* video stream, allow the camera sensor to warmup,
@app.route('/calcul_statistique')
def calcul_statistique():
    ####################################""
    # Requêtage sur la table d'histo match
    lg.info("Appel de la fonction statistique")
    cur, conn = fonction_database.fonction_connexion_sqllite()
    input_match_df = pd.read_sql_query(
        "select a.* from PROD_LIVE_MATCH_HISTO as a INNER JOIN (SELECT distinct id_match FROM PROD_LIVE_MATCH_HISTO WHERE score_b = 10 OR score_r = 10) as b ON a.id_match = b.id_match;",
        conn)
    fonction_database.fonction_connexion_sqllite_fermeture(cur, conn)

    lg.info("Récupération du dernier match")
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
    col = ['match_count', 'match_win_count', 'match_los_count', 'game_time_sec', 'goals_scored', 'goals_conceced'
            , 'worst_score', 'best_score'
            #, 'bad_los_score', 'best_win_score', 'mean_score'
            ,'best_partner', 'bad_partner', 'bad_adver', 'best_adver']

    lg.info("Début du calcul par player")
    resume_players = pd.DataFrame(columns=col)
    for player in players:
        # keep only match played
        match = resume_match_df[player == resume_match_df[['winner_id1', 'winner_id2', 'loser_id1', 'loser_id2']].values]
        # generate stats
        match_count = match.shape[0]
        match_win_count = match[player == match[['winner_id1', 'winner_id2']].values].shape[0]
        match_los_count = match[player == match[['loser_id1', 'loser_id2']].values].shape[0]
        game_time_sec = match.time_duration.sum()
        goals_scored = sum([match[player == match[['winner_id1', 'winner_id2']].values].goal_winner.sum(),
                            match[player == match[['loser_id1', 'loser_id2']].values].goal_loser.sum()])
        goals_conceced = sum([match[player == match[['winner_id1', 'winner_id2']].values].goal_loser.sum(),
                              match[player == match[['loser_id1', 'loser_id2']].values].goal_winner.sum()])
        worst_score = np.nanmin([match[player == match[['loser_id1', 'loser_id2']].values].goal_loser.min(),
                                 match[player == match[['winner_id1', 'winner_id2']].values].goal_winner.min()])
        best_score = np.nanmax([match[player == match[['loser_id1', 'loser_id2']].values].goal_loser.max(),
                                match[player == match[['winner_id1', 'winner_id2']].values].goal_winner.max()])

        # Calcul de best / bad partenaire
        temp1 = match[player == match[['winner_id1', 'winner_id2']].values].groupby(['winner_id1', 'winner_id2']).agg(
            {'id_match': 'count', 'goal_loser': sum, 'time_duration': sum}).reset_index()
        temp1['player_id'] = player
        temp1['winner_id'] = 0
        temp1.loc[temp1['player_id'] == temp1['winner_id1'], 'winner_id'] = temp1['winner_id2']
        temp1.loc[temp1['player_id'] == temp1['winner_id2'], 'winner_id'] = temp1['winner_id1']
        temp1 = temp1[player == temp1[['player_id']].values].groupby(['player_id', 'winner_id']).agg(
            {'id_match': sum, 'goal_loser': sum, 'time_duration': sum}).reset_index()
        temp1 = temp1.sort_values(by=['id_match', 'goal_loser', 'time_duration'], ascending=[False, True, True])
        try:
            best_partner = temp1.iloc[0, :]['winner_id']
            bad_partner = temp1.iloc[temp1.shape[0] - 1, :]['winner_id']
        except:
            best_partner=110
            bad_partner=110

        # Calcul de best / bad adversaire
        temp1 = match[player == match[['loser_id1', 'loser_id2']].values].groupby(['loser_id1', 'loser_id2']).agg(
            {'id_match': 'count', 'goal_loser': sum, 'time_duration': sum}).reset_index()
        temp1['player_id'] = player
        temp1['los_id'] = 0
        temp1.loc[temp1['player_id'] == temp1['loser_id1'], 'los_id'] = temp1['loser_id2']
        temp1.loc[temp1['player_id'] == temp1['loser_id2'], 'los_id'] = temp1['loser_id1']
        temp1 = temp1[player == temp1[['player_id']].values].groupby(['player_id', 'los_id']).agg(
            {'id_match': sum, 'goal_loser': sum, 'time_duration': sum}).reset_index()
        temp1 = temp1.sort_values(by=['id_match', 'goal_loser', 'time_duration'], ascending=[False, False, False])
        try:
            bad_adver = temp1.iloc[0, :]['los_id']
            best_adver = temp1.iloc[temp1.shape[0] - 1, :]['los_id']
        except:
            bad_adver = 110
            best_adver = 110
                  
        # create temp dataframe for player
        resume_player = pd.DataFrame(np.array([[match_count, match_win_count, match_los_count, game_time_sec,goals_scored, goals_conceced, worst_score, best_score,best_partner, bad_partner, bad_adver, best_adver]]), index=[player],columns=col)
        resume_players['best_partner'] = resume_players['best_partner'].astype('int')
        resume_players['best_adver'] = resume_players['best_adver'].astype('int')
        resume_players['bad_partner'] = resume_players['bad_partner'].astype('int')
        resume_players['bad_adver'] = resume_players['bad_adver'].astype('int')
		
        # concat resume_player with resume_players
        resume_players = pd.concat([resume_players, resume_player], axis=0)

    # generate other stats
    resume_players['match_win_percent'] = resume_players.match_win_count / resume_players.match_count * 100
    resume_players['goals_diff'] = resume_players.goals_scored - resume_players.goals_conceced
    resume_players['goal_per_minut'] = resume_players.goals_scored / (resume_players.game_time_sec / 60)
    resume_players = resume_players.sort_values(by=['match_win_count', 'match_win_percent'], ascending=False)
    resume_players['ranking'] = range(1, len(resume_players.match_win_count) + 1)

    # Création du player_id final
    resume_players = resume_players.rename_axis("player_id").reset_index().rename(index=str,columns={"player_id": "player_id_vf"})
    # Jointure bad / best adversaire & Partner
    resume_players = pd.merge(resume_players, ref_player, how='left', left_on=['best_partner'], right_on=['id_player'])
    resume_players = resume_players.rename(index=str, columns={"firstname": "firstname_best_partner"})
    resume_players = resume_players.rename(index=str, columns={"lastname": "lastname_best_partner"})
    resume_players = resume_players.rename(index=str, columns={"nickname": "nickname_best_partner"})
    resume_players = resume_players.drop(['id_player'], axis=1)
    resume_players = pd.merge(resume_players, ref_player, how='left', left_on=['bad_partner'], right_on=['id_player'])
    resume_players = resume_players.rename(index=str, columns={"firstname": "firstname_bad_partner"})
    resume_players = resume_players.rename(index=str, columns={"lastname": "lastname_bad_partner"})
    resume_players = resume_players.rename(index=str, columns={"nickname": "nickname_bad_partner"})
    resume_players = resume_players.drop(['id_player'], axis=1)
    resume_players = pd.merge(resume_players, ref_player, how='left', left_on=['bad_adver'], right_on=['id_player'])
    resume_players = resume_players.rename(index=str, columns={"firstname": "firstname_bad_adver"})
    resume_players = resume_players.rename(index=str, columns={"lastname": "lastname_bad_adver"})
    resume_players = resume_players.rename(index=str, columns={"nickname": "nickname_bad_adver"})
    resume_players = resume_players.drop(['id_player'], axis=1)
    resume_players = pd.merge(resume_players, ref_player, how='left', left_on=['best_adver'], right_on=['id_player'])
    resume_players = resume_players.rename(index=str, columns={"firstname": "firstname_best_adver"})
    resume_players = resume_players.rename(index=str, columns={"lastname": "lastname_best_adver"})
    resume_players = resume_players.rename(index=str, columns={"nickname": "nickname_best_adver"})
    resume_players = resume_players.drop(['id_player'], axis=1)
    resume_players_df = resume_players.rename(index=str, columns={"player_id_vf": "id_player"})

    # Jointure des player_id avec la base ref
    import sqlalchemy
    lg.info("Sauvegarde de la table dans sqlite")

    resume_players_df_vf = pd.merge(ref_player, resume_players_df)
    cur, conn = fonction_database.fonction_connexion_sqllite()
    
    resume_players_df_vf['match_count'] = resume_players_df_vf['match_count'].astype('int')
    resume_players_df_vf['match_win_count'] = resume_players_df_vf['match_win_count'].astype('int')
    resume_players_df_vf['match_los_count'] = resume_players_df_vf['match_los_count'].astype('int')
    resume_players_df_vf['goals_scored'] = resume_players_df_vf['goals_scored'].astype('int')
    resume_players_df_vf['goals_conceced'] = resume_players_df_vf['goals_conceced'].astype('int')
    resume_players_df_vf['match_win_percent'] = resume_players_df_vf['match_win_percent'].astype('int')
    
    resume_players_df_vf['game_time_sec']=resume_players_df_vf['game_time_sec'].astype('int')
    resume_players_df_vf['goal_per_minut'] = resume_players_df_vf['goal_per_minut'].astype('float')
    resume_players_df_vf['best_partner'] = resume_players_df_vf['best_partner'].astype('int')
    resume_players_df_vf['bad_partner'] = resume_players_df_vf['bad_partner'].astype('int')
    resume_players_df_vf['best_adver'] = resume_players_df_vf['best_adver'].astype('int')
    resume_players_df_vf['bad_adver'] = resume_players_df_vf['bad_adver'].astype('int')
    resume_players_df_vf.to_sql('PROD_STAT_PLAYERS', conn, index=False, if_exists='replace')
    fonction_database.fonction_connexion_sqllite_fermeture(cur, conn)

    lg.info("FIN DE LA FONCTION")
    return "ok"

# Lancement de l'app
if __name__ == '__main__':
    # Lancement de l'api flask
    app.run(debug=True, host='0.0.0.0', port=3333)



