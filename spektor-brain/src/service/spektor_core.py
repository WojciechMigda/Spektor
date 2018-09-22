import flask as F
from flask import Flask

import dlib
import openface

import spektor_impl as impl

app = Flask('spektor')

def do_error(s):
    return F.jsonify(dict(success=False, message=s))


def do_success(r):
    return F.jsonify(dict(success=True, result=r))


@app.errorhandler(OSError)
def handle_bad_request(e):
    # Exception handler for image loading error
    return do_error(str(e))


@app.route('/spektor/hello', methods=['POST'])
def on_hello():
    return impl.on_hello(app)


@app.route('/spektor/detect', methods=['POST'])
def on_detect():
    return impl.on_detect(app, F.request)



def initialize_logging(app, DEBUG):
    import logging
    formatter = logging.Formatter('%(asctime)s.%(msecs)03d:%(levelname)s:%(name)s:%(message)s', datefmt='%Y-%m-%dT%H:%M:%S')
    app.logger.handlers[0].setFormatter(formatter)

    #app.debug = DEBUG
    app.logger.handlers[0].setLevel(logging.DEBUG if DEBUG else logging.INFO)

    return


def initialize_models(app, DIM):
    app.config.update(DIM=DIM)

    predictor_model = "data/shape_predictor_68_face_landmarks.dat"
    face_detector = dlib.get_frontal_face_detector()
    face_aligner = openface.AlignDlib(predictor_model)

    app.config.update(face_detector=face_detector)
    app.config.update(face_aligner=face_aligner)

    net = openface.TorchNeuralNet('data/nn4.small2.v1.t7', DIM)
    app.config.update(net=net)

    return


def work(DEBUG, APP_HOST, APP_PORT, DIM):

    initialize_logging(app, DEBUG)

    app.logger.info('Starting app')

    app.logger.info('Models loading..')
    initialize_models(app, DIM)
    app.logger.info('Done.')


    """
    Having an option to pass an IP address which will be used by Flask
    will enable both being able to run the app locally and in a container.
    """
    app.logger.info('App ready!')

    import time
    app.config.update(started=time.time())

    app.run(host=APP_HOST, port=APP_PORT)
