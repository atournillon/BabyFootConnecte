# Chargement des packages
import sqlite3 as sql
import time
from datetime import datetime
import pandas as pd

# Base de recette
connexion = sql.connect('data/PARC_DES_PRINCES.db')

# Connexion
requete = connexion.cursor()

# Initialisation de la fonction de création des tables
def CreateTable():
    # Création de la table du live du match
    requete.execute('''CREATE TABLE IF NOT EXISTS PROD_LIVE_MATCH
    (id_match INTEGER PRIMARY KEY, b1 INTEGER, b2 INTEGER, r1 INTEGER, r2 INTEGER, time_start DATETIME, time_goal DATETIME, score_b INTEGER, score_r INTEGER)''')
    # Création de la table d'historisation des lives de match
    requete.execute('''CREATE TABLE IF NOT EXISTS PROD_LIVE_MATCH_HISTO
    (id_match INTEGER PRIMARY KEY, b1 INTEGER, b2 INTEGER, r1 INTEGER, r2 INTEGER, time_start DATETIME, time_goal DATETIME, score_b INTEGER, score_r INTEGER)''')
    # Création de la table contenant le référentiel des joueurs
    requete.execute('''CREATE TABLE IF NOT EXISTS PROD_REF_PLAYERS
    (id_player INTEGER PRIMARY KEY, firstname TEXT, lastname TEXT, nickname TEXT)''')
    
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

# Importation des commentaires depuis le dictionnaire vers SQLITE
# requete.execute('''DROP TABLE PROD_REF_COMMENTS''')
wb=pd.read_excel('data/dictionnaire_commentaires.xlsx',sheet_name=None)
"""
if_exists : {'fail', 'replace', 'append'}, default 'fail'
    - fail: If table exists, do nothing.
    - replace: If table exists, drop it, recreate it, and insert data.
    - append: If table exists, insert data. Create if does not exist.
"""
for sheet in wb:
    wb[sheet].to_sql('PROD_REF_COMMENTS',connexion, index=False, if_exists='replace')

# Soumission des fonctions précédemment appelées
connexion.commit()

# Déconnexion de la base
requete.close()