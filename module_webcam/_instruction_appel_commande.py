# !/usr/bin/python
# coding: utf8



import requests
t=requests.get('http://localhost:3574/go_webcam')
t

t=requests.get('http://localhost:3574/kill_webcam')
t


import datetime
t=requests.post('http://localhost:3574/generation_video_but',data={'but':datetime.datetime.strftime(datetime.datetime.now(),'%Y%m%d_%H_%M_%S_%f')})


import os
os.system("scp 004_module_raspberry/_video_output/" + moment_but_datetime_debut + ".avi admin@192.168.1.54:/tmp/")

