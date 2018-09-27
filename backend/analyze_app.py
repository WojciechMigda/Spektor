import logging
logging.basicConfig(level=logging.DEBUG)

"""
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
"""


def brain_url(endpoint):
    return 'http://127.0.0.1:5000/spektor/' + endpoint


def spektor_url(endpoint):
    return 'http://127.0.0.1:6900/api/' + endpoint


def analyze_face(face):
    import requests
    import json

    rect = face['rectangle']

    url = 'http://127.0.0.1:6900/spektor/analyze'
    rv = requests.post(url, json=dict(embedding=rect['embedding']))
    assert(rv.status_code == 200)
    matched_ranked = json.loads(rv.text)

    return matched_ranked


def analyze_faces(faces):
    return [analyze_face(face) for face in faces]


def analyze_image(infile):
    print('Analyzing {}'.format(infile.name))

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

    print('Found {} face(s) on {}'.format(len(faces), infile.name))
    return faces


def work(infiles):

    found_faces = [(infile, analyze_image(infile)) for infile in infiles]

    matched_faces = [(infile, faces, analyze_faces(faces)) for infile, faces in found_faces]

    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from skimage import io as skio

    for infile, faces, faces_scores in matched_faces:
        print('>>> Image {}'.format(infile.name))

        image = skio.imread(infile)
        fig, ax = plt.subplots(1)

        # Display the image
        ax.imshow(image)

        for face, ranked_scored in zip(faces, faces_scores):
            fr = face['rectangle']

            # Create a Rectangle patch
            rect = patches.Rectangle((fr['left'], fr['top']), fr['right'] - fr['left'], fr['bottom'] - fr['top'], linewidth=2, edgecolor='lightgreen', facecolor='none')

            # Add the patch to the Axes
            ax.add_patch(rect)
            plt.text(fr['left'], fr['bottom'], 'Richard Spencer',
                 va='top',
                 #weight='bold',
                 family='monospace',
                 color='w', bbox=dict(facecolor='black', alpha=0.5), size='small') # Valid font size are xx-small, x-small, small, medium, large, x-large, xx-large, larger, smaller, None

        plt.tight_layout()
        plt.show(block=False)
        input('Press any key')
        plt.close()

    """
    zapisac zdjecie w bazie
    zapisac embeddingi w bazie
    utworzyc nowe persony dla No Name
    zapisac nowe avatary
    """

    return




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
