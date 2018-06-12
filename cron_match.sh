#!/bin/sh
if ps -ef | grep -v grep | grep match.py ; then
        exit 0
else
        cd /home/pi/Documents/BabyFootConnecte
        nohup /usr/bin/python capteurs/match.py &
        exit 0
fi