# !/usr/bin/python
# coding: utf8

########################################
# BABY FOOT Connecté
# Programme pour compter les buts d'un match de Baby-Foot à partir de capteurs MC005
# 1 - INITIALISATION_________________________

import logging as lg
import json
import time
import datetime
import sys
sys.path.append("data")
import fonction_database


sys.path.append("capteurs/lib")
import interaction_database

#Import de la librairie pour les capteurs
#conda install -c poppy-project rpi.gpio
try:
    import RPi.GPIO as GPIO
except:
    import fake_rpi
    sys.modules['RPi'] = fake_rpi.RPi     # Fake RPi (GPIO)
    sys.modules['smbus'] = fake_rpi.smbus # Fake smbus (I2C)
    import RPi


#Import de la librairie PyGame
# http://www.montefiore.ulg.ac.be/~boigelot/cours/ppi/tuto-w10.pdf
import pygame

# Initialisation de la log
t = datetime.datetime.now()
fn = 'logs/run_capteurs.{}.log'.format(t.strftime("%Y-%m-%d"))

lg.basicConfig(filename = fn,
               level = lg.DEBUG,
               filemode = 'a',
               format = '%(asctime)s\t%(levelname)s\t%(message)s',
               datefmt = '%Y-%m-%d %H:%M:%S'
               )

# Fetching database configuration
with open('config.json') as conf_file:
    global DB
    DB = json.load(conf_file)

#Initialisation des capteurs
GPIO.setwarnings(False)     #Désactive le Warning
GPIO.setmode(GPIO.BOARD)    #Mode BCM si on utilise un BreadBoard
GPIO.setup(DB['capteurs']['id_capteur_bleu'], RPi.GPIO.IN)     #Ce Capteur est un Laser sur le PIN 18 - Il est pour les Bleus
GPIO.setup(DB['capteurs']['id_capteur_rouge'], RPi.GPIO.IN)     #Ce Capteur est un Laser sur le PIN 5 - Il est pour les Rouges

#Initilisation de la manette
try:
    pygame.init()                                #Init de Pygame
    mon_joystick = pygame.joystick.Joystick(0)   #Touche 0 correspond au bouton Start
    mon_joystick.init()
except:
    pass

#Initialisation du compteur de match
m = 0
i = 0
j = 0
Last_Goal = 0

# 2 - GESTION DE L'ATTENTE D'UN DEBUT DE MATCH_____________________
# Programme qui tourne à l'infini
lg.info("DEBUT DU PROGRAMME")
while True:
    lg.info("Vérification de la base Live en cours")
    # On vérifie si la base Live contient quelque chose
    try:
        requete,connexion = fonction_database.fonction_connexion_sqllite()
        requete.execute("SELECT count(*) FROM PROD_LIVE_MATCH")
        test_score = requete.fetchone()
        fonction_database.fonction_connexion_sqllite_fermeture(requete,connexion)
        nb_rows = test_score[0]

        if nb_rows > 0:
            # Si elle contient une ligne, c'est qu'un match doit démarrer
            lg.info("On peut démarrer un match")

            #################################
            # 3 - DEROULE DU MATCH
            #################################
            #Initialisation du début de match
            m += 1					#On incrémente le match dès le début
            i=0                     #i = Equipe Bleue
            j=0                     #j = Equipe Rouge
            Last_Goal = 0           # Pas de dernier but pour démarrer

            #Initialisation de l'heure de début de partie
            # Time de début de partie
            time_start = datetime.datetime.now()
            # Conversion pour stockage en caractère
            time_start_str = str('{0:%d/%m/%Y %H:%M:%S}'.format(time_start))

            #Début du match
            lg.info("Et c'est parti pour le " + str(m) + "e match de baby-foot à l'Avisia Arena!")
            # On rajoute du temps (5sec) avant de lancer le match et éviter les problèmes de détection
            time.sleep(5)


            #Boucle pour créer le match jusqu'au moment où une équipe arrive à 10
            while  i < 10 and j < 10:                                                       #Boucle de 10 buts
                #Buts pour les bleus
                if GPIO.input(DB['capteurs']['id_capteur_bleu']) == 0:
                    time_goal = datetime.datetime.now()                                     #Récupérer le time du but
                    time_goal_str = str('{0:%d/%m/%Y %H:%M:%S}'.format(time_goal))          #Conversion en format String pour stockage au bon format
                    i += 1                                                                  #Incrément du but marqué
                    Last_Goal = 1															#Ce but a été marqué par les bleus - utiliser pour l'annulation
                    lg.info("Buuuut des Bleus ! {}".format(time_goal_str))
                    interaction_database.live(time_goal_str, i, j, Last_Goal)               #Ecriture dans la table live
                    time.sleep(5)                                                           #On rajoute du temps (5sec) pour éviter les problèmes de détection

                #Buts pour les rouges
                elif GPIO.input(DB['capteurs']['id_capteur_rouge']) == 0:                   #Détection des mouvements sur le PIN 19
                    time_goal = datetime.datetime.now()                                     #Récupérer le time du but
                    time_goal_str = str('{0:%d/%m/%Y %H:%M:%S}'.format(time_goal))          #Conversion en format String pour stockage au bon format
                    j += 1                                                                  #Incrément du but marqué
                    Last_Goal = 2															#Ce but a été marqué par les bleus - utiliser pour l'annulation
                    lg.info("Buuuut des Rouges ! {}".format(time_goal_str))
                    interaction_database.live(time_goal_str, i, j, Last_Goal)                #Ecriture dans la table live
                    time.sleep(5)                                                           #On rajoute du temps (5sec) pour éviter les problèmes de détection

                #Annulation du dernier but
                for event in pygame.event.get():                                            #A tout moment on peut annuler un but
                    if event.type == pygame.JOYBUTTONDOWN:                                         #Quand un bouton est appuyé
                        if event.button == 0:                                               #Le bouton 0 correspond au bouton X
                            if Last_Goal == 1:                                              #Si le dernier but vient des bleus
                                i = i - 1                                                   #On retire le but
                                Last_Goal = -1                                              #En modifiant le Last Goal, on va empêcher la double annulation
                                lg.info("Oh le but n'est pas validé")
                                interaction_database.live(time_goal_str, i, j, Last_Goal)   #Ecriture dans la table live
                            elif Last_Goal == 2:                                            #Si le dernier but vient des rouge
                                j = j - 1                                                   #On retire le but
                                Last_Goal = -1                                              #En modifiant le Last Goal, on va empêcher la double annulation
                                lg.info("Oh le but n'est pas validé")
                                interaction_database.live(time_goal_str, i, j, Last_Goal)   #Ecriture dans la table live
                            elif Last_Goal == 0:                                            #Si c'est le premier but du match
                                i = 0                                                       #Les bleus reste à 0
                                j = 0                                                       #Les rouge reste à 0
                                Last_Goal = -1                                              #En modifiant le Last Goal, on va empêcher la double annulation
                                lg.info("Oh ce premier but n'est pas validé")
                                interaction_database.live(time_goal_str, i, j, Last_Goal)   #Ecriture dans la table live
                            elif Last_Goal == -1:                                           #En modifiant le Last Goal, on va empêcher la double annulation
                                lg.info("Pas de ça ici messieurs ! Bien essayé !\n\n")
# 4 - FIN DU MATCH

            #Affichage du résultat
            if i == 10:                                                                                 #Si les bleus arrivent à 10 buts
                lg.info("C'est donc terminé pour ce match. Victoire des Bleus")
            elif j == 10:                                                                               #Si les rouge arrivent à 10 buts
                lg.info("C'est donc terminé pour ce match. Victoire des Rouges")

    except Exception as e:
        lg.error("PROBLEME SUR LA TABLE LIVE")
        lg.error("{}".format(str(e)))
        pass

    #Après un match classique, on supprime la Table Live
    if i == 10 or j == 10:
        interaction_database.purge_live_match()
        # On réinitialise pour éviter que la purge continue de passer bloquant la base inutilement
        i = 0
        j = 0
        lg.info("PURGE DE LA TABLE LIVE_MATCH")

    time.sleep(10)  #Un check est fait toutes les 10 secondes pour savoir si un match commence

    # 5 - SORTIE DU PROGRAMME_____________________
    #Réinitialisation des capteurs
    GPIO.cleanup()
    lg.info("FIN DE LA BOUCLE")
