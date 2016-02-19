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
from flask import json
from flask_security import SQLAlchemyUserDatastore

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


def find_or_create_user(email, full_name='', provider='', provider_id=''):
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
        user = user_datastore.create_user(email=email)
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

