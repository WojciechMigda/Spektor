Docker image
------------

Inspect the ``Dockerfile``. It puts together an ``Openface`` installation, with all dependencies, on an Ubuntu system, along with a REST app.

Change current folder to ``spektor-brain``

Issue:

.. code::

  make docker-build


This will build a docker image ``spektor/brain``. It can take significant time because some dependencies are built from source.


In the meantime, download models listed in file ``urls.txt`` inside ``spektor-brain/src/service/data`` folder. These are pretrained neural networks used by ``Openface`` provided by authors and maintainers of ``Openface`` and ``DLib``.

I encourage to use docker installation instructions from Digital Ocean https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04


After the image is built you can run with with

.. code::

  make docker-run

Issue ``docker logs spektor`` to see if all went well (loading models upon image start takes few seconds).

In the logs you should see something like this:

.. code::

  INFO:spektor:Starting app
  INFO:spektor:Models loading..
  INFO:spektor:Done.
  INFO:spektor:App ready!
  INFO:werkzeug: * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)

The app works on port 5000 and exposes two endpoints. One is simple ``hello``, the other is ``identify`` and is used for finding faces on a JPEG photograph.

Backend
-------

With ``spektor/brain`` running you can start the backend REST app. Change current folder to ``spektor/backend``.

First you need to install required dependencies (see ``requirements.txt``).
To install them issue:

.. code::

  pip3 install -r requirements.txt

Once this this is completed issue:

.. code::

  ./spektor-cli.py

This will launch the second REST app. It will work on port 6900, communicating with the dockerized app and the database (sqlite 3 based).

There are two kinds of enpoints this app exposes. The first group enables interaction with the database. These are setup with ``flask-restless`` and allow creation, modification and deletion of entries in the database. On top of that there is ``flask-admin`` setup, which enables database management through a browser. To see it in action open

.. code::

  http://localhost:6900/admin/

The second group of endpoints is responsible for handling requests to analyze the submitted image and execute matching algorithm.

There are two demonstration command line scripts written in python which allow to track what kind of interactions can be made with the REST endpoints and what the workflow could look like.

First of them, ``add.py``, could be used to populate the database with faces found on new photographs.

Run ``./add.py --help`` to see available help.

What it does is it finds faces in specified photographsm picks the most probable face, analyzes it and adds coresponding data to the database (new persona, with a thumbnail and associated image).

You need to either specify personal data from the command line or to enable interactive mode to enter them using keyboard.

The second script, ``analyze.py``, takes given photographs, finds faces, analyzes them, executes match against profiles in the database and prompts for action.

Face can either be (1) skipped (e.g. falsely detected face), (2) used to create new persona (Joe Doe), or (3) added as another representation of a person's profile in the database (one person can be assigned more than one face to be matched against).
