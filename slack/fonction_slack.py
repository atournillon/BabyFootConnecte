#!/usr/bin/python
#coding: utf8

import json
import datetime
from slacker import Slacker

with open('config.json') as conf_file:
    global DB
    DB = json.load(conf_file)

def fonction_connexion_slack(choose):
    #Fonction pour se connecter à slack
    token_slack = DB['slack']['token']
    slackClient = Slacker(token_slack)
    channel = DB['slack'][choose]
    return slackClient,channel
