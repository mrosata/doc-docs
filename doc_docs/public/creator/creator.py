"""
Creator will assist in creating things like doc_docs by combining logic from database models and from site forms
"""
from sqlalchemy import and_
from doc_docs.sql import models
from doc_docs.public.site_forms import ReviewForm
from doc_docs.utilities import utils
from doc_docs import db, current_user


class Creator:
    """
    _data is a list of attributes this object (or child) will accept and data is where the values are populated
    after being pushed in by push(). They are really methods meant to be implemented on child classes
    """
    _data = tuple()
    data = dict()

    def __init__(self):
        self.session = db.session
        pass

    @staticmethod
    def return_or_create_doc(self, doc_url):
        url = utils.get_url_parts(doc_url)
        utils.log('this si URL %r', url)
        doc = None
        if db.session.query(models.DocDoc).all().count > 0:
            doc = db.session.query(models.DocDoc).\
                filter(models.DocDoc.full_url == url['full_url']).\
                filter(models.DocDoc.base_url == url['base_url']).\
                filter(models.DocDoc.pathname == url['pathname']).\
                filter(models.DocDoc.fragment == url['fragment']).first()

        if doc is None:
            doc = models.DocDoc(url, current_user, None)

        self.doc = doc
        return self.doc

    def push(self, **kwargs):
        """
        Each creator object can list kwargs that it will accept and they can be arbitrarily pushed to it.
        :param kwargs:
        :return:
        """
        for key in kwargs:
            if key in self._data:
                self.data[key] = kwargs[key]


class DocReviewCreator(Creator):

    _data = ('summary', 'review', 'rating', 'discoverer')
    form = ReviewForm
    model = models.DocReview

    def __init__(self, user):
        self.user = user
        Creator.__init__(self)

    def create(self):

        if self.doc is None:
            utils.log("Need Doc to create a review")
            return False

        for x in self._data:
            if x not in self.data:
                utils.log("Couldn't find %s in DocReviewCreator", x)
                return False

        models.DocReview(self.doc.doc_id, self.user, self.data["review"], self.data["summary"])
