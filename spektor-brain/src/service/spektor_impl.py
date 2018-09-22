import flask as F
from werkzeug.utils import secure_filename

import dlib
import openface


def do_error(s):
    return F.jsonify(dict(success=False, message=s))


def do_success(r):
    return F.jsonify(dict(success=True, result=r))


def on_hello(app):
    rv = dict(Hello=app.config['started'])
    return F.jsonify(rv)


def identify_faces(app, logger, stream, fname):
    import uuid
    import time
    time0 = time.time()

    from skimage import io as skio

    image = skio.imread(stream)

    #logger.info('Image: {}'.format(image.shape))

    face_detector = app.config['face_detector']
    face_aligner = app.config['face_aligner']
    net = app.config['net']

    face_rectangles = face_detector(image, 1)
    logger.info('Faces: {}'.format(face_rectangles))

    faces = []
    for i, fr in enumerate(face_rectangles):

        aligned_face = face_aligner.align(app.config['DIM'], image, fr, landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
        rep = net.forward(aligned_face)

        ident = uuid.UUID(int=hash(tuple(rep)) % 2 ** 128)
        face = {'rectangle': dict(left=fr.left(), top=fr.top(), right=fr.right(), bottom=fr.bottom(), embedding=list(rep), uuid=ident)}
        faces.append(face)

    return dict(filename=fname, shape=image.shape, faces=faces, time=time.time() - time0)


def on_detect(app, request):
    app.logger.info('In detect')

    if 'file' not in request.files:
        app.logger.warning('File not attached')
        return do_error('File not attached')
    file = request.files['file']

    if file.filename == '':
        app.logger.warning('Missing filename')
        return do_error('Missing filename')

    filename = secure_filename(file.filename)

    rv = identify_faces(app, app.logger, file, filename)

    return do_success(rv)
