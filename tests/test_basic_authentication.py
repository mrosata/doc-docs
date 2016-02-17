import os
import unittest
import tempfile
import pprint
from contextlib import contextmanager
from flask import appcontext_pushed, url_for

os.environ['FLASK_CONFIGURATION'] = 'testing'

from doc_docs import app, db, models, current_user


# Before starting any of the tests the database should be empty
db.session.query(models.DocDoc).delete()
db.session.query(models.User).delete()
db.session.query(models.UserProfile).delete()
db.session.query(models.UserBioText).delete()
db.session.query(models.UserBioText).delete()
db.session.query(models.Role).delete()
db.session.query(models.DocRating).delete()
db.session.query(models.DocReview).delete()
db.session.query(models.DocReviewBody).delete()
db.session.query(models.DocTerm).delete()
db.session.query(models.DocDetour).delete()
db.session.query(models.DocSiteMeta).delete()
db.session.query(models.CommunityApproval).delete()
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
        review="This was an informative piece of documentation. It helped me not only to "
               "understand more about Krunner but to understand more about myself. Who am "
               "I. Where did I come from? Where am I going and when will I get there? These"
               " are all questions that we as human beings tend to ask ourselves.",
        summary="I never actually read anything on this page. I'm just a very good judge "
                "of quality. An thus I review!",
        detour="",
        tags="os, linux, arch linux, desktop"
    )

    def test_1_doc_review_not_yet_created(self):
        """Make sure that there are no Doc Reviews by the test user before
        running any real tests."""
        # ??? We first need to log into the system to make a post
        with self.app as ctx:
            self._ctx = ctx
            ctx.get('/')
            self.login("mike@mike.com", "password")
            user = db.session.query(models.User).\
                filter_by(email="mike@mike.com").first()
            assert user is not None
            rc = db.session.query(models.DocReview).\
                filter_by(reviewer=current_user.id).count()
            self.assertEquals(rc, 0, "Should be no reviews by user yet")

    def test_2_create_new_doc_review(self):
        """Create a new doc doc and check that it is in the database, first
        the function needs to login a user and then create the doc_review"""
        with self.app as ctx:
            self._ctx = ctx
            ctx.get('/')

            self.login("mike@mike.com", "password")
            # Check if a review was made by this user
            ctx.post(url_for('public.add_new'), data=self.doc_review_data,
                     content_type="application/x-www-form-urlencoded",
                     follow_redirects=True)
            rc = db.session.query(models.DocReview). \
                filter_by(reviewer=current_user.id).count()
            self.assertEquals(rc, 1, "Should be 1 review by user now")

    def test_3_edit_created_doc_review(self):
        """Should be able to edit a doc review after it has been posted up"""
        with self.app as ctx:
            self._ctx = ctx
            ctx.get('/')

            self.login("mike@mike.com", "password")
            # Get the review which we just created then goto url_for(public.edit_review)
            review = db.session.query(models.DocReview).\
                filter_by(reviewer=current_user.id).one()

            review_page = ctx.get(url_for('public.edit_review', review_id=review.doc_review_id))
            assert(review_page.status_code == 200,
                   "Requesting public.edit_review should return status 200")
            assert('<form action="/review/edit/1"' in review_page.data,
                   "There should be an edit <form> in the html to edit review in review_page.data")


class TestingDocRating(TestingAppCommonFunctionality, unittest.TestCase):
    pass


class TestsWithSeleniumUI(TestingAppCommonFunctionality, unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
