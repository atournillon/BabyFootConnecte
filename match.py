#!/usr/bin/python
#coding: utf8

#_______________________________________________________________________
# BABY FOOT Connecté
# Programme pour compter les buts d'un match de Baby-Foot à partir de capteurs MC005
# Avril 2017
#_______________________________________________________________________


# 1 - INITIALISATION_________________________

#Initialisation des capteurs
import RPi.GPIO as GPIO																		    #Import de la librairie pour les capteurs
GPIO.setwarnings(False)                                                                         #Désactive le Warning
GPIO.setmode(GPIO.BCM)                                                                          #Mode BCM si on utilise un BreadBoard
GPIO.setup(18, GPIO.IN)                                                                         #Ce Capteur est un Laser sur le PIN 18 - Il est pour les Bleus
GPIO.setup(19, GPIO.IN)                                                                         #Ce Capteur est un Laser sur le PIN 5 - Il est pour les Rouges

#Initilisation du son
import pygame                                                                                   #Import de la librairie PyGame
from pygame.locals import *                                                                     #Tout importer
pygame.init()                                                                                   #Init de Pygame

#Initialisation de SQLite
import sqlite3 as lite                                                                          #Import de SQLite
import sys
conn = lite.connect('data/baby_foot.db')                                                        #Nom de la table d'affichage live
curs=conn.cursor()

with conn:
    curs.execute("DROP TABLE IF EXISTS LIVE_MATCH")                                         
    curs.execute("CREATE TABLE LIVE_MATCH (time_debut DATETIME, time_but DATETIME, team_1 NUMERIC, team_2 Numeric)")
    curs.execute("CREATE TABLE IF NOT EXISTS HISTO_MATCH (time_debut DATETIME, time_but DATETIME, match_id NUMERIC, team_1 NUMERIC, team_2 Numeric)")

#Fonction d'ajout de données dans la table
def live (time_debut, time_but, team_1, team_2):                                                #Création du programme d'incrément pour le live
    curs.execute("DROP TABLE IF EXISTS LIVE_MATCH")                                             #Suppression de la table
    curs.execute("CREATE TABLE LIVE_MATCH (time_debut DATETIME, time_but DATETIME, team_1 NUMERIC, team_2 Numeric)")                    #Création de la table
    curs.execute("INSERT INTO LIVE_MATCH values((?), (?), (?), (?))", (time_debut, time_but, team_1, team_2))                   #Insertion dans la table des time, du score des Bleus et Rouge
    conn.commit()

#Fonction d'ajout des infos dans la table historique
def histo_data (time_debut, time_but, match_id, team_1, team_2):
    curs.execute("INSERT INTO HISTO_MATCH values((?), (?), (?), (?), (?))", (time_debut, time_but, match_id, team_1, team_2))   #Insertion dans la table d'historique des time, du match et du score des Bleus et Rouge
    conn.commit()

#Initialisation de la manette
mon_joystick = pygame.joystick.Joystick(0)                                                      #Touche 0 correspond au bouton Start
mon_joystick.init()                                                                             #Initialisation du Joystick

#Initialisation du compteur de match
m = 0																						    #Par défaut le compteur de match est à 0

#Initialisation du Match
while True:	                                                                                    #Le programme ne s'arrêtera jamais de tourner
    #Initialisation des compteurs et du fichier d'export
    m += 1																				        #On incrémente le match dès le début
    i=0                                                                                         #i = Equipe Bleue
    j=0                                                                                         #j = Equipe Rouge
    Last_Goal = 0                                                                               # Pas de dernier but pour démarrer
    
    #Initialisation de l'heure de début de partie
    import datetime, time                                                                       #Import de la librairie Time et Datetime
    from datetime import timedelta                                                              #Import de TimeDelta pour calculer la durée
    time_debut = datetime.datetime.now()                                                        #Time de début de partie
    time_debut_str = str('{0:%d/%m/%Y %H:%M:%S}'.format(time_debut))                            #Conversion pour stockage en caractère
    live(time_debut_str,time_debut_str,i,j)                                                     #Ecriture du live
    histo_data(time_debut_str,time_debut_str,m,i,j)                                             #Ecriture de l'historique





# 2 - DEROULE DU MATCH_____________________

    #Début du match
    print("\nEt c'est parti pour le " + str(m) + "e match de baby-foot à l'Avisia Arena!\n\n")  #A supprimer
    time.sleep(5)                                                                               #On rajoute du temps (5sec) avant de lancer le match

    #Boucle pour créer le match jusqu'au moment où une équipe arrive à 10
    while  i < 10 and j < 10:                                                                   #Boucle de 10 buts
        
        #Buts pour les bleus
        if GPIO.input(18) == 0:                                                                 #Détection des mouvements sur le PIN 18
            time_but = datetime.datetime.now()                                                  #Récupérer le time du but
            time_but_str = str('{0:%d/%m/%Y %H:%M:%S}'.format(time_but))                        #Conversion en format String pour stockage au bon format
            i += 1                                                                              #Incrément du but marqué
            Last_Goal = 1																        #Ce but a été marqué par les bleus - utiliser pour l'annulation
            print("Buuuut des Bleus !")
            live(time_debut_str,time_but_str,i,j)                                                #Ecriture dans la table live
            for row in curs.execute("SELECT * FROM LIVE_MATCH"): 
                print (row)
            histo_data(time_debut_str,time_but_str,m,i,j)                                       #Ecriture dans la table d'historique
            time.sleep(5)                                                                       #On rajoute du temps (5sec) pour éviter les problèmes de détection
        
        #Buts pour les rouges
        elif GPIO.input(19) == 0:                                                                 #Détection des mouvements sur le PIN 19
            time_but = datetime.datetime.now()                                                  #Récupérer le time du but
            time_but_str = str('{0:%d/%m/%Y %H:%M:%S}'.format(time_but))                        #Conversion en format String pour stockage au bon format
            j += 1                                                                              #Incrément du but marqué
            Last_Goal = 2																        #Ce but a été marqué par les rouges - utiliser pour l'annulation
            print("Buuuut des Rouges !")
            live(time_debut_str, time_but_str, i,j)                                         #Ecriture dans la table live
            for row in curs.execute("SELECT * FROM LIVE_MATCH"):
                print (row)
            histo_data(time_debut_str,time_but_str,m,i,j)                                   #Ecriture dans la table d'historique
            time.sleep(5)                                                                   #On rajoute du temps (5sec) pour éviter les problèmes de détection

        #Annulation du dernier but
        for event in pygame.event.get():                                                        #A tout moment on peut annuler un but
            if event.type == JOYBUTTONDOWN:                                                     #Quand un bouton est appuyé
                if event.button == 0:                                                           #Le bouton 0 correspond au bouton X
                    if Last_Goal == 1:                                                          #Si le dernier but vient des bleus
                        i = i - 1                                                               #On retire le but
                        Last_Goal = -1                                                          #En modifiant le Last Goal, on va empêcher la double annulation
                        print("Oh le but n'est pas validé")	
                        live(time_debut_str,time_but_str,i,j)                                   #Ecriture dans la table live
                        for row in curs.execute("SELECT * FROM LIVE_MATCH"):
                            print (row)
                        histo_data(time_debut_str,time_but_str,m,i,j)                           #Ecriture dans la table d'historique
                    elif Last_Goal == 2:                                                        #Si le dernier but vient des rouge
                        j = j - 1                                                               #On retire le but
                        Last_Goal = -1                                                          #En modifiant le Last Goal, on va empêcher la double annulation
                        print("Oh le but n'est pas validé")
                        live(time_debut_str,time_but_str,i,j)                                   #Ecriture dans la table live
                        for row in curs.execute("SELECT * FROM LIVE_MATCH"):
                            print (row)
                        histo_data(time_debut_str,time_but_str,m,i,j)                           #Ecriture dans la table d'historique
                    elif Last_Goal == 0:                                                        #Si c'est le premier but du match
                        i = 0                                                                   #Les bleus reste à 0
                        j = 0                                                                   #Les rouge reste à 0
                        Last_Goal = -1                                                          #En modifiant le Last Goal, on va empêcher la double annulation
                        print("Oh ce premier but n'est pas validé")
                        live(time_debut_str,time_but_str,i,j)                                   #Ecriture dans la table live
                        for row in curs.execute("SELECT * FROM LIVE_MATCH"):
                            print (row)
                        histo_data(time_debut_str,time_but_str,m,i,j)                           #Ecriture dans la table d'historique
                    elif Last_Goal == -1:                                                       #En modifiant le Last Goal, on va empêcher la double annulation
                        print("Pas de ça ici messieurs ! Bien essayé !\n\n")	
        



# 3 - FIN DU MATCH_____________________

    #Affichage du résultat
    time.sleep(1)                                                                               #On rajoute du temps (1sec) pour afficher la fin de match
    if i == 10:                                                                                 #Si les bleus arrivent à 10 buts
        print("C'est donc terminé pour ce match")
    elif j == 10:                                                                               #Si les rouge arrivent à 10 buts
        print("C'est donc terminé pour ce match")     	

#Sortie de la table
conn.close()                                                                               

#Réinitialisation des capteurs
GPIO.cleanup() 
