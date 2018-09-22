
################################################################################
################################################################################


import flask as F

app = F.Flask(__name__)
app.config['SECRET_KEY'] = 'SpektorSecretKey'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['DEBUG'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_BINDS'] = {
  'personas':   'sqlite:///db/personas.db',
  'images':     'sqlite:///db/images.db',
  'faces':     'sqlite:///db/faces.db',
  'avatars':     'sqlite:///db/avatars.db',
}


import flask_sqlalchemy

db = flask_sqlalchemy.SQLAlchemy(app)


import flask_restless

class Persona(db.Model):
    __bind_key__ = 'personas'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Unicode)
    last_name = db.Column(db.Unicode)
    notes = db.Column(db.Unicode)
    avatar = db.Column(db.Integer, db.ForeignKey('image.id'))

class Image(db.Model):
    __bind_key__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.LargeBinary)

class Face(db.Model):
    __bind_key__ = 'faces'
    uuid = db.Column(db.String, primary_key=True) # technically, a hash of the embedding
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    top = db.Column(db.Integer)
    bottom = db.Column(db.Integer)
    left = db.Column(db.Integer)
    right = db.Column(db.Integer)
    embedding = db.Column(db.String) # json-ified array of floats

class Avatar(db.Model):
    __bind_key__ = 'avatars'
    id = db.Column(db.Integer, primary_key=True)
    persona_id = db.Column(db.Integer, db.ForeignKey('persona.id'))
    face_id = db.Column(db.Integer, db.ForeignKey('face.uuid'))


# Create the database tables. Has to be after models defined above.
db.create_all()


# Create the Flask-Restless API manager.
manager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)

# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.
manager.create_api(Persona, methods=['GET', 'POST', 'DELETE'])

import pp_image
manager.create_api(Image, methods=['GET', 'POST', 'DELETE'],
                   postprocessors=pp_image.postprocessors,
                   preprocessors=pp_image.preprocessors)
manager.create_api(Face, methods=['GET', 'POST', 'DELETE'])
manager.create_api(Avatar, methods=['GET', 'POST', 'DELETE'])

from flask_admin import Admin
from flask_admin import form as fa_form
from flask_admin.contrib.sqla import ModelView

admin = Admin(app, name='SPEKTOR', template_mode='bootstrap3')
admin.add_view(ModelView(Persona, db.session))
#admin.add_view(ModelView(Image, db.session))
class ImageView(ModelView):
    def _list_thumbnail(view, context, model, name):
        if not model.image:
            return ''

        import base64, jinja2
        return jinja2.Markup('<img src="data:;base64,{}">'.format(base64.b64encode(model.image).decode('utf8')))

        return Markup(
            '<img src="%s">' %
            url_for('static',
                    filename=form.thumbgen_filename(model.path))
        )

    def image_validation(form, field):
        if len(field.data.filename) == 0:
            raise ValidationError('None file selected')
        import imghdr
        if imghdr.what(field.data) != 'jpeg':
            raise ValidationError('file must be a valid jpeg image.')
        field.data = field.data.stream.read()
        return 'lalala'

    column_formatters = dict(image=_list_thumbnail)
    #form_extra_fields = dict(image=fa_form.ImageUploadField('Image', base_path='.', thumbnail_size=(100, 100, True)))
    form_overrides = dict(image=fa_form.FileUploadField)
    form_args = dict(image=dict(validators=[image_validation]))
    can_edit = False
    can_create = False

admin.add_view(ImageView(Image, db.session))
admin.add_view(ModelView(Face, db.session))
admin.add_view(ModelView(Avatar, db.session))



################################################################################
################################################################################


def initialize_logging(app, DEBUG):
    from logging.config import dictConfig
    dictConfig({
        'version': 1,
        'root':
        {
            'level': 'DEBUG' if DEBUG else 'INFO',
        },
    })

    import logging
    formatter = logging.Formatter('%(asctime)s.%(msecs)03d:%(levelname)s:%(name)s:%(message)s', datefmt='%Y-%m-%dT%H:%M:%S')
    app.logger.handlers[0].setFormatter(formatter)

    return


def work(HOST, PORT):
    initialize_logging(app, True)

    app.logger.info('Starting app')

    """
    Having an option to pass an IP address which will be used by Flask
    will enable both being able to run the app locally and in a container.
    """
    app.logger.info('App ready!')

    app.run(host=HOST, port=PORT)

    return