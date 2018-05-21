#!/usr/bin/python
#coding: utf8

#_______________________________________________________________________
# BABY FOOT Connecté
# Programme pour compter les buts d'un match de Baby-Foot à partir de capteurs MC005
# Avril 2017
#_______________________________________________________________________


# 1 - INITIALISATION_________________________

#Initialisation des capteurs
import RPi.GPIO as GPIO																		#Import de la librairie pour les capteurs
GPIO.setwarnings(False)                                                                     #Désactive le Warning
GPIO.setmode(GPIO.BCM)                                                                      #Mode BCM si on utilise un BreadBoard
GPIO.setup(18, GPIO.IN)                                                                     #Ce Capteur est un Laser sur le PIN 18 - Il est pour les Bleus
GPIO.setup(19, GPIO.IN)                                                                     #Ce Capteur est un Laser sur le PIN 5 - Il est pour les Rouges

#Initilisation du son
import pygame                                                                               #Import de la librairie PyGame
from pygame.locals import *                                                                 #Tout importer
pygame.init()                                                                               #Init de Pygame

#Initialisation de la manette
mon_joystick = pygame.joystick.Joystick(0)                                                  #Touche 0 correspond au bouton Start
mon_joystick.init()                                                                         #Initialisation du Joystick

#Initialisation du compteur de match
m = 0																						#Par défaut le compteur de match est à 0

#Initialisation du Push Button
while True:	                                                                                #Le programme ne s'arrêtera jamais de tourner
#Initialisation des compteurs et du fichier d'export
m += 1																				        #On incrémente le match dès le début
i=0                                                                                         #i = Equipe Bleue
j=0                                                                                         #j = Equipe Rouge
Last_Goal = 0                                                                               # Pas de dernier but pour démarrer
export = "Time;match;score_bleu;score_rouge\n"                                              #Création du texte pour export CSV avec le timestamp, le match, le score des bleus, le score des rouges
export_flask = "Time;score_bleu;score_rouge"                                                #Création du texte pour export CSV pour Flask et affichage avec le timestamp, le score des bleus, le score des rouges

#Initialisation de l'heure de début de partie
import datetime, time                                                                       #Import de la librairie Time et Datetime
from datetime import timedelta                                                              #Import de TimeDelta pour calculer la durée
time_debut = datetime.datetime.now()                                                        #Time de début de partie
time_debut_str = str('{0:%d/%m/%Y %H:%M:%S}'.format(time_debut))                            #Conversion pour stockage en caractère
export = export  + time_debut_str + ";" + str(m) + ";0;0\n"                                 #On ajoute une ligne à l'export avec l'initialisation du match




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
        Timing_But = time_but - time_debut                                                  #Timing du but
        heure_but, remainder = divmod(Timing_But.seconds, 3600)                             #Calcul pour découper le timing en heure, minute, secondes (1/2)
        minute_but, seconde_but = divmod(remainder, 60)                                     #Calcul pour découper le timing en heure, minute, secondes (2/2)
        i += 1                                                                              #Incrément du but marqué
        Last_Goal = 1																        #Ce but a été marqué par les bleus - utiliser pour l'annulation
        if i < 10:                                                                          #Boucle de buts
            print("Buuuut des Bleus !\nNous sommes à la " + str(seconde_but) + '" de jeu et ça fait ' + str(i) + "-" + str(j) + "\n\n")
            export = export + time_but_str +  ";" + str(m) + ";" + str(i) + ";" + str(j) + "\n"
            export_flask = time_but_str +  ";" + str(i) + ";" + str(j)                      #Export pour Flask en affichage
            fichier_flask = open("/home/pi/Desktop/Data_Match/Live.csv", "w")               #Ecraser le fichier
            fichier_flask.write(export_flask)                                               #Ecriture du score actuel
            fichier_flask.close()                                                           #Fermeture du fichier
            time.sleep(5)                                                                   #On rajoute du temps (5sec) pour éviter les problèmes de détection
    
    #Buts pour les rouges
    if GPIO.input(19) == 0:                                                                 #Détection des mouvements sur le PIN 19
        time_but = datetime.datetime.now()                                                  #Récupérer le time du but
        time_but_str = str('{0:%d/%m/%Y %H:%M:%S}'.format(time_but))                        #Conversion en format String pour stockage au bon format
        Timing_But = time_but - time_debut                                                  #Timing du but
        heure_but, remainder = divmod(Timing_But.seconds, 3600)                             #Calcul pour découper le timing en heure, minute, secondes (1/2)
        minute_but, seconde_but = divmod(remainder, 60)                                     #Calcul pour découper le timing en heure, minute, secondes (2/2)
        j += 1                                                                              #Incrément du but marqué
        Last_Goal = 2																        #Ce but a été marqué par les rouges - utiliser pour l'annulation
        if j < 10:                                                                          #Boucle de buts
            print("Buuuut des Rouges !\nNous sommes à la " + str(seconde_but) + '" de jeu et ça fait ' + str(i) + "-" + str(j) + "\n\n")
            export = export + time_but_str +  ";" + str(m) + ";" + str(i) + ";" + str(j) + "\n"
            export_flask = time_but_str +  ";" + str(i) + ";" + str(j)                      #Export pour Flask en affichage
            fichier_flask = open("/home/pi/Desktop/Data_Match/Live.csv", "w")               #Ecraser le fichier
            fichier_flask.write(export_flask)                                               #Ecriture du score actuel
            fichier_flask.close()                                                           #Fermeture du fichier
            time.sleep(5)                                                                   #On rajoute du temps (5sec) pour éviter les problèmes de détection

    #Annulation du dernier but
    for event in pygame.event.get():                                                        #A tout moment on peut annuler un but
        if event.type == JOYBUTTONDOWN:                                                     #Quand un bouton est appuyé
            if event.button == 0:                                                           #Le bouton 0 correspond au bouton X
                if Last_Goal == 1:                                                          #Si le dernier but vient des bleus
                    i = i - 1                                                               #On retire le but
                    Last_Goal = -1                                                          #En modifiant le Last Goal, on va empêcher la double annulation
                    print("Oh le but n'est pas validé, terrible pour les Bleus ! Le match reprend\nLe score reste à " + str(i) + "-" + str(j) + "\n\n")	
                elif Last_Goal == 2:                                                        #Si le dernier but vient des rouge
                    j = j - 1                                                               #On retire le but
                    Last_Goal = -1                                                          #En modifiant le Last Goal, on va empêcher la double annulation
                    print("Oh le but n'est pas validé, terrible pour les Rouges ! Le match reprend\nLe score resre à " + str(i) + "-" + str(j) + "\n\n")
                elif Last_Goal == 0:                                                        #Si c'est le premier but du match
                    i = 0                                                                   #Les bleus reste à 0
                    j = 0                                                                   #Les rouge reste à 0
                    Last_Goal = -1                                                          #En modifiant le Last Goal, on va empêcher la double annulation
                    print("Oh ce premier but n'est pas validé, ! Le match reprend\nLe score reste à " + str(i) + "-" + str(j) + "\n\n")	
                elif Last_Goal == -1:                                                       #En modifiant le Last Goal, on va empêcher la double annulation
                    print("Pas de ça ici messieurs ! Bien essayé !\n\n")	
    



# 3 - FIN DU MATCH_____________________

#Affichage du résultat
time.sleep(1)                                                                               #On rajoute du temps (3sec) pour afficher la fin de match
if i == 10:                                                                                 #Si les bleus arrivent à 10 buts
    print("C'est donc terminé pour ce match #" + str(m) + " à l'Avisia Arena !\nVictoire des Bleus : " + str(i) + "-" + str(j) + "\nOn se retrouve très vite pour un nouveau match !\nA vous les studios !")
elif j == 10:                                                                               #Si les rouge arrivent à 10 buts
    print("C'est donc terminé pour ce match #" + str(m) + " à l'Avisia Arena !\nVictoire des Rouges : " + str(i) + "-" + str(j) + "\nOn se retrouve très vite pour un nouveau match !\nA vous les studios !")      	

#Ecriture du fichier d'export
nom_fichier = str('{0:%Y%m%d_%H%M%S}'.format(time_debut))                                   #Le fichier se base sur l'horodatage
fichier = open("/home/pi/Desktop/Data_Match/Data_" + str(nom_fichier) + "_Match" + str(m) + ".csv", "w")                    #Ecraser le fichier
fichier.write(export)                                                                       #Ecriture de tous les enregistrements du match
fichier.close()                                                                             #Fermeture du fichier

#Réinitialisation des capteurs
GPIO.cleanup()                                                                              #On réinitialise les ports GPIO
