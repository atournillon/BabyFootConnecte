#!/bin/sh
if ps -ef | grep -v grep | grep api_statistique.py ; then
        exit 0
else
        #source /opt/anaconda/bin/activate py27
        cd /home/pi/Documents/BabyFootConnecte
        nohup /usr/bin/python3.5 statistics/api_statistique.py &
        exit 0
fi