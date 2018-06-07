# !/usr/bin/python
# coding: utf8

from threading import Thread, Event
import time
import socketio

import sys
import interaction_database_app

# New thread to get live data from the SQLITE DB
class LiveScoreThread(Thread):
    def __init__(self):
        self.delay = 1  # Query the DB each 1 second
        super(LiveScoreThread, self).__init__()

    def scoreLiveMatch(self):
        """
        Query the DB to get the live score each second
        Ideally to be run in a separate thread?
        """
        # infinite loop
        while not thread_stop_event.isSet():
            score_b, score_r = interaction_database_app.getData()
            socketio.emit('livematch', {'score_b': score_b, 'score_r': score_r}, namespace='/test')
            time.sleep(self.delay)

    def run(self):
        self.scoreLiveMatch()
