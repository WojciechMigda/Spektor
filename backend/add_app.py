import logging
logging.basicConfig(level=logging.DEBUG)

from db_tools import spektor_url, save_image_as_bytes, save_persona, save_avatar, maybe_save_face


def brain_url(endpoint):
    return 'http://127.0.0.1:5000/spektor/' + endpoint


def work(UI, FIRST, LAST, NOTES, infile):

    if UI:
        if infile is None:
            import tkinter
            from tkinter import filedialog as tkfiledialog

            tkinter.Tk().withdraw()

            print('>>> Please select input image')
            fname = tkfiledialog.askopenfilename(multiple=0)
            if len(fname) == 0:
                print('No file was selected. Quitting..')
                return
            print('Selected {}'.format(fname))
            infile = open(fname, 'rb')


    import requests
    import json

    url = brain_url('detect')
    rv = requests.post(url, files=dict(file=infile))
    assert(rv.status_code == 200)
    js = json.loads(rv.text)
    if js['success'] == False:
        print(js)
        assert(js['success'])
    rv = js['result']

    faces = rv['faces']

    if len(faces) == 0:
        print('No face was detected in the selected image. Quiting..')
        return

    print('Found {} faces'.format(len(faces)))

    def largest_face(d):
        h = r['top'] - r['bottom']
        w = r['left'] - r['right']
        return abs(w * h)

    def best_face(d):
        r = d['rectangle']
        return r['confidence']

    primary = max(faces, key=best_face)

    if UI:
        while FIRST is None or len(FIRST) == 0:
            FIRST = input(">>> Please enter persona's first name:\n... ")
        while LAST is None or len(LAST) == 0:
            LAST = input(">>> Please enter persona's last name:\n... ")
        if NOTES is None:
            NOTES = input(">>> Please enter persona's description:\n... ")


    # store image in the db
    infile.seek(0) # rewind, because 'detect' above has already read till EOF
    image_as_bytes = infile.read()
    image_id = save_image_as_bytes(image_as_bytes)

    # store persona
    persona_id = save_persona(FIRST, LAST, NOTES, image_id)

    # store face
    face_id, _ = maybe_save_face(primary['rectangle']['uuid'], image_id,
                                 top=primary['rectangle']['top'],
                                 bottom=primary['rectangle']['bottom'],
                                 left=primary['rectangle']['left'],
                                 right=primary['rectangle']['right'],
                                 embedding=primary['rectangle']['embedding'])

    # store avatar
    save_avatar(persona_id, face_id)

    pass
