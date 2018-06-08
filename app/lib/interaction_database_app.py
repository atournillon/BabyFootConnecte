# !/usr/bin/python
# coding: utf8

import sys
sys.path.append("data")
import fonction_database
import pandas as pd
import datetime
import time

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
    except:
        pass
    return score_b, score_r


def get_players():
    #Load Players Table
    cur,conn= fonction_database.fonction_connexion_sqllite()
    query = "SELECT * FROM PROD_REF_PLAYERS"
    df_players = pd.read_sql(query, cur)
    fonction_database.fonction_connexion_sqllite_fermeture(cur,conn)
    return df_players

#  Initalisation de la fonction de vidage des tables
def purge_live_match():
    cur, conn = fonction_database.fonction_connexion_sqllite()
    # Purge de la table contenant le live du match
    cur.execute("DELETE FROM PROD_LIVE_MATCH")
    fonction_database.fonction_connexion_sqllite_fermeture(cur,conn)

#Function to insert data on PROD_LIVE_MATCH when livematch.html is loaded
def init_prod_live_match():
    cur, conn = fonction_database.fonction_connexion_sqllite()
    time_match = datetime.datetime.now()
    id_match = int(time.mktime(time_match.timetuple()))
    b1 = 0
    b2 = 0
    r1 = 0
    r2 = 0
    score_b = 0
    score_r = 0
    time_match_str = str('{0:%Y-%m-%d %H:%M:%S}'.format(time_match))
    cur.execute("INSERT INTO PROD_LIVE_MATCH values((?), (?), (?), (?), (?), (?), null, (?), (?))", (id_match, b1, b2, r1, r2,time_match_str, score_b, score_r))
    fonction_database.fonction_connexion_sqllite_fermeture(cur,conn)

def recup_players_stat():
    cur, conn = fonction_database.fonction_connexion_sqllite()
    query = "SELECT * FROM PROD_STAT_PLAYERS LIMIT 5"
    df_sortie = pd.read_sql(query, cur).set_index('id_player')
    fonction_database.fonction_connexion_sqllite_fermeture(cur,conn)
    return df_sortie
