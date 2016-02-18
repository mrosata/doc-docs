import unittest

from flask import url_for

from common_testing_code import TestingAppCommonFunctionality
from doc_docs import db, models, current_user


class TestingDocReview(TestingAppCommonFunctionality, unittest.TestCase):

    doc_review_data = dict(
          original=dict(
                csrf_token="",
                doc_url="https://userbase.kde.org/Plasma/Krunner",
                rating="8",
                review="original review text",
                summary="original summary text",
                detour="",
                tags="os, linux, arch linux, desktop"
          ),
          edit_one=dict(
                csrf_token="",
                doc_url="https://userbase.kde.org/Plasma/Krunner",
                rating="7",
                review="Edit on review 1.",
                summary="Edit on summary 1",
                detour="",
                tags="os, linux"
          ),
          edit_two=dict()
    )

    def test_1_doc_review_not_yet_created(self):
        """Make sure that there are no Doc Reviews by the test user before
        running any real tests."""
        # ??? We first need to log into the system to make a post.
        with self.app as ctx:
            self._ctx = ctx
            ctx.get('/')
            self.login("mike@mike.com", "password")
            user = db.session.query(models.User). \
                filter_by(email="mike@mike.com").first()
            assert user is not None
            rc = db.session.query(models.DocReview). \
                filter_by(reviewer=current_user.id).count()
            self.assertEquals(rc, 0, "Should be no reviews by user yet")

    def test_2_create_new_doc_review(self):
        """Create a new doc doc and check that it is in the database, first
        the function needs to login a user and then create the doc_review"""
        with self.app as ctx:
            self._ctx = ctx
            ctx.get('/')

            self.login("mike@mike.com", "password")
            # Check if a review was made by this user.
            ctx.post(url_for('public.add_new'), data=self.doc_review_data['original'],
                     content_type="application/x-www-form-urlencoded",
                     follow_redirects=True)
            rc = models.DocReview.query.filter_by(reviewer=current_user.id).count()
            self.assertEquals(rc, 1, "Should be 1 review by user now")

    def test_3_edit_created_doc_review(self):
        """Should be able to edit a doc review after it has been posted up"""
        with self.app as ctx:
            self._ctx = ctx
            ctx.get('/')

            self.login("mike@mike.com", "password")
            # Get the review which we just created then goto url_for(public.edit_review).
            review = models.DocReview.query.filter_by(reviewer=current_user.id).one()

            review_page = ctx.get(url_for('public.edit_review', review_id=review.doc_review_id))
            assert review_page.status_code == 200, \
                "Requesting public.edit_review should return status 200"
            assert '<form action="/review/edit/1"' in review_page.data, \
                "There should be an edit <form> in the html to edit review in review_page.data"

            # Make sure that all the review data is different from what the edit will create.
            for d in ('summary', 'review', 'tags'):
                assert self.doc_review_data['edit_one'][d] != review.get_form_data(d), \
                    "Before testing review edit, the %s to edit must be different".format(d)

            # Send the Edit through POST request
            ctx.post(
                  url_for('public.edit_review', review_id=review.doc_review_id),
                  data=self.doc_review_data['edit_one'], follow_redirects=True,
                  content_type="application/x-www-form-urlencoded")

            # Get the review which we just edited, now it matches doc_review_data['edit_one'].
            review = db.session.query(models.DocReview). \
                filter_by(reviewer=current_user.id).one()

            # Make sure that the edit worked.
            for d in ('summary', 'review', 'tags'):
                assert self.doc_review_data['edit_one'][d] == review.get_form_data(d), \
                       "After editing review, the review {} should be the same".format(d)




