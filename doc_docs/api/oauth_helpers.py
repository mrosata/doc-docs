"""
doc_docs.api.oauth2_helpers

The functions in this file abstract some of the OAuth2 work. It's just to keep clean the
endpoint_routes.py file mainly.
"""
import httplib2
import requests

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from sqlalchemy.orm.exc import NoResultFound
from flask import json, make_response
from flask_security import SQLAlchemyUserDatastore
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

from doc_docs import db, login_session, utils
from doc_docs.sql.models import User, Role
from doc_docs.public import creator


user_datastore = SQLAlchemyUserDatastore(db, User, Role)


def fb_graph(token):
    url = 'https://graph.facebook.com/v2.2/me?fields=id,name,email&%s' % token

    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    rv = json.loads(result)

    # Store our user into the login session
    login_session['username'] = rv.get('name')
    login_session['email'] = rv.get('email')
    login_session['facebook_id'] = rv.get('id')

    return rv


def gplus_info(access_token):
    """
    Get profile information for the user which this access_token belongs to.
    :param access_token:
    :return:
    """
    url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    result = requests.get(url, params=params)
    rv = json.loads(result.text)

    # Store our user into the login session (note: we already have gplus_id)
    login_session['username'] = rv.get('name')
    login_session['email'] = rv.get('email')
    login_session['picture'] = rv.get('picture')

    return rv


def fb_login(app_id, secret, access_token):
    """

    :param app_id:
    :param secret:
    :param access_token:
    :return:
    """
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token' \
          '&client_id={0}&client_secret={1}&fb_exchange_token={2}'
    url = url.format(app_id, secret, access_token)

    try:
        h = httplib2.Http()
        result = h.request(url, 'GET')[1]
        token = result.split('&')[0]

        # Error will raise if the user doesn't exist
        user_info = fb_graph(token)
        return find_or_create_user(user_info.get('email'), user_info.get('name'), 'facebook')

    except NoResultFound, e:
        utils.log("WE HAVE UNO PROBLEMA %r", e)
        return None


def google_login(access_token, client_id, id_token):
    # /identity/sign-in/web/backend-auth
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %
           access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there is error in the access token info, abort.
    if result.get('error') is not None:
        # 500
        raise Exception(result.get('error'))

    # Verify that the access token is for the current user
    gplus_id = id_token['sub']
    if result['user_id'] != gplus_id:
        # 401
        raise Exception("Token's user ID doesn't match current user ID")

    # also verify my apps token
    if result['issued_to'] != client_id:
        # 401
        raise Exception("Token's client ID doesn't match current app")

    # Check if user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        # 200
        raise Warning("The User is already logged in")

    # Since we are good, we want to hold credentials in persistent dict.
    login_session['gplus_id'] = gplus_id

    user_info = gplus_info(access_token)
    return find_or_create_user(user_info.get('email'), user_info.get('name'), 'google')


def github_login(step1_code, client_secret, client_id):
    """
    Return a user by upgrading the code returned from GitHub step 1 OAuth and getting the
    users email. If there is no user matching the email then create a new user.

    :param step1_code:
    :param client_secret:
    :param client_id:
    :return:
    """
    url = 'https://github.com/login/oauth/access_token'
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": step1_code
    }

    try:
        req = requests.post(url, data, headers=dict(accept="application/json"))
        result = req.json()

        if result.get('error') is not None:
            # 500
            raise Exception("Github Error: {}".format(result.get('error_description')))

        access_token = result.get('access_token')
        scope = result.get('scope')

        if "user:email" not in scope:
            # 403
            raise Exception("Github Error: Require scope user:email in order to complete OAuth2")

        # Now if we have the token we can get back the email
        url = "https://api.github.com/user?access_token={}".format(access_token)
        req = requests.get(url)
        result = req.json()
        utils.log("HERE IS THE USER INFORMATION:::: %r ", result)
        email = result.get('email')
        full_name = result.get('name')
        login = result.get('login')
        if login is None:
            login = email
        if email is None:
            raise ValueError
    except ValueError, KeyError:
        # There was a problem with the request.. probably not a 200
        raise Exception("Github Error: Did not recieve a valid response from Github.")

    user = find_or_create_user(email, full_name, username=login)

    return user


def find_or_create_user(email, full_name='', provider='', provider_id='', username=''):
    """
    Return a User based on their email address. If the User doesn't exist then create
    a user using the user_datastore and UserProfileCreator, then return that User.

    :param provider_id:
    :param provider:
    :param full_name:
    :param email:
    :return:
    """
    user = user_datastore.find_user(email=email)
    if user is None:
        # Create the user and start their profile since they don't exist yet.
        provider = str(provider).lower()
        # DocDocs doesn't require unique username, but we do need a username.
        if username is None or username == "":
            if full_name is None or full_name == "":
                username = str(email).split('@')[0]
            username = full_name

        user = user_datastore.create_user(email=email, username=username)
        role = user_datastore.find_role('member')
        user_datastore.add_role_to_user(user, role)
        profile = creator.UserProfileCreator(user=user)
        if full_name != '':
            profile.full_name(full_name)

        if provider == 'facebook':
            profile.facebook = provider_id
        elif provider == 'google':
            profile.google = provider_id
        elif provider == 'github':
            profile.github = provider_id

        profile.create()

    return user

