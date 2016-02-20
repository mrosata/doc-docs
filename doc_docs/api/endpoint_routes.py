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
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from flask_security import utils as security_utils

from doc_docs import login_session
from doc_docs.public.security_forms import ExtendedRegistrationForm
from doc_docs.public.creator import DocReviewCreator
from doc_docs.utilities import utils
from doc_docs import db, app, resources

from oauth_helpers import fb_login, google_login

# Register the API Blueprint
api = Blueprint('api', __name__)


@api.route('/api/login', methods=['POST'])
def api_login():
    # Assume that the attempt will fail
    status = 'failure'
    user = None
    resp_data = dict()
    message = str()
    access_token = request.json.get('access_token')
    # FB Specific
    action = request.json.get('action')
    # Google Specific
    code = request.json.get('code')

    utils.log("THIS IS THE REQUEST::: %r", request.json)
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
        utils.log("THIS IS THE CODE::: %r", code)
        # Google OAuth
        try:
            # Upgrade the authorization code
            oauth_flow = flow_from_clientsecrets(resources.client_secrets['google'], scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(code)
            # Override the code sent in access_token from browser with upgraded token
            access_token = credentials.access_token
            client_id = credentials.client_id
            id_token = credentials.id_token
            user = google_login(access_token, client_id, id_token)
            # I was having a problem where trying to store the credentials raised a TypeError even
            # though the data seemed Ok. The problem is solved by setting empty/null values to
            # None by using a default value with lambda/anonymous function
            # http://stackoverflow.com/questions/10872604/json-dump-throwing-typeerror-is-not-json
            # -serializable-on-seemingly-vali
            login_session['credentials'] = json.dumps(credentials, default=lambda x: None)
        except FlowExchangeError:
            resp = make_response(
                  json.dumps('Failed to upgrade the authorization code.'), 401)
            resp.headers['Content-Type'] = 'application/json'
            return resp

    else:
        # We don't know what type of login this request is trying to make.
        status = 'rejected'
        message = 'Missing required API param "type"'

    if user is not None:
        security_utils.login_user(user=user)
        status = 'success'
        message = 'Successful login!'

    resp_data['location'] = url_for('public.index')
    # This will be the content of the response.
    the_json = json.dumps(
          dict(
                action=action,
                status=status,
                message=message,
                data=resp_data
          )
    )

    resp = make_response(the_json)
    resp.headers['Content-type'] = "application/json"
    return resp


