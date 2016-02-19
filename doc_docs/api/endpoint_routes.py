"""
Doc Docs >> 2015 - 2016
    by: Michael Rosata <<

API Endpoint Routes
-----------------
API endpoints return JSON. Some API calls include logging on with JavaScript through OAuth2, adding
DocReviews through Ajax, ect..
"""
from random import choice
from string import ascii_letters, digits

from flask import Blueprint, request, make_response, url_for, json
from flask_security import current_user, login_required, logout_user, forms

from doc_docs import login_session, security_utils
from doc_docs.public.security_forms import ExtendedRegistrationForm
from doc_docs.public.creator import DocReviewCreator
from doc_docs.utilities import utils
from doc_docs import db, app, resources

from oauth_helpers import fb_login

# Register the API Blueprint
api = Blueprint('api', __name__)


@api.route('/api/login', methods=['POST'])
def api_login():
    # Assume that the attempt will fail
    status = 'failure'
    data = dict()
    message = str()
    action = request.json.get('action')
    access_token = request.json.get('access_token')
    utils.log("ACCESSSS TOKEN!!!:::: %r", access_token)

    # Ensure that the App State has been perserved or else we can't trust request
    if request.json.get('_state') != login_session['STATE']:
        status = 'rejected'
        message = 'Session state is not in sync with server!'

    # Setup and make OAuth request based on service type (fb, google)
    if request.json.get('type') == 'fb':
        # Facebook OAuth
        secrets = json.load(open(resources.client_secrets['fb'], 'r'))
        app_secret = secrets['web']['app_secret']
        app_id = secrets['web']['app_id']
        user = fb_login(app_id, app_secret, access_token)
    elif request.json.get('type') == 'google':
        # Google OAuth
        secrets = json.load(open(resources.client_secrets['google'], 'r'))
        user = None
    else:
        user = None
        status = 'rejected'
        message = 'Missing required API param "type"'

    if user is not None:
        security_utils.login_user(user=user)
        status = 'success'
        message = 'Successful login!'

    data['location'] = url_for('public.index')

    # This will be the content of the response
    the_json = json.dumps(
          dict(
                action=action,
                status=status,
                message=message,
                data=data
          )
    )

    resp = make_response(the_json)
    resp.headers['Content-type'] = "application/json"
    return resp
