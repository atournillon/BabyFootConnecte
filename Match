#!/usr/bin/python
#coding: utf8

#_______________________________________________________________________
# BABY FOOT Connecté
# Programme pour compter les buts d'un match de Baby-Foot à partir de capteurs PIR
# Avril 2017
#_______________________________________________________________________


# 1 - INITIALISATION_________________________

#Initialisation des capteurs
import RPi.GPIO as GPIO																		#Import de la librairie pour les capteurs
GPIO.setwarnings(False)                                                                     #Désactive le Warning
GPIO.setmode(GPIO.BCM)                                                                      #Mode BCM si on utilise un BreadBoard
GPIO.setup(17, GPIO.IN)                                                                     #Ce Capteur est un PIR sur le PIN 17 - Il est pour les Bleus
GPIO.setup(18, GPIO.IN)                                                                     #Ce Capteur est un PIR sur le PIN 17 - Il est pour les Rouges
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)                                           #Ce Capteur est un Push Button sur le PIN 26

#Initilisation du son
import pygame                                                                               
from pygame.locals import *
pygame.init()
pygame.mixer.music.load("goal.ogg")                                                         #Chargement du fichier de son pour les buts


#Initialisation du compteur de match
m = 0																						#Par défaut le compteur est à 0

#Initialisation du Push Button
while True:																					#Le programme ne s'arrêtera jamais de tourner
    input_state_1 = GPIO.input(26)                                                            #Détection du Push Button
    if input_state_1 == False:                                                                #Si le bouton est appuyé

        #Initialisation des compteurs et du fichier d'export
        m += 1																				#On incrémente le match
        i=0                                                                                 #Equipe Bleue
        j=0                                                                                 #Equipe Rouge
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
        print("\nEt c'est parti pour le " + str(m) + "ème match de baby-foot à l'Avisia Arena!\n\n")
        time.sleep(5)                                                                       #On rajoute du temps (5sec) avant de lancer le match

    #Boucle pour créer le match jusqu'au moment où une équipe arrive à 10
        while  i < 10 and j < 10:
            #Buts pour les bleus
            if GPIO.input(17):                                                              #Détection des mouvements sur le PIN 17
                time_but = datetime.datetime.now()                                          #Récupérer l'heure du but
                time_but_str = str('{0:%d/%m/%Y %H:%M:%S}'.format(time_but))                #Passage en format String pour affichage au bon format
                Timing_But = time_but - time_debut                                          #Calculer à quel moment le but est marqué 
                Timing_But_str = str(Timing_But.seconds)                                    #Nombre de secondes depuis le début de match pour affichage
                i += 1																		#Incrément du but marqué
                if i == 1 and j == 0:                                                       #Premier But
                    print("Buuuut ! C'est l'ouverture du score pour les Bleus chez Avisia à la " + Timing_But_str + "e secondes !\nVoilà un but qui lance le match " + str(i) + "-" + str(j) + "\n\n")
                    pygame.mixer.music.play()                                               #Lecture du son goal
                    export = export + time_but_str +  ";" + str(m) + ";" + str(i) + ";" + str(j) + "\n"
                    time.sleep(5)                                                           #On rajoute du temps (5sec) pour éviter les doublons
                elif i < 10:                                                                 #Buts suivants
                    print("Et ça continue ! Buuuut des Bleus !\nNous sommes à la " + Timing_But_str + "e secondes et ça fait " + str(i) + "-" + str(j) + "\n\n")
                    pygame.mixer.music.play()                                               #Lecture du son goal
                    export = export + time_but_str +  ";" + str(m) + ";" + str(i) + ";" + str(j) + "\n"
                    time.sleep(5)                                                           #On rajoute du temps (5sec) pour éviter les doublons
                    #Cas où le but n'est pas validé
                    while datetime.datetime.now() < time_but + delai:
                    	input_state_2 = GPIO.input(26)                                            #Détection du Push Button
    					if input_state_2 == False:                                                #Si le bouton est appuyé
    						i -= 1																#On retire le but
    						print("Ah! On nous dit dans l'oreillette que ce but n'est pas vraiment valide ! \n On reste donc sur le score de  " + str(i) + "-" + str(j) + "\n\n")
    					else:
    						continue															#Si personne n'appuie alors on continue
                else:                                                                       #Dernier but
                    print("Buuuuut ! C'est le but de la victoire pour les Bleus à la " + Timing_But_str + "e secondes !\n\n")
                    pygame.mixer.music.play()                                               #Lecture du son goal
                    export = export + time_but_str +  ";" + str(m) + ";" + str(i) + ";" + str(j) + "\n"
            #Buts pour les rouges
            elif GPIO.input(18):                                                            #Détection des mouvements sur le PIN 18
                time_but = datetime.datetime.now()                                          #Récupérer l'heure du but
                time_but_str = str('{0:%d/%m/%Y %H:%M:%S}'.format(time_but))                #Passage en format String pour affichage au bon format
                Timing_But = time_but - time_debut                                          #Calculer à quel moment le but est marqué 
                Timing_But_str = str(Timing_But.seconds)                                    #Nombre de secondes depuis le début de match pour affichage
                j += 1																		#Incrément du but marqué
                if j == 1 and i == 0:                                                                  #Premier But
                    print("Buuuut ! C'est l'ouverture du score pour les Rouges chez Avisia à la " + Timing_But_str + "e secondes !\nVoilà un but qui lance le match " + str(i) + "-" + str(j) + "\n\n")
                    pygame.mixer.music.play()                                               #Lecture du son goal
                    export = export + time_but_str +  ";" + str(m) + ";" + str(i) + ";" + str(j) + "\n"
                    time.sleep(5)                                                           #On rajoute du temps (5sec) pour éviter les doublons
                elif j < 10:                                                                #Buts suivants
                    print("Et ça continue ! Buuuut des Rouges !\nNous sommes à la " + Timing_But_str + "e secondes et ça fait " + str(i) + "-" + str(j) + "\n\n")
                    pygame.mixer.music.play()                                               #Lecture du son goal
                    export = export + time_but_str +  ";" + str(m) + ";" + str(i) + ";" + str(j) + "\n"
                    time.sleep(5)                                                           #On rajoute du temps (5sec) pour éviter les doublons
                else:                                                                       #Dernier but
                    print("Buuuuut ! C'est le but de la victoire pour les Rouges à la " + Timing_But_str + "e secondes !\n\n")
                    pygame.mixer.music.play()                                               #Lecture du son goal
                    export = export + time_but_str +  ";" + str(m) + ";" + str(i) + ";" + str(j) + "\n"
        


# 3 - FIN DU MATCH_____________________

        #Affichage du résultat
        time.sleep(3)                                                                       #On rajoute du temps (3sec) pour afficher la fin de match
        if i == 10:
        	print("C'est donc terminé pour ce match #" + str(m) + " à l'Avisia Arena !\nVictoire des Bleus : " + str(i) + "-" + str(j) + "\nOn se retrouve très vite pour un nouveau match !\nA vous les studios !")
        elif j == 10:
        	print("C'est donc terminé pour ce match #" + str(m) + " à l'Avisia Arena !\nVictoire des Rouges : " + str(i) + "-" + str(j) + "\nOn se retrouve très vite pour un nouveau match !\nA vous les studios !")      	

        #Ecriture du fichier d'export
        nom_fichier = str('{0:%Y%m%d_%H%M%S}'.format(time_debut))
        fichier = open("/home/pi/Desktop/Data_Match/Data_" + str(nom_fichier) + "_Match" + str(m) + ".csv", "w")                    #Ecraser le fichier
        fichier.write(export)                                                               #Ecriture de tous les enregistrements du match
        fichier.close()
