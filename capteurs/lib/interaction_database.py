# !/usr/bin/python
# coding: utf8

import sys

sys.path.append('data')
import fonction_database


# Fonction d'ajout de données dans la table
# Update de la table Live avec le time du but, et les scores des Bleus et Rouge
def live(time_goal_str, i, j):
    connexion, requete = fonction_database.fonction_connexion_sqllite()
    requete.execute("UPDATE PROD_LIVE_MATCH SET time_goal=?, score_b=?, score_r=?", (time_goal_str, i, j))
    connexion.commit()
    fonction_database.fonction_connexion_sqllite_fermeture(requete, connexion)
