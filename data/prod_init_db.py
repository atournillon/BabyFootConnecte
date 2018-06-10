#!/usr/bin/python
#coding: utf8

# Chargement des packages
import sys
import logging as lg
import sqlite3 as sql
import time
import datetime
import pandas as pd
import json
sys.path.append("data")
import fonction_database

# Visualiser la base SQL
# Télécharger PARC_DES_PRINCES.DB puis sur https://sqliteonline.com/ -> File -> Open DB

# Initialisation de la log
t = datetime.datetime.now()
fn = 'logs/init_db.{}.log'.format(t.strftime("%Y-%m-%d"))
lg.basicConfig(filename = fn,
               level = lg.DEBUG,
               filemode = 'a',
               format = '%(asctime)s\t%(levelname)s\t%(message)s',
               datefmt = '%Y-%m-%d %H:%M:%S'
               )

try:
    lg.info("Chargement de la base à partir du fichier de configuration")
    with open('config.json') as conf_file:
        global DB
        DB = json.load(conf_file)
        
except:
    lg.info("Erreur lors du chargement de la base à partir du fichier de configuration")
    
else:
    lg.info("Chargement de la base OK")
    
    lg.info("Ouverture de la base")
    connexion,requete = fonction_database.fonction_connexion_sqllite()
    
    # Initialisation de la fonction de création des tables
    def CreateTable():
        # Création de la table du live du match
        requete.execute('''CREATE TABLE IF NOT EXISTS PROD_LIVE_MATCH
        (id_match INTEGER, b1 INTEGER, b2 INTEGER, r1 INTEGER, r2 INTEGER, time_start DATETIME, time_goal DATETIME, score_b INTEGER, score_r INTEGER, last_team INTEGER)''')
        # Création de la table d'historisation des lives de match
        requete.execute('''CREATE TABLE IF NOT EXISTS PROD_LIVE_MATCH_HISTO
        (id_match INTEGER, b1 INTEGER, b2 INTEGER, r1 INTEGER, r2 INTEGER, time_start DATETIME, time_goal DATETIME, score_b INTEGER, score_r INTEGER, last_team INTEGER)''')
        # Création de la table des stats
        requete.execute('''CREATE TABLE IF NOT EXISTS PROD_STAT_PLAYERS
        (id_player INTEGER, match_count INTEGER, match_win_count INTEGER, match_los_count INTEGER, game_time_sec INTEGER,
         goals_win_count INTEGER, goals_los_count INTEGER, match_win_percent REAL, goals_count INTEGER, goal_per_minut REAL
         , prenom TEXT , nom TEXT , trigram TEXT)''')
        
    # Initialisation de la fonction contenant le déclencheur
    def Trigger():
        # Historisation après un INSERT
        requete.execute('''CREATE TRIGGER IF NOT EXISTS MAJ_HISTO_MATCH2 
        AFTER INSERT
        ON PROD_LIVE_MATCH
        BEGIN insert into PROD_LIVE_MATCH_HISTO  
        SELECT id_match, b1, b2, r1, r2, time_start, time_goal, score_b, score_r, last_team
        FROM PROD_LIVE_MATCH;
        END
        ''')
        # Historisation après un UPDATE
        requete.execute('''CREATE TRIGGER IF NOT EXISTS MAJ_HISTO_MATCH 
        AFTER UPDATE OF id_match, b1, b2, r1, r2, time_start, time_goal, score_b, score_r, last_team
        ON PROD_LIVE_MATCH
        BEGIN insert into PROD_LIVE_MATCH_HISTO  
        SELECT id_match, b1, b2, r1, r2, time_start, time_goal, score_b, score_r, last_team
        FROM PROD_LIVE_MATCH;
        END
        ''')
        
    #  Initalisation de la fonction de vidage des tables
    def PurgeLiveMatch():
        # Purge de la table contenant le live du match
        requete.execute('''DELETE FROM PROD_LIVE_MATCH''')
    
    # Appel de la fonction de création des tables
    lg.info("Création des tables")
    CreateTable()
    
    # Appel de la fonction du trigger
    lg.info("Création du Trigger après INSERT et UPDATE")
    Trigger()
    
    # Appel de la fonction de vidage des tables
    lg.info("Purge de PROD_LIVE_MATCH, par securite")
    PurgeLiveMatch()
    
    # Importation des commentaires et des joueurs depuis les dictionnaires vers SQLITE3
    wb_comments=pd.read_excel('data/input/dictionnaire_commentaires.xlsx',sheet_name=None)
    wb_players=pd.read_excel('data/input/dictionnaire_joueurs.xlsx',sheet_name=None)
    """
    if_exists : {'fail', 'replace', 'append'}, default 'fail'
        - fail: If table exists, do nothing.
        - replace: If table exists, drop it, recreate it, and insert data.
        - append: If table exists, insert data. Create if does not exist.
    """
    for sheet in wb_comments:
        lg.info("Importation des commentaires depuis un dictionnaire xlsx")
        wb_comments[sheet].to_sql('PROD_REF_COMMENTS',requete, index=False, if_exists='replace')
    for sheet in wb_players:
        lg.info("Importation des joueurs depuis un dictionnaire xlsx")
        wb_players[sheet].to_sql('PROD_REF_PLAYERS',requete, index=False, if_exists='replace')
   
    # Les logs de match
#    logs_match = pd.read_csv('data/logs_match.csv', sep = ';')
#    logs_match.to_sql('PROD_LIVE_MATCH_HISTO',connexion, index=False, if_exists='replace')
    
    lg.info("Fermeture de la base")
    fonction_database.fonction_connexion_sqllite_fermeture(connexion,requete)

finally:
    lg.info("Fin d'initialisation des tables dans la base")
