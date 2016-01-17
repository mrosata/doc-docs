import os
import unittest
import tempfile
import pprint
from contextlib import contextmanager
from flask import appcontext_pushed

os.environ.__setitem__('FLASK_CONFIGURATION', 'testing')
from run_interactive import delete_all

import flask
import flask_security
import flask_sqlalchemy
from doc_docs import app, db, models, utils, security, security_forms, \
    security_utils, current_user


class TestingSetupAndTearDown(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        pass


class TestUserLoginLogoff(TestingSetupAndTearDown, unittest.TestCase):
    username = "mike@mike.com"
    password = "password"

    def login(self, username, password):
        ctx = self._ctx or self.app
        return ctx.post(app.config['SECURITY_LOGIN_URL'],
                        data=dict(
                              cfrf_token="",
                              email=username,
                              password=password,
                              submit="Login",
                              next=""
                        ),
                        follow_redirects=True,
                        content_type='application/x-www-form-urlencoded')

    def logout(self):
        ctx = self._ctx or self.app
        return ctx.post('/logout', follow_redirects=True)

    def test_user_login_and_logoff(self):
        """
        First load home page, check that the user is Anonymous by checking for
        an id which will throw an AttributeError. Then login and check that
        the current_user.email is the same as the email used to login with.
        Then make a get request to logoff and check that once more we have
        no id on the current user. In testing cfrf_token is not required.

        :return:
        """
        # User should not be logged in

        with self.app as ctx:
            self._ctx = ctx

            ctx.get('/')
            self.assertNotEquals(current_user, None,
                                 "current_user not None after request")
            # AnonymousUser doesn't have an id attribute
            self.assertRaises(AttributeError, lambda fn: current_user.id,
                              "current_user equal to None after logout")
            self.login("mike@mike.com", "password")
            self.assertTrue(current_user.email == "mike@mike.com",
                            "current_user.email should be the same as the "
                            "email used for login \"mike@mike.com\"")
            ctx.get("/logout", follow_redirects=True)

            # logged off current_user shouldn't have an id as an AnonymousUser
            self.assertRaises(AttributeError, lambda fn: current_user.id,
                              "current_user equal to None after logout")


class TestingUserProfile(TestingSetupAndTearDown, unittest.TestCase):
    pass


class TestingDocDoc(TestingSetupAndTearDown, unittest.TestCase):
    pass


class TestingDocReview(TestingSetupAndTearDown, unittest.TestCase):
    pass


class TestingDocRating(TestingSetupAndTearDown, unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
