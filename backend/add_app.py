import logging
logging.basicConfig(level=logging.DEBUG)


def thumb_from_bytes(bytes, height=200):
    from io import BytesIO
    istream = BytesIO(bytes)
    from PIL import Image, ImageOps
    im = Image.open(istream)
    size = im.size # (int, int)
    ratio = max(size[1] / height, 1.0)
    thumb = ImageOps.fit(im, (int(round(size[0] / ratio)), int(round(size[1] / ratio))), Image.ANTIALIAS)
    ostream = BytesIO()
    thumb.save(ostream, 'JPEG', quality=60)
    ostream.seek(0)
    return ostream.read()


def brain_url(endpoint):
    return 'http://127.0.0.1:5000/spektor/' + endpoint


def spektor_url(endpoint):
    return 'http://127.0.0.1:6900/api/' + endpoint


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
        r = d['rectangle']
        h = r['top'] - r['bottom']
        w = r['left'] - r['right']
        return abs(w * h)

    largest = max(faces, key=largest_face)


    if UI:
        while FIRST is None or len(FIRST) == 0:
            FIRST = input(">>> Please enter persona's first name:\n... ")
        while LAST is None or len(LAST) == 0:
            LAST = input(">>> Please enter persona's last name:\n... ")
        if NOTES is None:
            NOTES = input(">>> Please enter persona's description:\n... ")


    # store image in the db

    url = spektor_url('image')
    import base64
    infile.seek(0) # detect above has read till EOF
    image_as_bytes = infile.read()
    image_as_b64 = base64.b64encode(image_as_bytes).decode('utf8')

    thumb_as_bytes = thumb_from_bytes(image_as_bytes)
    thumb_as_b64 = base64.b64encode(thumb_as_bytes).decode('utf8')

    rv = requests.post(url, json=dict(image=image_as_b64, thumb=thumb_as_b64))
    assert(rv.status_code == 201)
    js = json.loads(rv.text)
    image_id = js['id']

    # store persona

    url = spektor_url('persona')
    rv = requests.post(url, json=dict(first_name=FIRST, last_name=LAST, notes=NOTES, mugshot=image_id))
    assert(rv.status_code == 201)
    js = json.loads(rv.text)
    persona_id = js['id']

    # store face

    url = spektor_url('face')
    face_id = largest['rectangle']['uuid']

    # first check of there's one already

    rv = requests.get(url, params=dict(q='{"filters":[{"name":"uuid","op":"eq","val":"' +  face_id + '"}]}'))
    js = json.loads(rv.text)
    assert(rv.status_code == 200)

    if js['num_results'] == 0:
        rv = requests.post(url, json=dict(uuid=face_id,
                                      image_id=image_id, top=largest['rectangle']['top'],
                                      bottom=largest['rectangle']['bottom'],
                                      left=largest['rectangle']['left'],
                                      right=largest['rectangle']['right'],
                                      embedding=json.dumps(largest['rectangle']['embedding'])
                                      ))
        js = json.loads(rv.text)
        assert(rv.status_code == 201)

    # store avatar

    url = spektor_url('avatar')
    rv = requests.post(url, json=dict(persona_id=persona_id, face_id=face_id))
    assert(rv.status_code == 201)

    pass
