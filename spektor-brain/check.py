#!/usr/bin/python3

def main(url='http://localhost:5000/spektor/detect', fname='Obama1.jpg'):

    import requests
    import json

    rv = requests.post(url, files=dict(file=open(fname, 'rb')))
    assert(rv.status_code == 200)
    js = json.loads(rv.text)
    if js['success'] == False:
        print(js)
        assert(js['success'])
    rv = js['result']

    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    from PIL import Image

    image = Image.open(fname)
    fig, ax = plt.subplots(1)

    # Display the image
    ax.imshow(image)

    for face in rv['faces']:

        fr = face['rectangle']
        if fr['confidence'] < -0.4:
            continue
        print({fr['uuid']: fr['embedding']})

        # Create a Rectangle patch
        rect = patches.Rectangle((fr['left'], fr['top']), fr['right'] - fr['left'], fr['bottom'] - fr['top'], linewidth=2, edgecolor='lightgreen', facecolor='none')

        # Add the patch to the Axes
        ax.add_patch(rect)

    plt.tight_layout()
    plt.show()
    #fig.savefig('out.png')


if __name__ == '__main__':
    import sys
    kwargs = {}
    if len(sys.argv) == 2:
        kwargs['fname'] = sys.argv[1]
    main(**kwargs)
