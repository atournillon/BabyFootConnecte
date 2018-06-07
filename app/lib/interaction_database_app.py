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
        conn_thr,curs_thr=fonction_database.fonction_connexion_sqllite()
        table = curs_thr.execute("SELECT * FROM PROD_LIVE_MATCH").fetchall()
        fonction_database.fonction_connexion_sqllite_fermeture(conn_thr,curs_thr)

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
    conn, cur= fonction_database.fonction_connexion_sqllite()
    query = "SELECT * FROM PROD_REF_PLAYERS"
    df_players = pd.read_sql(query, conn)
    fonction_database.fonction_connexion_sqllite_fermeture(conn,cur)
    return df_players

#  Initalisation de la fonction de vidage des tables
def purge_live_match():
    conn, cur = fonction_database.fonction_connexion_sqllite()
    # Purge de la table contenant le live du match
    cur.execute("DELETE FROM PROD_LIVE_MATCH")
    fonction_database.fonction_connexion_sqllite_fermeture(conn,cur)

#Function to insert data on PROD_LIVE_MATCH when livematch.html is loaded
def init_prod_live_match():
    conn, cur = fonction_database.fonction_connexion_sqllite()
    id_match = int(time.mktime(datetime.datetime.now().timetuple()))
    b1 = 0
    b2 = 0
    r1 = 0
    r2 = 0
    score_b = 0
    score_r = 0
    cur.execute("INSERT INTO PROD_LIVE_MATCH values((?), (?), (?), (?), (?), datetime('now'), datetime('now'), (?), (?))", (id_match, b1, b2, r1, r2, score_b, score_r))
    fonction_database.fonction_connexion_sqllite_fermeture(conn,cur)

def recup_players_stat():
    conn, cur = fonction_database.fonction_connexion_sqllite()
    query = "SELECT * FROM PROD_STAT_PLAYERS LIMIT 5"
    df_sortie = pd.read_sql(query, conn).set_index('id_player')
    fonction_database.fonction_connexion_sqllite_fermeture(conn,cur)
    return df_sortie
