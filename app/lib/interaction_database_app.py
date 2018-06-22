# !/usr/bin/python
# coding: utf8

import sys
sys.path.append("data")
import fonction_database
import pandas as pd
import datetime
import time
import logging as lg


# Retrieve data from database
def getData():
    try:
        curs_thr, conn_thr = fonction_database.fonction_connexion_sqllite()
        table = curs_thr.execute("SELECT * FROM PROD_LIVE_MATCH").fetchall()
        fonction_database.fonction_connexion_sqllite_fermeture(curs_thr,conn_thr)
        if len(table) == 0:
            return '/', '/'
        else:
            row = table[0] #Just one line in the table
            score_b = row[7]
            score_r = row[8]
    except Exception as e:
        lg.error("PROBLEME WEBSOCKET : {]".format(e))
        pass
    return score_b, score_r

''' FONCTION PERMETTANT DE RECUPERER LA LISTE DES JOUEURS DE LA TABLE DE REF'''
def get_players():
    #Load Players Table
    cur,conn= fonction_database.fonction_connexion_sqllite()
    query = "SELECT * FROM PROD_REF_PLAYERS"
    df_players = pd.read_sql(query, conn)
    fonction_database.fonction_connexion_sqllite_fermeture(cur,conn)
    lg.info('RECUPERATION DE LA LISTE DES JOUEURS OK')
    return df_players

#  Initalisation de la fonction de vidage des tables
def purge_live_match():
    cur, conn = fonction_database.fonction_connexion_sqllite()
    # Purge de la table contenant le live du match
    cur.execute("DELETE FROM PROD_LIVE_MATCH")
    fonction_database.fonction_connexion_sqllite_fermeture(cur,conn)
    lg.info('PURGE DE LA TABLE PROD_LIVE_MATCH OK')

#Function to insert data on PROD_LIVE_MATCH when livematch.html is loaded
def init_prod_live_match(r1,r2,b1,b2):
    cur, conn = fonction_database.fonction_connexion_sqllite()
    time_match = datetime.datetime.now()
    id_match = int(time.mktime(time_match.timetuple()))
    score_b = 0
    score_r = 0
    time_match_str = str('{0:%Y-%m-%d %H:%M:%S}'.format(time_match))
    time_goal_init_str = str('{0:%d/%m/%Y %H:%M:%S}'.format(time_match))
    last_team = 0
    cur.execute("INSERT INTO PROD_LIVE_MATCH values((?), (?), (?), (?), (?), (?), (?), (?), (?), (?))", (id_match, b1, b2, r1, r2,time_match_str,time_goal_init_str, score_b, score_r, last_team))
    fonction_database.fonction_connexion_sqllite_fermeture(cur,conn)

def recup_players_stat():
    cur, conn = fonction_database.fonction_connexion_sqllite()
    query = "SELECT * FROM PROD_STAT_PLAYERS WHERE ID_PLAYER > 0 ORDER BY match_win_percent DESC "
    df_sortie = pd.read_sql(query, conn).set_index('id_player')
    df_sortie['game_time_sec']=df_sortie['game_time_sec'].apply(lambda x : str(datetime.timedelta(seconds=x)))
    fonction_database.fonction_connexion_sqllite_fermeture(cur,conn)
    return df_sortie


def perte_un_but():
    cur, conn = fonction_database.fonction_connexion_sqllite()
    table = cur.execute("SELECT * FROM PROD_LIVE_MATCH").fetchall()
    row = table[0] #Just one line in the table
    bleu = row[7]
    rouge = row[8]
    last = row[9]
    if last == 1 and bleu > 0:
    	query_2 = "UPDATE PROD_LIVE_MATCH SET score_b=score_b-1, last_team = 0;"
    if last == 2 and rouge > 0:
    	query_2 = "UPDATE PROD_LIVE_MATCH SET score_r=score_r-1, last_team = 0;"
    cur.execute(query_2)
    fonction_database.fonction_connexion_sqllite_fermeture(cur,conn)
    lg.info("ON SUPPRIME UN BUT")
    return 'ok'
    
def gamelle_bleu():
    cur, conn = fonction_database.fonction_connexion_sqllite()
    table = cur.execute("SELECT * FROM PROD_LIVE_MATCH").fetchall()
    row = table[0] #Just one line in the table
    bleu = row[7]
    rouge = row[8]
    if rouge > 0:
        query = "UPDATE PROD_LIVE_MATCH SET score_r=score_r-1, last_team = 0;"
    cur.execute(query)
    fonction_database.fonction_connexion_sqllite_fermeture(cur,conn)
    lg.info("GAMELLE DES BLEUS - ON SUPPRIME UN BUT DES ROUGES")
    return 'ok'
    
def gamelle_rouge():
    cur, conn = fonction_database.fonction_connexion_sqllite()
    table = cur.execute("SELECT * FROM PROD_LIVE_MATCH").fetchall()
    row = table[0] #Just one line in the table
    bleu = row[7]
    rouge = row[8]
    if bleu > 0:
        query = "UPDATE PROD_LIVE_MATCH SET score_b=score_b-1, last_team = 0;"
    cur.execute(query)
    fonction_database.fonction_connexion_sqllite_fermeture(cur,conn)
    lg.info("GAMELLE DES ROUGE - ON SUPPRIME UN BUT DES BLEUS")
    return 'ok'

def recup_prenom_nom(j1,j2):
    cur, conn = fonction_database.fonction_connexion_sqllite()
    query = "SELECT * FROM PROD_REF_PLAYERS WHERE id_player = {} " \
            "UNION ALL " \
            "SELECT * FROM PROD_REF_PLAYERS WHERE id_player={}".format(str(j1),str(j2))
    df_sortie = pd.read_sql(query, conn)
    fonction_database.fonction_connexion_sqllite_fermeture(cur,conn)
    return df_sortie
