import os
import unittest

os.environ['FLASK_CONFIGURATION'] = 'testing'
from doc_docs import app, db, models


# Before starting any of the tests the database should be empty
db.drop_all()
db.create_all()
db.session.commit()


class TestingAppCommonFunctionality(unittest.TestCase):
    _ctx = None

    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        """
        Cleanup that has to be done inbetween tests
        :return:
        """
        pass

    def login(self, username, password):
        """Login a user from inside a test."""
        ctx = self._ctx or self.app
        resp = ctx.post(app.config['SECURITY_LOGIN_URL'],
                        data=dict(
                              cfrf_token="",
                              email=username,
                              password=password,
                              submit="Login",
                              next=""
                        ),
                        follow_redirects=True,
                        content_type='application/x-www-form-urlencoded')
        return resp

    def logout(self):
        """Logoff a user from inside one of the tests."""
        ctx = self._ctx or self.app
        return ctx.post('/logout', follow_redirects=True)
