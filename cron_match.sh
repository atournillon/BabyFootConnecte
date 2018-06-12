#!/bin/sh
if ps -ef | grep -v grep | grep match.py ; then
        echo "deja ok"
        exit 0
else
        echo "launch"
        cd /home/pi/Documents/BabyFootConnecte
        nohup /usr/bin/python capteurs/match.py &
        exit 0
fi