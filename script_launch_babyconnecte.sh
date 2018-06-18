#!/usr/bin/env bash

cd /home/pi/Documents/BabyFootConnecte
# Launch capteurs avec native python
nohup /usr/bin/python capteurs/match.py &


# Activation de lenv
# source /opt/anaconda/bin/activate py27

# Launch de api statistique
nohup /usr/bin/python3.5 statistics/api_statistique.py &
# Launch app flask
nohup /usr/bin/python app/app.py &
# Launch commentaires_live
nohup /usr/bin/python data/commentaires_live.py &


