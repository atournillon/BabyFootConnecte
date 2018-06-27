#!/bin/sh

if ps -ef | grep -v grep | grep match.py ; then
    pkill -f -9 match.py
    echo "kill ok match"
else
    echo "deja ok"
fi


#if ps -ef | grep -v grep | grep api_statistique.py ; then
#    pkill -f -9 api_statistique.py
#    echo "kill ok api_statistique"
#else
#    echo "deja ok"
#fi
