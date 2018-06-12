#!/bin/sh
if ps -ef | grep -v grep | grep app.py ; then
        exit 0
else
        cd /home/pi/Documents/BabyFootConnecte
        nohup /usr/bin/python app/app.py &
        exit 0
fi
