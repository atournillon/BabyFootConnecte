# !/usr/bin/python
# coding: utf8

# import the necessary packages
from threading import Thread
import cv2
import datetime
import imutils
#Pour vider le dossier _image_init
import os, shutil

class WebcamVideoStream:
    def __init__(self, src=0):
        # On vide le dossier contenant les images lors du démarrage du programme
        folder = 'module_webcam/_image_init'
        for the_file in os.listdir(folder):
            if the_file != '.keep':
                file_path = os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    # elif os.path.isdir(file_path): shutil.rmtree(file_path)
                except Exception as e:
                    print(e)

        # Initialisation de la webcam
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()

        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                cv2.destroyAllWindows()
                self.stream.release()
                return

            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()
            # Export des images dans un dossier
            imutils.resize(self.frame, width=400)
            cv2.imwrite("module_webcam/_image_init/" + datetime.datetime.strftime(datetime.datetime.now(),
                                                                                        '%Y%m%d_%H_%M_%S_%f') + ".jpg",
                        self.frame)

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
