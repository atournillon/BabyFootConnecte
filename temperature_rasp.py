#!/usr/bin/python
#coding: utf8

from subprocess import PIPE, Popen
import json
from slacker import Slacker

with open('config.json') as conf_file:
    global DB
    DB = json.load(conf_file)

token_slack = DB['slack']['token']
slackClient = Slacker(token_slack)
channel = DB['slack']['channel']

def get_cpu_temperature():
    """get cpu temperature using vcgencmd"""
    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
    output, _error = process.communicate()
    return float(output[output.index('=') + 1:output.rindex("'")])

slackClient.chat.post_message(channel,"La température est de : "+str(get_cpu_temperature())+" °C")