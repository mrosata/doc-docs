import os
import unittest
import tempfile
import pprint
from contextlib import contextmanager
from flask import appcontext_pushed, url_for

os.environ.__setitem__('FLASK_CONFIGURATION', 'testing')
from run_interactive import delete_all

import flask
import flask_security
import flask_sqlalchemy
from doc_docs import app, db, models, utils, security, security_forms, \
    security_utils, current_user


class TestingAppCommonFunctionality(unittest.TestCase):
    _ctx = None

    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        pass

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


class TestUserLoginLogoff(TestingAppCommonFunctionality, unittest.TestCase):
    username = "mike@mike.com"
    password = "password"

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


class TestingUserProfile(TestingAppCommonFunctionality, unittest.TestCase):

    def test_new_user_profile_is_empty(self):
        pass


class TestingDocDoc(TestingAppCommonFunctionality, unittest.TestCase):

    def test_create_new_doc_doc(self):
        """Create a new doc doc and check that it is in the database"""
        with self.app as ctx:
            self._ctx = ctx

            ctx.get('/')
            self.login("mike@mike.com", "password")
            ctx.get(url_for('public.add_new'))
            self.assertTrue(current_user.email == "mike@mike.com",
                            "current_user.email should be the same as the "
                            "email used for login \"mike@mike.com\"")
            ctx.get("/logout", follow_redirects=True)

            # logged off current_user shouldn't have an id as an AnonymousUser
            self.assertRaises(AttributeError, lambda fn: current_user.id,
                              "current_user equal to None after logout")

    def test_delete_doc_doc(self):
        pass


class TestingDocReview(TestingAppCommonFunctionality, unittest.TestCase):

    doc_review_data = dict(
        csrf_token="",
        doc_url="https://userbase.kde.org/Plasma/Krunner",
        rating="8",
        review="This was an informative piece of documentation. It helpe"
               "d me not only to understand more about Krunner but to un"
               "derstand more about myself. Who am I? Where did I come f"
               "rom? Where am I going and when will I get there? These a"
               "re all questions that we as human beings tend to ask our"
               "selves. Many of us will never get any answers. But I hop"
               "e, and I think that I speak for the documentators of Kru"
               "nner, that through good operating systems and through op"
               "en source software we will find the answer to these ques"
               "tions. For what am I without a machine if I am not a mac"
               "hine myself? My thoughts are input, stimuli from the wor"
               "ld is input from a network. The electrical pulses which "
               "move my limbs aren't they but drivers to my hardware? Wh"
               "en I do 2 things at once, is my OS not managing system p"
               "rocess? Do we not share similiar hardware and implementa"
               "tion? We do, we are machine, and we are all opensource. "
               "Thank you and goodnight citizens of Boop-Bop County.",
        summary="I never actually read anything on this page. I'm just a"
                " very good judge of quality. An thus I review!",
        detour="",
        tags="os, linux, arch linux, desktop"
    )

    def test_1_doc_review_not_yet_created(self):
        """Make sure that there are no Doc Reviews by the test user before
        running any real tests."""
        # ??? We first need to log into the system to make a post
        with self.app as ctx:
            self._ctx = ctx
            ctx.post('/')
            self.login("mike@mike.com", "password")
            user = db.session.query(models.User).\
                filter_by(email="mike@mike.com").first()
            assert user is not None
            rc = db.session.query(models.DocReview).\
                filter_by(reviewer=current_user.id).count()
            self.assertEquals(rc, 0, "Should be no reviews by user yet")

    def test_2_create_new_doc_review(self):
        """Create a new doc doc and check that it is in the database"""
        pass
        with self.app as ctx:
            self._ctx = ctx

            # Check if a review was made by this user
            rv = ctx.get(url_for('public.add_new'))
            ctx.post(url_for('public.add_new'), data=self.doc_review_data,
                     content_type="application/x-www-form-urlencoded",
                     follow_redirects=True,
                     referer=url_for('public.add_new'))
            pprint.pprint(rv.data)
            self.assertTrue(
                  current_user.email == "mike@mike.com",
                  "Current user doesn't have the correct email property")


class TestingDocRating(TestingAppCommonFunctionality, unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
