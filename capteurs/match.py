# !/usr/bin/python
# coding: utf8

########################################
# BABY FOOT Connecté
# Programme pour compter les buts d'un match de Baby-Foot à partir de capteurs MC005
# 1 - INITIALISATION_________________________

import logging as lg
import os
import os.path
import json
import time
import datetime
import sys
from threading import Thread
from slacker import Slacker
from subprocess import PIPE, Popen
sys.path.append("data")
import fonction_database

sys.path.append("capteurs/lib")
import interaction_database

#Import de la librairie pour les capteurs
try:
    import RPi.GPIO as GPIO
    rpi=1
except:
    import fake_rpi
    sys.modules['RPi'] = fake_rpi.RPi                                   # Fake RPi (GPIO)
    sys.modules['smbus'] = fake_rpi.smbus                               # Fake smbus (I2C)
    import RPi
    rpi=0


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
if rpi==0:
    lg.info("FAKE RPi")
    #RPi.GPIO.setwarnings(False)                                        #Désactive le Warning
    RPi.GPIO.setmode(RPi.GPIO.BOARD)                                    #Mode BCM si on utilise un BreadBoard
    RPi.GPIO.setup(DB['capteurs']['id_capteur_bleu'], RPi.GPIO.IN)      #Ce Capteur est un Laser sur le PIN 18 - Il est pour les Bleus
    RPi.GPIO.setup(DB['capteurs']['id_capteur_rouge'], RPi.GPIO.IN)     #Ce Capteur est un Laser sur le PIN 5 - Il est pour les Rouges
else:
    #GPIO.setwarnings(False)                                            #Désactive le Warning
    GPIO.setmode(GPIO.BOARD)                                        #Mode BCM si on utilise un BreadBoard
    GPIO.setup(DB['capteurs']['id_capteur_bleu'], GPIO.IN)              #Ce Capteur est un Laser sur le PIN 18 - Il est pour les Bleus
    GPIO.setup(DB['capteurs']['id_capteur_rouge'], GPIO.IN)             #Ce Capteur est un Laser sur le PIN 5 - Il est pour les Rouges

#Initilisation de la manette
try:
    pygame.init()                                                       #Init de Pygame
    mon_joystick = pygame.joystick.Joystick(0)                          #Touche 0 correspond au bouton Start
    mon_joystick.init()
except:
    pass

#Initialisation du compteur de match
m = 0
i = 0
j = 0
Last_Goal = 0

def get_cpu_temperature():
    """get cpu temperature using vcgencmd"""
    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
    output, _error = process.communicate()
    return float(output[output.index('=') + 1:output.rindex("'")])

class but(Thread):
    def __init__(self, team, i, j, Last_Goal):
        Thread.__init__(self)
        self.team = team
        self.i = i
        self.j = j
        self.Last_Goal = Last_Goal

    def run(self):
        time_goal = datetime.datetime.now()                                                 #Récupérer le time du but
        time_goal_str = str('{0:%d/%m/%Y %H:%M:%S}'.format(time_goal))                      #Conversion en format String pour stockage au bon format
        os.system("mpg321 -q data/audio/sifflet1.mp3")
        lg.info("Coup de sifflet")
        if self.team=="bleu":
            lg.info("Buuuut des Bleus ! {}".format(time_goal_str))
        elif self.team=="rouge":
            lg.info("Buuuut des Rouges ! {}".format(time_goal_str))
        lg.info("{}".format(str(self.i)))
        lg.info("{}".format(str(self.j)))
        interaction_database.live(time_goal_str, self.i, self.j, self.Last_Goal)            #Ecriture dans la table live
        time.sleep(6)                                                                       #On rajoute du temps (5sec) pour éviter les problèmes de détection

class commentaire(Thread):
    def __init__(self, team, i, j):
        Thread.__init__(self)
        self.team = team
        self.i = i
        self.j = j

    def run(self):
        if self.team=="bleu":
            if self.i == self.j:
                os.system("mpg321 -q data/audio/egalite.mp3")
                lg.info("Il y a egalite au score")
            else:
                filexist = 0
                while filexist < 1:
                    commentaire = requete.execute('''select id_comment from PROD_REF_COMMENTS where (team = 'bleu' or team = 'lesdeux') and scenario = 'but' order by random() limit 1 ''').fetchall()
                    commentaire_TTS = str(commentaire[0][0])
                    if os.path.exists("data/audio/com" + commentaire_TTS + ".mp3") == True:
                        filexist=1
                        os.system("mpg321 -q data/audio/com" + commentaire_TTS + ".mp3")
                        lg.info("commentaire data/audio/com" + commentaire_TTS + ".mp3")
        elif self.team=="rouge":
            if self.j == self.i:
                os.system("mpg321 -q data/audio/egalite.mp3")
                lg.info("Il y a egalite au score")
            elif self.j-self.i == 5:
                os.system("mpg321 -q data/audio/allez_les_bleus.mp3")
                lg.info("Encouragement des bleus qui galerent")
            else:
                filexist = 0
                while filexist < 1:
                    commentaire = requete.execute('''select id_comment from PROD_REF_COMMENTS where (team = 'rouge' or team = 'lesdeux') and scenario = 'but' order by random() limit 1 ''').fetchall()
                    commentaire_TTS = str(commentaire[0][0])
                    if os.path.exists("data/audio/com" + commentaire_TTS + ".mp3") == True:
                        filexist=1
                        os.system("mpg321 -q data/audio/com" + commentaire_TTS + ".mp3")
                        lg.info("Commentaire data/audio/com" + commentaire_TTS + ".mp3")

# 2 - GESTION DE L'ATTENTE D'UN DEBUT DE MATCH_____________________
# Programme qui tourne à l'infini
lg.info("DEBUT DU PROGRAMME")
start = time.time()
while True:
    lg.info("Vérification de la base Live en cours")
    # On vérifie si la base Live contient quelque chose
    try:
        requete,connexion = fonction_database.fonction_connexion_sqllite()
        requete.execute("SELECT count(*) FROM PROD_LIVE_MATCH")
        test_score = requete.fetchone()
        #fonction_database.fonction_connexion_sqllite_fermeture(requete,connexion)
        nb_rows = test_score[0]
        b, r = interaction_database.read_live()
        i = b
        j = r       
        
        if rpi==1:
            end = time.time()
            interval = end - start
            
            if interval >= 300:
                slackClient,channel_temp = fonction_database.fonction_temperature_slack()

                # Temperature
                temperature = get_cpu_temperature()
                lg.info("Temperature : " + str(temperature))

                slackClient.chat.post_message(channel_temp,"La température est de : "+str(temperature)+" °C")
                
                start = end

        if nb_rows > 0 and i == 0 and j == 0:
            # Si elle contient une ligne, c'est qu'un match doit démarrer
            lg.info("On peut démarrer un match")
            
            slackClient,channel = fonction_database.fonction_connexion_slack()

            # Lancement des festivites
            os.system("mpg321 -q data/audio/ea_sport.mp3")
            lg.info("Son EA Sport")

            #################################
            # 3 - DEROULE DU MATCH
            #################################
            #Initialisation du début de match
            m += 1					#On incrémente le match dès le début
            #i=0                     #i = Equipe Bleue
            #j=0                     #j = Equipe Rouge
            Last_Goal = 0           # Pas de dernier but pour démarrer

            # Initialisation de l'heure de début de partie
            # Time de début de partie
            time_start = datetime.datetime.now()
            # Conversion pour stockage en caractère
            time_start_str = str('{0:%d/%m/%Y %H:%M:%S}'.format(time_start))

            #Début du match
            lg.info("Et c'est parti pour le " + str(m) + "e match de baby-foot à l'Avisia Arena!")
            # On rajoute du temps (5sec) avant de lancer le match et éviter les problèmes de détection
            time.sleep(5)


            #Boucle pour créer le match jusqu'au moment où une équipe arrive à 10
            while  i < 10 and j < 10:                                                           #Boucle de 10 buts
                if rpi==0:
                    #Buts pour les bleus
                    if RPi.GPIO.input(DB['capteurs']['id_capteur_bleu']) == 0:
                        b, r = interaction_database.read_live()
                        i = b + 1                                                               #Incrément du but marqué
                        j = r
                        Last_Goal = 1                                                           #Ce but a été marqué par les bleus - utiliser pour l'annulation
                        thread_1 = but("bleu",i,j,Last_Goal)
                        thread_2 = commentaire("bleu",i,j)
                        lg.info("Démarrage Thread 1 BUT")
                        lg.info("Démarrage Thread 2 COMMENTAIRE")
                        thread_1.start()
                        thread_2.start()
                        thread_1.join()
                        thread_2.join()
                        lg.info("Fin Thread 1 BUT")
                        lg.info("Fin Thread 2 COMMENTAIRE")

                    #Buts pour les rouges
                    if RPi.GPIO.input(DB['capteurs']['id_capteur_rouge']) == 0:                 
                        b, r = interaction_database.read_live()
                        j = r + 1                                                               #Incrément du but marqué
                        i = b
                        Last_Goal = 2                                                           #Ce but a été marqué par les bleus - utiliser pour l'annulation
                        thread_1 = but("rouge",i,j,Last_Goal)
                        thread_2 = commentaire("rouge",i,j)
                        lg.info("Démarrage Thread 1 BUT")
                        lg.info("Démarrage Thread 2 COMMENTAIRE")
                        thread_1.start()
                        thread_2.start()
                        thread_1.join()
                        thread_2.join()
                        lg.info("Fin Thread 1 BUT")
                        lg.info("Fin Thread 2 COMMENTAIRE")
                else:
                    #Buts pour les bleus
                    if GPIO.input(DB['capteurs']['id_capteur_bleu']) == 0:
                        b, r = interaction_database.read_live()
                        i = b + 1                                                               #Incrément du but marqué
                        j = r
                        Last_Goal = 1                                                           #Ce but a été marqué par les bleus - utiliser pour l'annulation
                        thread_1 = but("bleu",i,j,Last_Goal)
                        thread_2 = commentaire("bleu",i,j)
                        lg.info("Démarrage Thread 1 BUT")
                        lg.info("Démarrage Thread 2 COMMENTAIRE")
                        thread_1.start()
                        thread_2.start()
                        thread_1.join()
                        thread_2.join()
                        lg.info("Fin Thread 1 BUT")
                        lg.info("Fin Thread 2 COMMENTAIRE")

                    #Buts pour les rouges
                    if GPIO.input(DB['capteurs']['id_capteur_rouge']) == 0:                     
                        b, r = interaction_database.read_live()
                        j = r + 1                                                               #Incrément du but marqué
                        i = b
                        Last_Goal = 2                                                           #Ce but a été marqué par les bleus - utiliser pour l'annulation
                        thread_1 = but("rouge",i,j,Last_Goal)
                        thread_2 = commentaire("rouge",i,j)
                        lg.info("Démarrage Thread 1 BUT")
                        lg.info("Démarrage Thread 2 COMMENTAIRE")
                        thread_1.start()
                        thread_2.start()
                        thread_1.join()
                        thread_2.join()
                        lg.info("Fin Thread 1 BUT")
                        lg.info("Fin Thread 2 COMMENTAIRE")  
                try:
                    #Annulation du dernier but
                    for event in pygame.event.get():                                            #A tout moment on peut annuler un but
                        if event.type == pygame.JOYBUTTONDOWN:                                  #Quand un bouton est appuyé
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
                except:
                    pass
                    #lg.info('pas de joystick')
# 4 - FIN DU MATCH

            os.system("mpg321 -q data/audio/applaudissements1.mp3")
            lg.info("Applaudissements car fin du match")

            # Affichage du résultat
            if i == 10:                                                                          #Si les bleus arrivent à 10 buts
                fonction_database.fonction_connexion_sqllite_fermeture(requete,connexion)
                lg.info("C'est donc terminé pour ce match. Victoire des Bleus")
                if rpi==0:
                    messageToChannel = "[test local] Hello, Victoire des Bleus " + str(i) + " - " + str(j)
                else:
                    messageToChannel = "Hello, Victoire des Bleus " + str(i) + " - " + str(j)
                slackClient.chat.post_message(channel,messageToChannel)
                lg.info("Push du match sur slack")
            elif j == 10:                                                                        #Si les rouge arrivent à 10 buts
                fonction_database.fonction_connexion_sqllite_fermeture(requete,connexion)
                lg.info("C'est donc terminé pour ce match. Victoire des Rouges")
                if rpi==0:
                    messageToChannel = "[test local] Hello, Victoire des Rouges " + str(j) + " - " + str(i)
                else:
                    messageToChannel = "Hello, Victoire des Rouges " + str(j) + " - " + str(i)
                slackClient.chat.post_message(channel,messageToChannel)
                lg.info("Push du match sur Slack")

    except Exception as e:
        lg.error("PROBLEME SUR LA TABLE LIVE")
        lg.error("{}".format(str(e)))
        pass

    #Après un match classique, on supprime la Table Live
    if i == 10 or j == 10:
        #interaction_database.purge_live_match()
        # On réinitialise pour éviter que la purge continue de passer bloquant la base inutilement
        #i = -1
        #j = -1
        lg.info("PURGE DE LA TABLE LIVE_MATCH")

    time.sleep(10)  #Un check est fait toutes les 10 secondes pour savoir si un match commence

    # 5 - SORTIE DU PROGRAMME_____________________
    #Réinitialisation des capteurs
    #GPIO.cleanup()
    lg.info("FIN DE LA BOUCLE")
