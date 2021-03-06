"""
Doc Docs >> 2015 - 2016
    by: Michael Rosata << doc_docs.__init__.py

This is the main access point for everything in the app. This file isn't run
to start the app though. The run.py in the root folder is used to access the
application.
"""
# System modules
import pprint
from random import choice
from string import digits, ascii_letters

# Third party imports.
from flask import Flask, render_template, request, flash, g
from flask_security import SQLAlchemyUserDatastore, Security, current_user, \
    user_registered
from flask.ext.login import user_logged_out

from flask import session as login_session

from flask_mail import Mail
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.principal import identity_changed

from . import resources
from doc_doc_errors import PreviousReviewException, ReviewNotExistException, \
    MissingInformationException, ProfileNotExistsException
from doc_docs.config import configure_app
from doc_docs.utilities import utils

# Create app, the main object which runs this entire application.
app = Flask(__name__, instance_path=utils.get_inst_path(),
            instance_relative_config=True, template_folder='templates')

# Load BaseConfig then overwrite with custom configs (dev, file, server, ect).
configure_app(app)
# SQLAlchemy().init_app()
db = SQLAlchemy(app)
db.init_app(app)
# Public facing url routes and API endpoint blueprints.
from public import url_routes, creator
from api import endpoint_routes

# Jinja2 loopcontrols.
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
# Flask Security Blueprint for all pages created so far.
app.register_blueprint(public.url_routes.public)
app.register_blueprint(api.endpoint_routes.api)

from public import security_forms
from sql import models
from sql.retriever import _q


# Mock Mailing class. This is to satisfy a service which will be implemented.
class MyMail(Mail):
    def send(self, msg):
        return True

mail = MyMail()
mail.init_app(app)

# This is to init Flask Security user and roles
user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
security = Security(app, user_datastore, register_form=security_forms.ExtendedRegistrationForm)


def newly_registered_user(app, user, confirm_token, **extra):
    """
    Anytime a user registers on the site we want to give them a profile (empty) and add
    the Standard User role "member" to their user. This will complete the creation of
    entries in all the user specific tables User, UserProfile, ProfileBioText

    :param app:
    :param user:
    :param confirm_token:
    :param extra:
    :return:
    """
    profile = creator.UserProfileCreator(user)
    profile.create()
    role = user_datastore.find_or_create_role(
          name="member", description="Standard User")
    user_datastore.add_role_to_user(user, role)


def app_state_token():
    """
    Get the App State Token, create the token if it is not already created.
    :return:
    """
    # Check if STATE is not available.
    if 'STATE' not in login_session:
        login_session['STATE'] = "".join(
              choice(ascii_letters.join(digits)) for i in range(32))
    # return STATE
    return login_session['STATE']


@app.before_first_request
def init_app_db():
    # user_datastore.delete_user('mike@mike.com')
    role = user_datastore.find_or_create_role(name="member", description="Typical Member")
    # user_datastore.create_role(name="member", description="Typical Member")
    _main_user = user_datastore.find_user(email="mike@mike.com")
    if _main_user is None:
        _main_user = user_datastore.create_user(
              email="mike@mike.com", username="mrosata", password="password")

        user_datastore.add_role_to_user(_main_user, role)

    app_state_token()
    db.session.commit()


# TODO: function to add class names onto the body based on the template.
@app.context_processor
def check_body_classes():
    # g.user = current_user is for testing ATM
    g.user = current_user or None
    body_classes = ("home",)
    register_form = security_forms.ExtendedRegistrationForm()
    login_form = security_forms.LoginForm()
    app_state = app_state_token()
    return dict(
          body_classes=body_classes,
          register_user_form=register_form,
          login_user_form=login_form,
          app_state=app_state
    )


@identity_changed.connect
def signal_identity_changed_handler(sender, identity):
    """This is the signal flask security fires when a user is logged in. Each request
    made while a user is logged into the app should trigger this signal
    :param sender:
    :param identity:
    :return:
    """
    g.user_id = identity.id or None

    if g.user_id is None:
        g.logged_off = True
        flash("Successfully Logged Out.", category="doc doc system message")
    else:
        g.logged_in = True
        flash("Successfully Logged In.", category="doc doc system message")


@user_logged_out.connect
def user_logged_out_handler(*args, **kwargs):
    """Clear the login_session upon logout"""
    login_session.clear()


# We should try to handle some errors
# ( 500 )
# ( 404 )
@app.errorhandler(500)
@app.errorhandler(404)
def errors_and_stuff(error=None):
    if error is not None:
        print error
    return render_template(resources.error["html"], error_code=404)


# When the user_registered signal is triggered the app should take action
user_registered.connect(newly_registered_user)