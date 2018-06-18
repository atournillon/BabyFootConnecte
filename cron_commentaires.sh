#!/bin/sh
if ps -ef | grep -v grep | grep commentaires_live.py ; then
        echo "deja ok"
        exit 0
else
        echo "launch"
        cd /home/pi/Documents/BabyFootConnecte
        nohup /usr/bin/python data/commentaires_live.py &
        exit 0
fi
