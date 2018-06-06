#!/usr/bin/python
#coding: utf8


#_______________________________________________________________________
# BABY FOOT Connecté
# Programme pour compter les buts d'un match de Baby-Foot à partir de capteurs MC005
# Juin 2017
#_______________________________________________________________________


# 1 - INITIALISATION_________________________


#Initialisation des capteurs
import RPi.GPIO as GPIO																		    #Import de la librairie pour les capteurs
GPIO.setwarnings(False)                                                                         #Désactive le Warning
GPIO.setmode(GPIO.BOARD)                                                                          #Mode BCM si on utilise un BreadBoard
GPIO.setup(12, GPIO.IN)                                                                         #Ce Capteur est un Laser sur le PIN 18 - Il est pour les Bleus
GPIO.setup(18, GPIO.IN)                                                                         #Ce Capteur est un Laser sur le PIN 5 - Il est pour les Rouges

#Initilisation de la manette
import pygame                                                                                   #Import de la librairie PyGame
from pygame.locals import *                                                                     #Tout importer
pygame.init()                                                                                   #Init de Pygame
mon_joystick = pygame.joystick.Joystick(0)                                                      #Touche 0 correspond au bouton Start
mon_joystick.init() 

#Initialisation de SQLite
import sqlite3 as sql                                                                          #Import de SQLite
import sys

#Import des librairies Time
import time
import datetime

#Fonction d'ajout de données dans la table
def live (time_goal_str, i, j):                                                                 #Update de la table Live avec le time du but, et les scores des Bleus et Rouge
    requete.execute("UPDATE PROD_LIVE_MATCH SET time_goal=?, score_b=?, score_r=?",(time_goal_str, i, j))                   
    connexion.commit()

#Fonction d'ajout des infos dans la table historique
def histo_data ():                                                                              #Recopie de la table Live vers la table d'Histo                   
    requete.execute("INSERT INTO PROD_LIVE_MATCH_HISTO SELECT * from PROD_LIVE_MATCH")   
    connexion.commit()


#Initialisation du compteur de match
m = 0	


# 2 - GESTION DE L'ATTENTE D'UN DEBUT DE MATCH_____________________


try:                                                                                            #Gestion de l'arret du programme
    while True:                                                                                 #Programme qui tourne à l'infini
        print("Vérification de la base Live en cours")                                                        
        try:                                                                                    #On vérifie si la base Live contient quelque chose
            connexion = sql.connect('data/PARC_DES_PRINCES.db')  # Nom de la base
            requete = connexion.cursor()

            requete.execute("SELECT count(*) FROM PROD_LIVE_MATCH")
            test_score = requete.fetchone()
            nb_rows = test_score[0]
            if nb_rows > 0:
                print("On peut démarrer un match")                                              #Si elle contient une ligne, c'est qu'un match doit démarrer


# 3 - DEROULE DU MATCH_____________________


                #Initialisation du début de match
                m += 1																	        #On incrémente le match dès le début
                i=0                                                                             #i = Equipe Bleue
                j=0                                                                             #j = Equipe Rouge
                Last_Goal = 0                                                                   # Pas de dernier but pour démarrer
                histo_data ()                                                                   #On écrit dans la table d'Histo le début du match

                #Initialisation de l'heure de début de partie
                from datetime import timedelta                                                  #Import de TimeDelta pour calculer la durée
                time_start = datetime.datetime.now()                                            #Time de début de partie
                time_start_str = str('{0:%d/%m/%Y %H:%M:%S}'.format(time_start))                #Conversion pour stockage en caractère                           

                #Début du match
                print("\nEt c'est parti pour le " + str(m) + "e match de baby-foot à l'Avisia Arena!\n\n")  
                time.sleep(5)                                                                   #On rajoute du temps (5sec) avant de lancer le match et éviter les problèmes de détection

                #Boucle pour créer le match jusqu'au moment où une équipe arrive à 10
                while  i < 10 and j < 10:                                                       #Boucle de 10 buts
                    
                    #Buts pour les bleus
                    if GPIO.input(12) == 0:                                                     #Détection des mouvements sur le PIN 18
                        time_goal = datetime.datetime.now()                                     #Récupérer le time du but
                        time_goal_str = str('{0:%d/%m/%Y %H:%M:%S}'.format(time_goal))          #Conversion en format String pour stockage au bon format
                        i += 1                                                                  #Incrément du but marqué
                        Last_Goal = 1															#Ce but a été marqué par les bleus - utiliser pour l'annulation
                        print("Buuuut des Bleus !")
                        live (time_goal_str, i, j)                                              #Ecriture dans la table live
                        for row in requete.execute("SELECT * FROM PROD_LIVE_MATCH"):                    #Affichage de la table Live
                            print (row)
                        histo_data()                                                            #Ecriture dans la table d'historique
                        time.sleep(5)                                                           #On rajoute du temps (5sec) pour éviter les problèmes de détection
                    
                    #Buts pour les rouges
                    elif GPIO.input(18) == 0:                                                   #Détection des mouvements sur le PIN 19
                        time_goal = datetime.datetime.now()                                     #Récupérer le time du but
                        time_goal_str = str('{0:%d/%m/%Y %H:%M:%S}'.format(time_goal))          #Conversion en format String pour stockage au bon format
                        j += 1                                                                  #Incrément du but marqué
                        Last_Goal = 2															#Ce but a été marqué par les bleus - utiliser pour l'annulation
                        print("Buuuut des Rouge !")
                        live (time_goal_str, i, j)                                              #Ecriture dans la table live
                        for row in requete.execute("SELECT * FROM PROD_LIVE_MATCH"):                    #Affichage de la table Live
                            print (row)
                        histo_data()                                                            #Ecriture dans la table d'historique
                        time.sleep(5)                                                           #On rajoute du temps (5sec) pour éviter les problèmes de détection

                    #Annulation du dernier but
                    for event in pygame.event.get():                                            #A tout moment on peut annuler un but
                        if event.type == JOYBUTTONDOWN:                                         #Quand un bouton est appuyé
                            if event.button == 0:                                               #Le bouton 0 correspond au bouton X
                                if Last_Goal == 1:                                              #Si le dernier but vient des bleus
                                    i = i - 1                                                   #On retire le but
                                    Last_Goal = -1                                              #En modifiant le Last Goal, on va empêcher la double annulation
                                    print("Oh le but n'est pas validé")	
                                    live (time_goal_str, i, j)                                  #Ecriture dans la table live
                                    for row in requete.execute("SELECT * FROM PROD_LIVE_MATCH"):        #Affichage de la table Live
                                        print (row)
                                    histo_data()                                                #Ecriture dans la table d'historique
                                elif Last_Goal == 2:                                            #Si le dernier but vient des rouge
                                    j = j - 1                                                   #On retire le but
                                    Last_Goal = -1                                              #En modifiant le Last Goal, on va empêcher la double annulation
                                    print("Oh le but n'est pas validé")
                                    live (time_goal_str, i, j)                                  #Ecriture dans la table live
                                    for row in requete.execute("SELECT * FROM PROD_LIVE_MATCH"):        #Affichage de la table Live
                                        print (row)
                                    histo_data()                                                #Ecriture dans la table d'historique
                                elif Last_Goal == 0:                                            #Si c'est le premier but du match
                                    i = 0                                                       #Les bleus reste à 0
                                    j = 0                                                       #Les rouge reste à 0
                                    Last_Goal = -1                                              #En modifiant le Last Goal, on va empêcher la double annulation
                                    print("Oh ce premier but n'est pas validé")
                                    live (time_goal_str, i, j)                                  #Ecriture dans la table live
                                    for row in requete.execute("SELECT * FROM PROD_LIVE_MATCH"):        #Affichage de la table Live
                                        print (row)
                                    histo_data()                                                #Ecriture dans la table d'historique
                                elif Last_Goal == -1:                                           #En modifiant le Last Goal, on va empêcher la double annulation
                                    print("Pas de ça ici messieurs ! Bien essayé !\n\n")	
                    

# 4 - FIN DU MATCH_____________________


                #Affichage du résultat
                if i == 10:                                                                                 #Si les bleus arrivent à 10 buts
                    print("C'est donc terminé pour ce match. Victoire des Bleus")
                elif j == 10:                                                                               #Si les rouge arrivent à 10 buts
                    print("C'est donc terminé pour ce match. Victoire des Rouge")     	

        except:
            print ("Table Live Vide")                                                                       #Si la Table Live est vide, on affiche l'info

        #requete.execute("DROP TABLE IF EXISTS PROD_LIVE_MATCH")                                                     #Après un match classique, on supprime la Table Live
        requete.execute("DELETE FROM PROD_LIVE_MATCH")
        connexion.close()
        time.sleep(10)                                                                                      #Un check est fait toutes les 10 secondes pour savoir si un match commence


# 5 - SORTIE DU PROGRAMME_____________________


except:                                                                                                     #Si on quitte le programme,
    #Sortie de la table 
    connexion.close()                                                                                                                                                               

    #Réinitialisation des capteurs
    GPIO.cleanup()                                                                                      

    print("Fin du game")
