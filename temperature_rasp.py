#!/usr/bin/python
#coding: utf8

from subprocess import PIPE, Popen
import json
from slacker import Slacker
sys.path.append("data")
import fonction_database

with open('config.json') as conf_file:
    global DB
    DB = json.load(conf_file)

slackClient,channel_temp = fonction_database.fonction_temperature_slack()

def get_cpu_temperature():
    """get cpu temperature using vcgencmd"""
    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
    output, _error = process.communicate()
    return float(output[output.index('=') + 1:output.rindex("'")])

slackClient.chat.post_message(channel_temp,"La température est de : "+str(get_cpu_temperature())+" °C")
