#!/bin/sh
if ps -ef | grep -v grep | grep api_statistique.py ; then
        echo "deja ok"
        exit 0
else
        echo "launch"
        #source /opt/anaconda/bin/activate py27
        cd /home/pi/Documents/BabyFootConnecte
        nohup /usr/bin/python3.5 statistics/api_statistique.py &
        exit 0
fi