#!/usr/bin/python
#coding: utf8

from subprocess import PIPE, Popen
import json
from slacker import Slacker
import sys
sys.path.append("slack")
import fonction_slack

with open('config.json') as conf_file:
    global DB
    DB = json.load(conf_file)

slackClient,channel = fonction_slack.fonction_connexion_slack("channel_usage")

def get_cpu_temperature():
    """get cpu temperature using vcgencmd"""
    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
    output, _error = process.communicate()
    return float(output[output.index('=') + 1:output.rindex("'")])

messageToChannel = "La température est de : " + str(get_cpu_temperature()) + " °C"

slackClient.chat.post_message(channel,messageToChannel)
