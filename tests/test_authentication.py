import unittest

from flask import url_for

from common_testing_code import TestingAppCommonFunctionality
from doc_docs import current_user


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


class TestingDocRating(TestingAppCommonFunctionality, unittest.TestCase):
    pass


class TestsWithSeleniumUI(TestingAppCommonFunctionality, unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
