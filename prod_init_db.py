#!/usr/bin/python
#coding: utf8

# Chargement des packages
import sqlite3 as sql
import time
from datetime import datetime
import pandas as pd

# Base de recette
connexion = sql.connect('data/PARC_DES_PRINCES.db')

# Visualiser la base SQL
# Télécharger PARC_DES_PRINCES.DB puis sur https://sqliteonline.com/ -> File -> Open DB

# Connexion
requete = connexion.cursor()

# Initialisation de la fonction de création des tables
def CreateTable():
    # Création de la table du live du match
    requete.execute('''CREATE TABLE IF NOT EXISTS PROD_LIVE_MATCH
    (id_match INTEGER, b1 INTEGER, b2 INTEGER, r1 INTEGER, r2 INTEGER, time_start DATETIME, time_goal DATETIME, score_b INTEGER, score_r INTEGER)''')
    # Création de la table d'historisation des lives de match
    requete.execute('''CREATE TABLE IF NOT EXISTS PROD_LIVE_MATCH_HISTO
    (id_match INTEGER, b1 INTEGER, b2 INTEGER, r1 INTEGER, r2 INTEGER, time_start DATETIME, time_goal DATETIME, score_b INTEGER, score_r INTEGER)''')
    requete.execute('''CREATE TABLE IF NOT EXISTS PROD_STAT_PLAYERS
    (id_player INTEGER, match_count INTEGER, match_win_count INTEGER, match_los_count INTEGER, game_time_sec INTEGER,
     goals_win_count INTEGER, goals_los_count INTEGER, match_win_percent REAL, goals_count INTEGER, goal_per_minut REAL
     , prenom TEXT , nom TEXT , trigram TEXT)''')
    
# Initialisation de la fonction contenant le déclencheur
def Trigger():
    # Initialisation du Trigger permettant de copier PROD_LIVE_MATCH dans PROD_LIVE_MATCH_HISTO
    requete.execute('''CREATE TRIGGER IF NOT EXISTS MAJ_HISTO_MATCH 
    AFTER UPDATE OF id_match, b1, b2, r1, r2, time_start, time_goal, score_b, score_r
    ON PROD_LIVE_MATCH
    BEGIN insert into PROD_LIVE_MATCH_HISTO  
    SELECT id_match, b1, b2, r1, r2, time_start, time_goal, score_b, score_r
    FROM PROD_LIVE_MATCH;
    END
    ''')
    requete.execute('''CREATE TRIGGER IF NOT EXISTS MAJ_HISTO_MATCH2 
    AFTER INSERT OF id_match, b1, b2, r1, r2, time_start, time_goal, score_b, score_r
    ON PROD_LIVE_MATCH
    BEGIN insert into PROD_LIVE_MATCH_HISTO  
    SELECT id_match, b1, b2, r1, r2, time_start, time_goal, score_b, score_r
    FROM PROD_LIVE_MATCH;
    END
    ''')

#  Initalisation de la fonction de vidage des tables
def PurgeLiveMatch():
    # Purge de la table contenant le live du match
    requete.execute('''DELETE FROM PROD_LIVE_MATCH''')

# Appel de la fonction de création des tables
CreateTable()

# Appel de la fonction du trigger
Trigger()

# Appel de la fonction de vidage des tables
PurgeLiveMatch()

# Soumission des fonctions précédemment appelées
connexion.commit()

# Importation des commentaires et des joueurs depuis les dictionnaires vers SQLITE3
wb=pd.read_excel('data/dictionnaire_commentaires.xlsx',sheet_name=None)
wb2=pd.read_excel('data/dictionnaire_joueurs.xlsx',sheet_name=None)
"""
if_exists : {'fail', 'replace', 'append'}, default 'fail'
    - fail: If table exists, do nothing.
    - replace: If table exists, drop it, recreate it, and insert data.
    - append: If table exists, insert data. Create if does not exist.
"""
for sheet in wb:
    wb[sheet].to_sql('PROD_REF_COMMENTS',connexion, index=False, if_exists='replace')
for sheet in wb2:
    wb2[sheet].to_sql('PROD_REF_PLAYERS',connexion, index=False, if_exists='replace')
    
# 1 ) Les logs de match
#logs_match = pd.read_csv('data/logs_match.csv', sep = ';')
#logs_match.to_sql('PROD_LIVE_MATCH_HISTO',connexion, index=False, if_exists='replace')

# Déconnexion de la base
requete.close()
