#!/usr/bin/python
#coding: utf8


#_______________________________________________________________________
# BABY FOOT Connecté
# Programme pour : Stat des joeurs & Matchs + Score
# Juin 2017
#_______________________________________________________________________

#Others indicators : Match,Victoires,Défaites,Plus longue série de victoires,Buts marqués ,Bus encaissés ,Score moyen ,Score Meilleur match,Score pire défaite
#Adversaire favoris (plus de victoires) ,Adversaire redoutable (plus de défaites) ,Meilleur partenaire (plus de victoires) ,Pire partenaire (plus de défaites)

#Import librairies python
import pandas as pd, numpy as np, datetime

#Initialisation de SQLite
import sqlite3 as sql                                                                          #Import de SQLite
import sys

connexion = sql.connect('data/PARC_DES_PRINCES.db')                                                        #Nom de la base
requete=connexion.cursor()

#Requêtage sur la table d'histo match
input_match_df = pd.read_sql_query("select * from PROD_LIVE_MATCH_HISTO;", connexion)

################## functions #############################
##########################################################

def time_function(df):
    df['time_goal'] = pd.to_datetime(df['time_goal'])
    df = df.groupby('id_match', as_index=False).agg(['min','max'])['time_goal']
    df['time_start'] = pd.to_datetime(df['min'])
    df['time_end'] = pd.to_datetime(df['max'])
    print df
    df['time_duration'] = df['time_end'] - df['time_start']
    df['time_duration'] = df['time_duration'].dt.total_seconds().astype(int)
    col_keep = ['time_start','time_end','time_duration']
    return df[col_keep]


def players_function(df):
    # players count
    df['players_count_dom'] = df[['b1','b2']].count(axis=1)
    df['players_count_ext'] = df[['r1','r2']].count(axis=1)
    df['players_count_all'] = df[['b1','b2','r1','r2']].count(axis=1)
    # players list
    df['players_list_all'] = df['b1'].astype(str)+'-'+df['b2'].astype(str)+'-'+df['r1'].astype(str)+'-'+df['r2'].astype(str)
    df['players_list_dom'] = df['b1'].astype(str)+'-'+df['b2'].astype(str)
    df['players_list_ext'] = df['r1'].astype(str)+'-'+df['r2'].astype(str)
    df = df.groupby('id_match', as_index=False).agg(['max'])
    # keep columns and drop level
    df.columns = df.columns.droplevel(1)
    col_keep = ['players_count_all','players_count_dom','players_count_ext','players_list_all','players_list_dom','players_list_ext']
    df = df[col_keep]
    return df


def results_function(df):
    # create 2 dataframe for domicile and ext winner with filter. Traitments and concat two DF
    # if team domicile win : filter match with domicile winner
    # filter each dataframe for winners domicile or ext
    df_dom_win = df[df.score_b==10]
    df_ext_win = df[df.score_r==10]
    # if dom. team win :
    df_dom_win['winner_loc'] = 'domicile'
    df_dom_win['winner_id1'] = df_dom_win[['b1','b2']].min(axis=1)
    df_dom_win['winner_id2'] = df_dom_win[['b1','b2']].max(axis=1)
    df_dom_win['loser_id1'] = df_dom_win[['r1','r2']].min(axis=1)
    df_dom_win['loser_id2'] = df_dom_win[['r1','r2']].max(axis=1)
    df_dom_win['winners_list_id'] = df_dom_win['winner_id1'].astype(str)+ '-' + df_dom_win['winner_id2'].astype(str)
    df_dom_win['losers_list_id'] = df_dom_win['loser_id1'].astype(str) + '-' + df_dom_win['loser_id2'].astype(str)
    df_dom_win['goal_winner'] = 10
    df_dom_win['goal_loser'] = df_dom_win[['score_r']]
    df_dom_win['goal_difference'] = 10 - df_dom_win[['score_r']]
    df_dom_win.reset_index()
    #if ext. team win :
    df_ext_win['winner_loc'] = 'exterieur'
    df_ext_win['winner_id1'] = df_ext_win[['r1','r2']].min(axis=1)
    df_ext_win['winner_id2'] = df_ext_win[['r1','r2']].max(axis=1)
    df_ext_win['loser_id1'] = df_ext_win[['b1','b2']].min(axis=1)
    df_ext_win['loser_id2'] = df_ext_win[['b1','b2']].max(axis=1)
    df_ext_win['winners_list_id'] = df_ext_win['winner_id1'].astype(str)+ '-' + df_ext_win['winner_id2'].astype(str)
    df_ext_win['losers_list_id'] = df_ext_win['loser_id1'].astype(str) + '-' + df_ext_win['loser_id2'].astype(str)
    df_ext_win['goal_winner'] = 10
    df_ext_win['goal_loser'] = df_ext_win[['score_b']]
    df_ext_win['goal_difference'] = 10 - df_ext_win[['score_b']]
    df_ext_win.reset_index()
    # concat two dataframe
    df_concat = pd.concat([df_dom_win,df_ext_win],axis=0).set_index('id_match').sort_index()
    print(df_concat.columns)
    df_concat = df_concat.drop(['b1','b2','r1','r2','score_b','score_r'],axis=1)
    return df_concat

############ preprocessing ####################
# compute dataframe with one row per match : id_match / start_time / end_time / duration / players_dom / players_etx /
# winers / losers / score_win / score_los / score_diff / goal_per_min_win / goal_per_min_los
###############################################

#### time_function
columns_time = ['id_match','time_goal']
match_time = time_function(input_match_df[columns_time])

#### match_players
columns_players = ['id_match','b1','b2','r1','r2']
match_players = players_function(input_match_df[columns_players])

#### match_results : winner_id1 / winner_id2 / losers_id1 / loser_id2 / goal_winners / goal_losers / goal_difference
columns_results = ['id_match','b1','b2','r1','r2','score_b','score_r']
match_results = results_function(input_match_df[columns_results][(input_match_df.score_b == 10) | (input_match_df.score_r==10)])

############### join all parts ################
# join all dataframe by id_match
###############################################

resume_match_df = pd.concat([match_time, match_players,match_results],axis=1).reset_index()

# new dataframe with all players
players = pd.unique(resume_match_df[['winner_id1', 'winner_id2','loser_id1', 'loser_id2']].values.ravel('K'))

#Loop for each player ?
col = ['match_count','match_win_count','match_los_count','game_time_sec','goals_win_count','goals_los_count']
resume_players = pd.DataFrame(columns=col)


for player in players :
    # keep only match played
    match = resume_match_df[player == resume_match_df[['winner_id1', 'winner_id2','loser_id1', 'loser_id2']].values]

    # generate stats
    match_count = match.shape[0]
    match_win_count = match[player == match[['winner_id1', 'winner_id2']].values].shape[0]
    match_los_count = match[player == match[['loser_id1', 'loser_id2']].values].shape[0]
    game_time_sec = match.time_duration.sum()
    goals_win_count = match[player == match[['winner_id1', 'winner_id2']].values].goal_winner.sum()
    goals_los_count = match[player == match[['loser_id1', 'loser_id2']].values].goal_loser.sum()

    # create temp dataframe for player
    resume_player = pd.DataFrame(np.array([[match_count, match_win_count, match_los_count,game_time_sec,
                                           goals_win_count,goals_los_count]]), index = [player], columns=col)

    # concat resume_player with resume_players
    resume_players = pd.concat([resume_players,resume_player],axis=0)



# generate other stats
resume_players['match_win_percent'] = resume_players.match_win_count / resume_players.match_count
resume_players['goals_count'] = resume_players.goals_win_count + resume_players.goals_los_count
resume_players['goal_per_minut'] = resume_players.goals_count / (resume_players.game_time_sec/60)

resume_players_df = resume_players.rename_axis("id_player").reset_index()

#Jointure avec le référentiel joueur
ref_player=pd.read_sql_query("select * from PROD_REF_PLAYERS;", connexion)

resume_players_df_vf=pd.merge(ref_player,resume_players_df)

resume_players_df_vf.to_sql('PROD_STAT_PLAYERS',connexion, index=False, if_exists='replace')
