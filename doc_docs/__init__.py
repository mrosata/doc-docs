"""
Doc Docs >> 2015 - 2016
    by: Michael Rosata <<
"""
# Third party imports.
from flask import Flask, render_template
from flask_security import current_user, SQLAlchemyUserDatastore, Security


# DocDocs utiliies (mainly path resolution).
from doc_docs.utilities import utils
# This holds the public facing url routes and templates.
from doc_docs.public.url_routes import public
from doc_docs.config import configure_app
from doc_docs.sql import db, User, Role, UserProfile, UserBioText

import pprint
# Create the app, this will be the main object which runs this entire application.
app = Flask(__name__, instance_path=utils.get_instance_folder_path(), instance_relative_config=True
            , template_folder='templates')

# Load BaseConfig then overwrite with custom configs (dev, file, server, ect).
configure_app(app)
# SQLAlchemy().init_app()
db.init_app(app)
# Jinja2 Documentation says to load loopcontrols or some of the templates built won't run proper.
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.register_blueprint(public)

# This is to init Flask Security user and roles
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


@app.before_first_request
def create_user_one():
    db.create_all()
    # user_datastore.delete_user('mike@mike.com')
    user_datastore.find_or_create_role(name="member", description="Typical Member")
    # user_datastore.create_role(name="member", description="Typical Member")
    _main_user = user_datastore.find_user(email="mike@mike.com")
    if _main_user is None:
        user_datastore.create_user(email="mike@mike.com", username="mrosata", password="password")
        user_datastore.add_role_to_user("mike@mike.com", 'member')

    db.session.commit()


# We should try to handle some errors
# ( 500 )
@app.errorhandler(500)
def errors_and_stuff(error=None):
    if error is not None:
        print error
    return '500'


# ( 404 )
@app.errorhandler(404)
def errors_and_stuff(error=None):
    if error is not None:
        print error
    return '404'

