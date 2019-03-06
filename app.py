#!/usr/bin/env python
from importlib import import_module
import os
import cv2 as cv
from flask import Flask, render_template, Response

from camera import Camera
from detector import Detector
import threading
import time

app = Flask(__name__)
#Camera = Camera.Camera
detector = Detector()
camera = Camera()

last_frame = None
ret = None
rvecs = None
tvecs = None
diagnostic_img = None
keep_running = True


def detector_thread():
  global diagnostic_img
  while keep_running:
    # get the job from the front of the queue
    frame, _ = camera.get_frame()
    ret, rvecs, tvecs, diagnostic_img = detector.solve(frame)
    time.sleep(0.1)

thread = threading.Thread(target = detector_thread)
# this ensures the thread will die when the main thread dies
# can set t.daemon to False if you want it to keep running
thread.daemon = True
thread.start()

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

@app.route('/diagnostic')
def diagnostic():
    """Video streaming home page."""
    return render_template('diagnostic.html')

@app.route('/both')
def both():
    """Video streaming home page."""
    return render_template('both.html')

def gen(camera):
    """Video streaming generator function."""
    while True:
        _, encoded_frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + encoded_frame + b'\r\n')

def diagnostic_gen(camera):
    """Video streaming generator function."""
    global diagnostic_img
    while True:
        # frame, _ = camera.get_frame()
        # ret, rvecs, tvecs, diagnostic_img = detector.solve(frame)

        encoded_diagnostic_img = cv.imencode('.jpg', diagnostic_img)[1].tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + encoded_diagnostic_img + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/diagnostic_feed')
def diagnostic_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(diagnostic_gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)

keep_running = False
camera.keep_running = False
