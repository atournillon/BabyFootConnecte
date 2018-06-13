# !/usr/bin/python
# coding: utf8

import sys

sys.path.append('data')
import fonction_database


# Fonction d'ajout de données dans la table
# Update de la table Live avec le time du but, et les scores des Bleus et Rouge
def live(time_goal_str, i, j, Last_Goal):
    requete, connexion = fonction_database.fonction_connexion_sqllite()
    requete.execute("UPDATE PROD_LIVE_MATCH SET time_goal=?, score_b=?, score_r=?, last_team=?", (time_goal_str, i, j, Last_Goal))
    fonction_database.fonction_connexion_sqllite_fermeture(requete, connexion)


#  Initalisation de la fonction de vidage des tables
def purge_live_match():
    cur, conn = fonction_database.fonction_connexion_sqllite()
    # Purge de la table contenant le live du match
    cur.execute("DELETE FROM PROD_LIVE_MATCH")
    fonction_database.fonction_connexion_sqllite_fermeture(cur,conn)
    
# Fonction de lecture des données de Live
def read_live():
    requete, connexion = fonction_database.fonction_connexion_sqllite()
    table = requete.execute("SELECT * FROM PROD_LIVE_MATCH").fetchall()
    row = table[0] #Just one line in the table
    score_b = row[7]
    score_r = row[8]
    fonction_database.fonction_connexion_sqllite_fermeture(requete, connexion)
    return score_b, score_r
