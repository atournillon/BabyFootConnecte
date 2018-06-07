#!/usr/bin/python
#coding: utf8

import sqlite3
import json
with open('config.json') as conf_file:
    global DB
    DB = json.load(conf_file)


def fonction_connexion_sqllite():
    #Fonction pour ajouter un club dans la base
    fichierDonnees = DB['database']['prod']
    conn =sqlite3.connect(fichierDonnees)
    cur =conn.cursor()
    return cur,conn

def fonction_connexion_sqllite_fermeture(cur,conn):
    conn.commit()
    cur.close()
    conn.close()
