# !/usr/bin/python
# coding: utf8


#sudo apt-get update
#sudo apt-get install python-numpy
#sudo apt-get update
#sudo apt-get install python-opencv
#sudo apt-get install python-scipy
#sudo apt-get install ipython
#sudo apt-get install libgl1-mesa-dri
#python2.7 module_webcam/001_lancement_webcam.py


import logging as lg
import datetime
# Initialisation de la log
t = datetime.datetime.now()
fn = 'logs/run_api_webcam.{}.log'.format(t.strftime("%Y-%m-%d"))
lg.basicConfig(filename = fn,
               level = lg.DEBUG,
               filemode = 'a',
               format = '%(asctime)s\t%(levelname)s\t%(message)s',
               datefmt = '%Y-%m-%d %H:%M:%S'
               )

# import the necessary packages
import sys
sys.path.append('module_webcam/class')

from WebcamVideoStream import *
import cv2
from PIL import Image
import imutils

# Pour la partie API
from flask import Flask, Response, request
import json
import numpy as np
import os
from os.path import isfile, join

app = Flask(__name__)


# created a *threaded* video stream, allow the camera sensor to warmup,
@app.route('/go_webcam')
def go_webcam():
    # Recuperation du timestamp au format texte
    # datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d_%H_%M_%S_%f')})
    global vs
    vs = WebcamVideoStream(src=0).start()
    return "ok"

@app.route('/kill_webcam')
def kill_webcam():
    # Recuperation du timestamp au format texte
    # datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d_%H_%M_%S_%f')})
    vs.stop()
    return "ok stop"


#Fonction permettant de passer des images vers la video
def convert_frames_to_video(pathIn, pathOut, time_but,fps):
    frame_array = []
    files = [f for f in os.listdir(pathIn) if isfile(join(pathIn, f))]
    files = [f for f in files if f != '.keep']
    files_fin = [f for f in files if datetime.datetime.strptime(f.replace('.jpg',''),'%Y%m%d_%H_%M_%S_%f') > time_but]

    # for sorting the file names properly
    files_fin.sort(key=lambda x: x.replace('.jpg', ''))
    for i in range(len(files_fin)):
        filename = pathIn + files_fin[i]
        # reading each files
        img = cv2.imread(filename)
        height, width, layers = img.shape
        size = (width, height)
        # inserting the frames into an image array
        frame_array.append(img)

    out = cv2.VideoWriter(pathOut, cv2.cv.CV_FOURCC('M','J','P','G'), fps, size)

    for i in range(len(frame_array)):
        # writing to a image array
        out.write(frame_array[i])
    out.release()



@app.route('/generation_video_but', methods=['POST'])
def generation_but():
    if request.method == 'POST':
        # Recuperation du timestamp au format texte
        # datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d_%H_%M_%S_%f')})
        moment_but = request.form['but']

        print(moment_but)
        #moment_but='20180602_12_49_00_550869'
        moment_but_datetime=datetime.datetime.strptime(moment_but,'%Y%m%d_%H_%M_%S_%f')

        # 5 secondes avant le but
        moment_but_datetime_debut=moment_but_datetime + datetime.timedelta(seconds=-5)

        #Lancement de la fonction de création de la video
        pathIn = 'module_webcam/_image_init/'
        pathOut = 'module_webcam/_video_output/{}.avi'.format(moment_but)
        fps = 30

        convert_frames_to_video(pathIn, pathOut, moment_but_datetime_debut,fps)

        # Il faut maintenant envoyer la video sur la machine contenant l'api flask du site
        # il faut générer une lé et la copier sur l'autre raspberry
        # ssh-keygen
        # ssh-copy-id -i ~/.ssh/tatu-key-ecdsa user@host
        #import os
        #os.system("scp module_webcam/_video_output/"+datetime.datetime.strftime(moment_but_datetime,'%Y%m%d_%H_%M_%S_%f')+".avi admin@192.168.1.54:/tmp/")
        return 'ok'
    else:
        return 'ko'

# Lancement de l'app
if __name__ == '__main__':
    # Lancement de l'api flask
    app.run(debug=True, host='0.0.0.0', port=3574)



