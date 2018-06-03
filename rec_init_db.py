# Chargement des packages
import sqlite3 as sql
import time
from datetime import datetime
import pandas as pd

# Base de recette
connexion = sql.connect('data/ROUDOUROU.db')

# Connexion
requete = connexion.cursor()

# Initialisation de la fonction de création des tables
def CreateTable():
    # Création de la table du live du match
    requete.execute('''CREATE TABLE IF NOT EXISTS REC_LIVE_MATCH
    (id_match INTEGER PRIMARY KEY, b1 INTEGER, b2 INTEGER, r1 INTEGER, r2 INTEGER, time_start DATETIME, time_goal DATETIME, score_b INTEGER, score_r INTEGER)''')
    # Création de la table d'historisation des lives de match
    requete.execute('''CREATE TABLE IF NOT EXISTS REC_LIVE_MATCH_HISTO
    (id_match INTEGER PRIMARY KEY, b1 INTEGER, b2 INTEGER, r1 INTEGER, r2 INTEGER, time_start DATETIME, time_goal DATETIME, score_b INTEGER, score_r INTEGER)''')
    # Création de la table contenant le référentiel des joueurs
    requete.execute('''CREATE TABLE IF NOT EXISTS REC_REF_PLAYERS
    (id_player INTEGER PRIMARY KEY, firstname TEXT, lastname TEXT, nickname TEXT)''')
    
# Initialisation de la fonction contenant le déclencheur
def Trigger():
    # Initialisation du Trigger permettant de copier REC_LIVE_MATCH dans REC_LIVE_MATCH_HISTO
    requete.execute('''CREATE TRIGGER IF NOT EXISTS MAJ_HISTO_MATCH 
    AFTER UPDATE OF id_match, b1, b2, r1, r2, time_start, time_goal, score_b, score_r
    ON REC_LIVE_MATCH
    BEGIN insert into REC_LIVE_MATCH_HISTO  
    SELECT id_match, b1, b2, r1, r2, time_start, time_goal, score_b, score_r
    FROM REC_LIVE_MATCH;
    END
    ''')

#  Initalisation de la fonction de vidage des tables
def PurgeLiveMatch():
    # Purge de la table contenant le live du match
    requete.execute('''DELETE FROM REC_LIVE_MATCH''')
#    requete.execute('''DELETE FROM REC_LIVE_MATCH_HISTO''')
#    requete.execute('''DELETE FROM REC_REF_PLAYERS''')

# Initialisation des fonctions permettant l'ajouter de données dans une table, manuellement
#def AddData_LIVE(id_match,b1,b2,r1,r2,time_start,time_goal,score_b,score_r):
#    requete.execute('''INSERT INTO REC_LIVE_MATCH (id_match,b1,b2,r1,r2,time_start,time_goal,score_b,score_r)
#    VALUES (?,?,?,?,?,?,?,?,?)''',(id_match,b1,b2,r1,r2,time_start,time_goal,score_b,score_r))
#def AddData_HISTO(id_match,b1,b2,r1,r2,time_start,time_goal,score_b,score_r):
#    requete.execute('''INSERT INTO REC_LIVE_MATCH_HISTO (id_match,b1,b2,r1,r2,time_start,time_goal,score_b,score_r)
#    VALUES (?,?,?,?,?,?,?,?,?)''',(id_match,b1,b2,r1,r2,time_start,time_goal,score_b,score_r))
#def AddData_PLAYER(id_player,firstname,lastname,nickname):
#    requete.execute('''INSERT INTO REC_REF_PLAYERS (id_player,firstname,lastname,nickname)
#    VALUES (?,?,?,?)''',(id_player,firstname,lastname,nickname))

# Appel de la fonction de création des tables
CreateTable()

# Appel de la fonction du trigger
Trigger()

# Appel de la fonction de vidage des tables
PurgeLiveMatch()

# Importation des commentaires depuis le dictionnaire vers SQLITE
# requete.execute('''DROP TABLE REC_REF_COMMENTS''')
wb=pd.read_excel('data/dictionnaire_commentaires.xlsx',sheet_name=None)
"""
if_exists : {'fail', 'replace', 'append'}, default 'fail'
    - fail: If table exists, do nothing.
    - replace: If table exists, drop it, recreate it, and insert data.
    - append: If table exists, insert data. Create if does not exist.
"""
for sheet in wb:
    wb[sheet].to_sql('REC_REF_COMMENTS',connexion, index=False, if_exists='replace')

# Soumission des fonctions précédemment appelées
connexion.commit()

# Appel des fonctions d'ajout de données
# Génération du datetime en INTEGER qui sera le id_match
#time_start=int(time.mktime(datetime.now().timetuple()))
#time_end=time_start+666
#AddData_HISTO(time_start,1,2,3,4,time_start,time_end,4,10)
#
#time_start=time_end+60
#time_end=time_start+666
#AddData_HISTO(time_start,1,7,3,4,time_start,time_end,10,8)
#
#time_start=time_end+60
#time_end=time_start+666
#AddData_HISTO(time_start,5,7,3,6,time_start,time_end,10,9)
#
#time_start=time_end+60
#time_end=time_start+666
#AddData_HISTO(time_start,5,7,3,6,time_start,time_end,10,3)
#AddData_LIVE(time_start,5,7,3,6,time_start,time_end,10,3)
#
#AddData_PLAYER(1,'Eric','BESCOND','RiCo')
#AddData_PLAYER(2,'Thibault','QUINQUIS','TQS')
#AddData_PLAYER(3,'Fabrice','SIMON','Simon')
#AddData_PLAYER(4,'Nicolas','BETIN','BN')
#AddData_PLAYER(5,'Adrien','TOURNILLON','Tournicoti')
#AddData_PLAYER(6,'Mathieu','BROCHARD','La Broche')
#AddData_PLAYER(7,'Mireille','MATHIEU','MiMi')



# Soumission des fonctions précédemment appelées
#connexion.commit()

# Affichage du contenu d'une table
#print('\n REC_LIVE_MATCH')
#requete.execute('SELECT * FROM REC_LIVE_MATCH')
#for i in requete:
#    print ('\n')
#    for j in i:
#        print (j)
#        
#print('\n REC_LIVE_MATCH_HISTO')
#requete.execute('SELECT * FROM REC_LIVE_MATCH_HISTO')
#for i in requete:
#    print ('\n')
#    for j in i:
#        print (j)
#
#print('\n REC_REF_PLAYERS')
#requete.execute('SELECT * FROM REC_REF_PLAYERS')
#for i in requete:
#    print ('\n')
#    for j in i:
#        print (j)
#        
#print('\n REC_REF_COMMENTS')
#requete.execute('SELECT * FROM REC_REF_COMMENTS')
#for i in requete:
#    print ('\n')
#    for j in i:
#        print (j)

# Déconnexion de la base
requete.close()