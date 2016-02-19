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
from doc_docs import db, login_session, utils
from doc_docs.sql.models import User


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
        return get_user_from_email(user_info.get('email'))

    except NoResultFound, e:
        utils.log("WE HAVE UNO PROBLEMA %r", e)
        return None


def get_user_from_email(email):
    """
    Try to lookup a user by email, return id or None.
    :param email:
    :return:
    """
    return db.session.query(User).filter_by(email=email).one()

