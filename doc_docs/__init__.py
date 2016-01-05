"""
Doc Docs >> 2015 - 2016
    by: Michael Rosata << doc_docs.__init__.py

---------
This is the main access point for everything in the app. This file isn't run to start the app though.
The run.py in the root folder is used to access the application.
"""
# System modules
import pprint

# Third party imports.
from flask import Flask, render_template, request, redirect, url_for
from flask_security import SQLAlchemyUserDatastore, Security, current_user
from flask_security import utils as security_utils
from flask_mail import Mail
from flask.ext.sqlalchemy import SQLAlchemy

from . import resources
from doc_doc_errors import PreviousReviewException
from doc_docs.config import configure_app
from doc_docs.utilities import utils
# Create the app, this will be the main object which runs this entire application.
app = Flask(__name__, instance_path=utils.get_inst_path(), instance_relative_config=True, template_folder='templates')
# Load BaseConfig then overwrite with custom configs (dev, file, server, ect).
configure_app(app)
# SQLAlchemy().init_app()
db = SQLAlchemy(app)
db.init_app(app)
# This holds the public facing url routes and templates.
from public import url_routes
# Jinja2 Documentation says to load loopcontrols or some of the templates built won't run proper.
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.register_blueprint(public.url_routes.public)

from public import security_forms
from sql import models
from sql.retriever import _q


# Need to setup email. Flask Security seems to try to use mail even if I set all config options against it.
class MyMail(Mail):
    def send(self, msg):
        return True

mail = MyMail()
mail.init_app(app)

# This is to init Flask Security user and roles
user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
security = Security(app, user_datastore, register_form=security_forms.ExtendedRegistrationForm)


@app.before_first_request
def create_user_one():
    # user_datastore.delete_user('mike@mike.com')
    user_datastore.find_or_create_role(name="member", description="Typical Member")
    # user_datastore.create_role(name="member", description="Typical Member")
    _main_user = user_datastore.find_user(email="mike@mike.com")
    if _main_user is None:
        user_datastore.create_user(email="mike@mike.com", username="mrosata", password="password")
        user_datastore.add_role_to_user("mike@mike.com", 'member')

    db.session.commit()


# TODO: I want to create a function to be able to add class names onto the body based on the template. Template done.
@app.context_processor
def check_body_classes():
    body_classes = ("home",)
    register_form = security_forms.ExtendedRegistrationForm()
    login_form = security_forms.LoginForm()
    return dict(body_classes=body_classes, register_user_form=register_form, login_user_form=login_form)


# We should try to handle some errors
# ( 500 )
# ( 404 )
@app.errorhandler(500)
@app.errorhandler(404)
def errors_and_stuff(error=None):
    if error is not None:
        print error
    return render_template(resources.error["html"], error_code=404)



