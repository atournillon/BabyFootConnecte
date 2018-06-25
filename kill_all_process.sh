#!/bin/sh

if ps -ef | grep -v grep | grep app.py ; then
    pkill -f app.py
    echo "deja ok"
    exit 0
else
    echo "deja ok"
    exit 0
fi

if ps -ef | grep -v grep | grep match.py ; then
    pkill -f match.py
    echo "deja ok"
    exit 0
else
    echo "deja ok"
    exit 0
fi


if ps -ef | grep -v grep | grep api_statistique.py ; then
    pkill -f api_statistique.py
    echo "deja ok"
    exit 0
else
    echo "deja ok"
    exit 0
fi



