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
GPIO.setup(18, GPIO.IN)                                                                     #Ce Capteur est un PIR sur le PIN 17 - Il est pour les Bleus
GPIO.setup(19, GPIO.IN)                                                                      #Ce Capteur est un PIR sur le PIN 5 - Il est pour les Rouges

#Initilisation du son
import pygame                                                                               
from pygame.locals import *
pygame.init()

#Initialisation de la manette
mon_joystick = pygame.joystick.Joystick(0)
mon_joystick.init()


#Initialisation du compteur de match
m = 0																						#Par défaut le compteur est à 0
rouge = 1

#Initialisation du Push Button
while True:	                                                                                #Le programme ne s'arrêtera jamais de tourner
    #for event in pygame.event.get():
        #if event.type == JOYBUTTONDOWN:
            #if event.button == 9:																				
    #input_state_1 = GPIO.input(26)                                                            #Détection du Push Button
    #if input_state_1 == False:                                                                #Si le bouton est appuyé

                #Initialisation des compteurs et du fichier d'export
                m += 1																				#On incrémente le match
                i=0                                                                                 #Equipe Bleue
                j=0
                Last_Goal = 0                                                                                 #Equipe Rouge
                export = "Time;match;score_bleu;score_rouge\n"                                      #Création du texte pour export CSV avec le timestamp, le match, le score des bleus, le score des rouges
                
                #Initialisation de l'heure de début de partie
                import datetime, time
                from datetime import timedelta
                delai = datetime.timedelta(hours=0, minutes=0, seconds=10)
                time_debut = datetime.datetime.now()                                                #Heure de début de partie
                time_debut_str = str('{0:%d/%m/%Y %H:%M:%S}'.format(time_debut))                    #Conversion pour affichage au bon format 
                export = export  + time_debut_str + ";" + str(m) + ";0;0\n"                         #On ajoute une ligne à l'export avec l'initialisation du match

        # 2 - DEROULE DU MATCH_____________________

        #Début du match
                if m == 1:
                    print("\nEt c'est parti pour le " + str(m) + "er match de baby-foot à l'Avisia Arena!\n\n")
                else:
                    print("\nEt c'est parti pour le " + str(m) + "ème match de baby-foot à l'Avisia Arena!\n\n")
                time.sleep(5)                                                                       #On rajoute du temps (5sec) avant de lancer le match

            #Boucle pour créer le match jusqu'au moment où une équipe arrive à 10
                while  i < 10 and j < 10:
                    #Buts pour les bleus
                    if GPIO.input(18) == 0:                                                              #Détection des mouvements sur le PIN 17
                        time_but = datetime.datetime.now()                                          #Récupérer l'heure du but
                        time_but_str = str('{0:%d/%m/%Y %H:%M:%S}'.format(time_but))                #Passage en format String pour affichage au bon format
                        Timing_But = time_but - time_debut                                          #Calculer à quel moment le but est marqué 
                        Timing_But_str = str(Timing_But.seconds)                                    #Nombre de secondes depuis le début de match pour affichage
                        heure_but, remainder = divmod(Timing_But.seconds, 3600)
                        minute_but, seconde_but = divmod(remainder, 60)
                        i += 1
                        Last_Goal = 1																#Incrément du but marqué
                        if i == 1 and j == 0:                                                       #Premier But
                            if minute_but < 1:
                                print("Buuuut ! C'est l'ouverture du score pour les Bleus chez Avisia à la " + str(seconde_but) + '" de jeu !\nVoilà un but qui lance le match ' + str(i) + "-" + str(j) + "\n\n")
                            else:
                                print("Buuuut ! C'est l'ouverture du score pour les Bleus chez Avisia à la " + str(minute_but) + "' de jeu !\nVoilà un but qui lance le match " + str(i) + "-" + str(j) + "\n\n")
                            export = export + time_but_str +  ";" + str(m) + ";" + str(i) + ";" + str(j) + "\n"
                            time.sleep(5)															#Le programme ne s'arrêtera jamais de tourner        
                        elif i < 10:                                                                 #Buts suivants
                            if minute_but < 1:
                                print("Et ça continue ! Buuuut des Bleus !\nNous sommes à la " + str(seconde_but) + '" de jeu et ça fait ' + str(i) + "-" + str(j) + "\n\n")
                            else:
                                print("Et ça continue ! Buuuut des Bleus !\nNous sommes à la " + str(minute_but) + "' de jeu et ça fait " + str(i) + "-" + str(j) + "\n\n")
                            export = export + time_but_str +  ";" + str(m) + ";" + str(i) + ";" + str(j) + "\n"
                            time.sleep(5)                                                           #On rajoute du temps (5sec) pour éviter les doublon
                        else:                                                                       #Dernier but
                            if minute_but < 1:
                                print("Buuuuut ! C'est le but de la victoire pour les Bleus à la " + str(seconde_but) + '" de jeu !\n\n')
                            else:
                                print("Buuuuut ! C'est le but de la victoire pour les Bleus à la " + str(minute_but) + "' de jeu !\n\n")
                            export = export + time_but_str +  ";" + str(m) + ";" + str(i) + ";" + str(j) + "\n"
                    #Buts pour les rouges
                    elif GPIO.input(19) == 1:                                                            #Détection des mouvements sur le PIN 18
                        time_but = datetime.datetime.now()                                          #Récupérer l'heure du but
                        time_but_str = str('{0:%d/%m/%Y %H:%M:%S}'.format(time_but))                #Passage en format String pour affichage au bon format
                        Timing_But = time_but - time_debut                                          #Calculer à quel moment le but est marqué 
                        Timing_But_str = str(Timing_But.seconds)                                    #Nombre de secondes depuis le début de match pour affichage
                        heure_but, remainder = divmod(Timing_But.seconds, 3600)
                        minute_but, seconde_but = divmod(remainder, 60)
                        j += 1	
                        Last_Goal = 2															    #Incrément du but marqué
                        if j == 1 and i == 0:                                                       #Premier But
                            if minute_but < 1:
                                print("Buuuut ! C'est l'ouverture du score pour les Rouges chez Avisia à la " + str(seconde_but) + '" de jeu !\nVoilà un but qui lance le match ' + str(i) + "-" + str(j) + "\n\n")
                            else:
                                print("Buuuut ! C'est l'ouverture du score pour les Rouges chez Avisia à la " + str(minute_but) + "' de jeu !\nVoilà un but qui lance le match " + str(i) + "-" + str(j) + "\n\n")
                            export = export + time_but_str +  ";" + str(m) + ";" + str(i) + ";" + str(j) + "\n"
                            time.sleep(5)                                                           #On rajoute du temps (5sec) pour éviter les doublons
                        elif j < 10:                                                                #Buts suivants
                            if minute_but < 1:
                                print("Et ça continue ! Buuuut des Rouges !\nNous sommes à la " + str(seconde_but) + '" de jeu et ça fait ' + str(i) + "-" + str(j) + "\n\n")
                            else:
                                print("Et ça continue ! Buuuut des Rouges !\nNous sommes à la " + str(minute_but) + "' de jeu et ça fait " + str(i) + "-" + str(j) + "\n\n")
                            export = export + time_but_str +  ";" + str(m) + ";" + str(i) + ";" + str(j) + "\n"
                            time.sleep(5)                                                           #On rajoute du temps (5sec) pour éviter les doublons
                        else:                                                                       #Dernier but
                            if minute_but < 1:
                                print("Buuuuut ! C'est le but de la victoire pour les Rouges à la " + str(seconde_but) + '" de jeu !\n\n')
                            else:
                                print("Buuuuut ! C'est le but de la victoire pour les Rouges à la " + str(minute_but) + "' de jeu !\n\n")
                            export = export + time_but_str +  ";" + str(m) + ";" + str(i) + ";" + str(j) + "\n"
                    
                    #Annulation du dernier but
                    for event in pygame.event.get():
                        if event.type == JOYBUTTONDOWN:
                            if event.button == 0:                                                   #Si on appuie sur X
                                if Last_Goal == 1:                                                  #Si le dernier but vient des bleus
                                    i = i - 1
                                    Last_Goal = -1
                                    print("Oh le but n'est pas validé, terrible pour les Bleus ! Le match reprend\nLe score reste à " + str(i) + "-" + str(j) + "\n\n")	
                                elif Last_Goal == 2:                                                #Si le dernier but vient des rouge
                                    j = j - 1
                                    Last_Goal = -1
                                    print("Oh le but n'est pas validé, terrible pour les Rouges ! Le match reprend\nLe score resre à " + str(i) + "-" + str(j) + "\n\n")
                                elif Last_Goal == 0:                                                #Si c'est le premier but du match
                                    i = 0
                                    j = 0
                                    Last_Goal = -1
                                    print("Oh ce premier but n'est pas validé, ! Le match reprend\nLe score reste à " + str(i) + "-" + str(j) + "\n\n")	
                                elif Last_Goal == -1:
                                    print("Pas de ça ici messieurs ! Bien essayé !\n\n")	
                    #else:
                    #    continue


        # 3 - FIN DU MATCH_____________________

                #Affichage du résultat
                time.sleep(1)                                                                       #On rajoute du temps (3sec) pour afficher la fin de match
                if i == 10:
                    print("C'est donc terminé pour ce match #" + str(m) + " à l'Avisia Arena !\nVictoire des Bleus : " + str(i) + "-" + str(j) + "\nOn se retrouve très vite pour un nouveau match !\nA vous les studios !")
                elif j == 10:
                    print("C'est donc terminé pour ce match #" + str(m) + " à l'Avisia Arena !\nVictoire des Rouges : " + str(i) + "-" + str(j) + "\nOn se retrouve très vite pour un nouveau match !\nA vous les studios !")      	

                #Ecriture du fichier d'export
                nom_fichier = str('{0:%Y%m%d_%H%M%S}'.format(time_debut))
                fichier = open("/home/pi/Desktop/Data_Match/Data_" + str(nom_fichier) + "_Match" + str(m) + ".csv", "w")                    #Ecraser le fichier
                fichier.write(export)                                                               #Ecriture de tous les enregistrements du match
                fichier.close()

#Réinitialisation des capteurs
GPIO.cleanup()
