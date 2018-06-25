#!/bin/sh

if ps -ef | grep -v grep | grep app.py ; then
    pkill -f app.py
    echo "kill ok app"
else
    echo "deja ok"
fi

if ps -ef | grep -v grep | grep match.py ; then
    pkill -f match.py
    echo "kill ok match"
else
    echo "deja ok"
fi


if ps -ef | grep -v grep | grep api_statistique.py ; then
    pkill -f api_statistique.py
    echo "kill ok api_statistique"
else
    echo "deja ok"
fi



