#!/usr/bin/env bash

cd /home/pi/Documents/BabyFootConnecte
# Launch capteurs avec native python
nohup /usr/bin/python capteurs/match.py &


# Activation de lenv
source /opt/anaconda/bin/activate py27

# Launch de api statistique
nohup python statistics/api_statistique.py &
# Launch app flask
nohup python app/app.py &


