import logging
logging.basicConfig(level=logging.DEBUG)

from db_tools import spektor_url, save_image_as_bytes, save_persona, save_avatar, maybe_save_face


def brain_url(endpoint):
    return 'http://127.0.0.1:5000/spektor/' + endpoint


def analyze_face(face, NBEST):
    import requests
    import json

    rect = face['rectangle']

    url = 'http://127.0.0.1:6900/spektor/analyze'
    rv = requests.post(url, json=dict(embedding=rect['embedding'], nbest=NBEST))
    assert(rv.status_code == 200)
    matched_ranked = json.loads(rv.text)

    return matched_ranked


def analyze_faces(faces, NBEST):
    return [analyze_face(face, NBEST) for face in faces]


def analyze_image(infile, confidence_thr):
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

    # filter away detected faces with confidence level below threshold
    faces = [f for f in faces if f['rectangle']['confidence'] >= confidence_thr]

    if len(faces) == 0:
        print('No face with confidence score >= {} was detected in the selected image. Quiting..'.format(confidence_thr))
        return []

    print('Found {} face(s) on {}'.format(len(faces), infile.name))
    return faces


def names_by_ids(ids):
    import requests
    import json

    url = spektor_url('persona')

    rows = []
    page=1

    while True:
        rv = requests.get(url, params=dict(q='{"filters":[{"name":"id","op":"in","val":' +  str(ids) + '}]}', page=page))
        js = json.loads(rv.text)
        assert(rv.status_code == 200)
        rows.extend(js['objects'])
        if js['page'] >= js['total_pages']:
            break
        page += 1

    mapping = {row['id']: (row['first_name'], row['last_name']) for row in rows}
    rv = [mapping[id] for id in ids if id in mapping]
    return rv


def random_name():
    import string
    allchar = string.ascii_letters + string.digits

    import random
    rv = ('NoName', '#{}'.format("".join(random.choice(allchar) for x in range(10))))
    return rv


def crop_around_the_face(image, fr):
    # Create an outer Rectangle patch
    W = fr['right'] - fr['left']
    H = fr['bottom'] - fr['top']
    X = (fr['right'] + fr['left']) / 2
    Y = (fr['bottom'] + fr['top']) / 2
    print(W, H, X, Y)
    Xfactor = 0.8
    Yfactor = 1.0
    cutout = image.crop((int(X - Xfactor * W), int(Y - Yfactor * W), min(image.size[0], int(X + Xfactor * W)), min(image.size[1], int(Y + Yfactor * W))))

    from io import BytesIO
    ostream = BytesIO()
    cutout.save(ostream, 'JPEG', quality=80)
    ostream.seek(0)
    return ostream.read()



def work(DRYRUN, FACE_THR, MATCH_THR, infiles):

    found_faces = [(infile, analyze_image(infile, confidence_thr=FACE_THR)) for infile in infiles]

    matched_faces = [(infile, faces, analyze_faces(faces, NBEST=5)) for infile, faces in found_faces]

    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from PIL import Image

    for infile, faces, faces_scores in matched_faces:
        print('>>> Image {}'.format(infile.name))

        infile.seek(0)
        image_as_bytes = infile.read()
        image_id = DRYRUN or save_image_as_bytes(image_as_bytes)

        infile.seek(0)
        image = Image.open(infile)
        fig, ax = plt.subplots(1)

        # Display the image
        ax.imshow(image)

        all_found_names = []
        proposed_names = []

        for fid, (face, ranked_scored) in enumerate(zip(faces, faces_scores)):
            fr = face['rectangle']

            # retrieve names of matched personas
            found_names = names_by_ids([pair[1] for pair in ranked_scored])
            all_found_names.append(found_names)

            proposed_name = found_names[0] if len(ranked_scored) and ranked_scored[0][0] >= MATCH_THR else random_name()
            proposed_names.append(proposed_name)
            proposed_name_s = '{} {}'.format(*proposed_name)

            # Create a Rectangle patch
            rect = patches.Rectangle((fr['left'], fr['top']), fr['right'] - fr['left'], fr['bottom'] - fr['top'], linewidth=2, edgecolor='lightgreen', facecolor='none')

            # Add the patch to the Axes
            ax.add_patch(rect)
            plt.text(fr['left'], fr['bottom'], '[{}] {}'.format(fid + 1, proposed_name_s),
                 va='top',
                 #weight='bold',
                 family='monospace',
                 color='w', bbox=dict(facecolor='black', alpha=0.5), size='small') # Valid font size are xx-small, x-small, small, medium, large, x-large, xx-large, larger, smaller, None

        plt.tight_layout()
        plt.show(block=False)

        # query user for confirmation
        for fid, (face, ranked_scored) in enumerate(zip(faces, faces_scores)):
            print('>>> Face [{}]'.format(fid + 1))

            fr = face['rectangle']

            if len(ranked_scored) and ranked_scored[0][0] >= MATCH_THR:
                print('... Face matched to <{}> with confidence score {:.1f}%'.format('{} {}'.format(*all_found_names[fid][0]), ranked_scored[0][0] * 100))
                print('... Please confirm either by typing number of a known persona or 0 to create new `NoName` persona')

                N = None
                for id, (name_t, (score, _)) in enumerate(zip(all_found_names[fid], ranked_scored)):
                    if score < MATCH_THR:
                        break
                    print('{}. {} {}, {:.1f}%'.format(id + 1, *name_t, score * 100))
                    N = id + 1

                print('{}. create `NoName` persona'.format(N + 1))
                print('0. skip detected face')
                while True:
                    try:
                        val = int(input('??? '))
                    except Exception as e:
                        continue
                    if 0 <= int(val) <= N + 1:
                        break

                if val == N + 1:
                    if DRYRUN:
                        persona_id = None
                    else:
                        cutout_as_bytes = crop_around_the_face(image, fr)
                        cutout_id = save_image_as_bytes(cutout_as_bytes)
                        persona_id = save_persona(*random_name(), 'Persona from image {} <{}>'.format(image_id, infile.name), cutout_id)
                elif val == 0:
                    persona_id = None
                    print('Skipped')
                elif val <= N:
                    persona_id = ranked_scored[val - 1][1]
                    #print('Selected persona_id {} for {}'.format(persona_id, all_found_names[fid][val - 1]))

            else:
                print('... No matched persona was found.', end='')
                if len(ranked_scored):
                    print(' The best match was to <{}> with confidence score {:.1f}%'.format('{} {}'.format(*all_found_names[fid][0]), ranked_scored[0][0] * 100))
                else:
                    print()

                if not DRYRUN:
                    print('1. create persona <{} {}>'.format(*proposed_names[fid]))
                    print('0. skip detected face')

                    while True:
                        try:
                            val = int(input('??? '))
                        except Exception as e:
                            continue
                        if 0 <= int(val) <= 1:
                            break

                    if val == 1:
                        cutout_as_bytes = crop_around_the_face(image, fr)
                        cutout_id = save_image_as_bytes(cutout_as_bytes)
                        persona_id = save_persona(*proposed_names[fid], 'Persona from image {} <{}>'.format(image_id, infile.name), cutout_id)
                    else:
                        persona_id = None
                        print('Skipped')
                else:
                    persona_id = None

            if persona_id is not None:
                DRYRUN or maybe_save_face(fr['uuid'], image_id, top=fr['top'], bottom=fr['bottom'], left=fr['left'], right=fr['right'], embedding=fr['embedding'])
                DRYRUN or save_avatar(persona_id, fr['uuid'])

        input('Press any key')
        plt.close()

    return
