"""
Doc Docs >> 2015 - 2016
    by: Michael Rosata << doc_doc/public/creator/creator.py

------
Creator will assist in creating things like doc_docs by combining logic from database models and from site forms
"""
from sqlalchemy import and_
from .doc_scraper import fetch_meta
from doc_docs.sql import models
from doc_docs.public.site_forms import ReviewForm
from doc_docs.utilities import utils
from doc_docs import db, current_user, PreviousReviewException


class Creator:
    """
    _data is a list of attributes this object (or child) will accept and data is where the values are populated
    after being pushed in by push(). They are really methods meant to be implemented on child classes
    """
    _data = tuple()
    data = dict()
    doc = None

    def __init__(self):
        self.session = db.session
        pass

    def return_or_create_doc(self, doc_url):
        parsed_url = utils.get_url_parts(doc_url)
        doc = None
        if self.session.query(models.DocDoc).all().count > 0:
            doc = self.session.query(models.DocDoc).\
                filter(models.DocDoc.full_url == parsed_url['full_url']).\
                filter(models.DocDoc.base_url == parsed_url['base_url']).\
                filter(models.DocDoc.pathname == parsed_url['pathname']).\
                filter(models.DocDoc.fragment == parsed_url['fragment']).first()

        if doc is None:
            # Create the og_meta and the doc
            og_meta = fetch_meta(doc_url)
            doc = models.DocDoc(doc_url, current_user, None, og_meta)

        self.doc = doc
        return doc

    def push(self, **kwargs):
        """
        Each creator object can list kwargs that it will accept and they can be arbitrarily pushed to it.
        :param kwargs:
        :return:
        """
        for key in kwargs:
            if key in self._data:
                self.data[key] = kwargs[key]


class DocRatingCreator(Creator):

    @staticmethod
    def rate(doc_doc, user, rating):
        """
        Pass in a DocDoc, User and rating to set it in the database. It's really just a buffer between the
        model.DocRating object and potentially could depracate in near future. Depends on usefulness.
        :param doc_doc:
        :param user:
        :param rating:
        :return:
        """
        if not (isinstance(doc_doc, models.DocDoc) or isinstance(user, models.User)):
            utils.log("INSTANCE TROUBLE IN DocRatingCreator %r", doc_doc)
            utils.log("INSTANCE TROUBLE IN DocRatingCreator %r", user)

        doc_id = doc_doc.doc_id
        user_id = user.id
        rating = rating

        the_rating = models.DocRating(doc_id, user_id, rating)
        return the_rating


class DocReviewCreator(Creator):

    _data = ('summary', 'review', 'rating', 'discoverer', 'tags')
    form = ReviewForm
    model = models.DocReview
    _tag_count = 0
    tags = list()
    doc = None

    def __init__(self, user):
        self.user = user
        Creator.__init__(self)

    def create(self):

        if self.doc is None:
            return False

        # Check for all the required fields before moving on.
        for x in self._data:
            if x not in self.data:
                return False

        previous_review = self.session.query(models.DocReview).\
            filter_by(doc_id=self.doc.doc_id).\
            filter_by(reviewer=self.user.id).\
            first()

        # A Reviewer may only review an article/document 1 time.
        if previous_review is not None:
            raise PreviousReviewException()

        self.doc = models.DocReview(self.doc.doc_id, self.user, self.data["review"], self.data["summary"])

        if self.doc is None:
            return None

        self.update_terms()
        if self.data["rating"]:
            DocRatingCreator().rate(self.doc, self.user, int(self.data["rating"]))

        return self.doc

    def _attach_tag(self, tag):
        """
        Check if a tag already exists and then attach it to the doc_review in the db (if not exists then create it).
        :param tag:
        :return:
        """
        session = self.session
        if self._tag_count > 5 or self.doc is None:
            return False
        tag = str(tag.strip())
        # Get or create a new term
        term = session.query(models.DocTerm).filter_by(term=tag).first()
        if term is None:
            term = models.DocTerm(tag)

        # Create the relationship between the tag and this review
        term_rel = models.DocTermRelationship(term.term_id, self.doc.doc_review_id)

        # Keep track of tag count in order to enforce set limits
        self._tag_count += 1

    def update_terms(self):
        if self.data["tags"] is not None:
            _tags = str(self.data["tags"]).split(",")
            # We only allow a max of 5 tags per doc TODO: Abstract that value to a config setting might be better.
            for _tag in _tags:
                self._attach_tag(_tag)
