#!/bin/sh
if ps -ef | grep -v grep | grep app.py ; then
        echo "deja ok"
        exit 0
else
        echo "launch"
        cd /home/pi/Documents/BabyFootConnecte
        nohup /usr/bin/python app/app.py &
        exit 0
fi
