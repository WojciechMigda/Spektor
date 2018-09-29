import requests
import json


def spektor_url(endpoint):
    return 'http://127.0.0.1:6900/api/' + endpoint


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


def save_image_as_bytes(image_as_bytes):
    import base64

    url = spektor_url('image')

    image_as_b64 = base64.b64encode(image_as_bytes).decode('utf8')

    thumb_as_bytes = thumb_from_bytes(image_as_bytes)
    thumb_as_b64 = base64.b64encode(thumb_as_bytes).decode('utf8')

    rv = requests.post(url, json=dict(image=image_as_b64, thumb=thumb_as_b64))
    assert(rv.status_code == 201)
    js = json.loads(rv.text)
    image_id = js['id']
    return image_id


def save_persona(FIRST, LAST, NOTES, image_id):
    url = spektor_url('persona')
    rv = requests.post(url, json=dict(first_name=FIRST, last_name=LAST, notes=NOTES, mugshot=image_id))
    assert(rv.status_code == 201)
    js = json.loads(rv.text)
    persona_id = js['id']
    return persona_id


def save_avatar(persona_id, face_id):
    url = spektor_url('avatar')
    rv = requests.post(url, json=dict(persona_id=persona_id, face_id=face_id))
    assert(rv.status_code == 201)
    js = json.loads(rv.text)
    avatar_id = js['id']
    return avatar_id


def maybe_save_face(face_id, image_id, top, bottom, left, right, embedding):
    url = spektor_url('face')

    # first check of there's one already

    rv = requests.get(url, params=dict(q='{"filters":[{"name":"uuid","op":"eq","val":"' +  face_id + '"}]}'))
    js = json.loads(rv.text)
    assert(rv.status_code == 200)

    not_exists = (js['num_results'] == 0)
    if not_exists:
        rv = requests.post(url, json=dict(uuid=face_id,
                                      image_id=image_id,
                                      top=top,
                                      bottom=bottom,
                                      left=left,
                                      right=right,
                                      embedding=embedding))
        js = json.loads(rv.text)
        assert(rv.status_code == 201)

    return face_id, not_exists
