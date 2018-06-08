#!/usr/bin/python
#coding: utf8

import sys
sys.path.append('data')
import fonction_database
sys.path.append('app/lib')
import interaction_database_app

def add_goal_bleu():
    cur, conn=fonction_database.fonction_connexion_sqllite()
    cur.execute("UPDATE PROD_LIVE_MATCH SET score_b=score_b+1")
    fonction_database.fonction_connexion_sqllite_fermeture(cur, conn)

def add_goal_rouge():
    cur,conn=fonction_database.fonction_connexion_sqllite()
    cur.execute("UPDATE PROD_LIVE_MATCH SET score_r=score_r+1")
    fonction_database.fonction_connexion_sqllite_fermeture(cur, conn)

interaction_database_app.init_prod_live_match()
add_goal_bleu()