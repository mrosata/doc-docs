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
        parsed_url = utils.get_url_parts(doc_url)
        doc = None
        if db.session.query(models.DocDoc).all().count > 0:
            doc = db.session.query(models.DocDoc).\
                filter(models.DocDoc.full_url == parsed_url['full_url']).\
                filter(models.DocDoc.base_url == parsed_url['base_url']).\
                filter(models.DocDoc.pathname == parsed_url['pathname']).\
                filter(models.DocDoc.fragment == parsed_url['fragment']).first()

        if doc is None:
            doc = models.DocDoc(doc_url, current_user, None)

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

        for x in self._data:
            if x not in self.data:
                utils.log("Couldn't find %s in DocReviewCreator", x)
                return False

        self.doc = models.DocReview(self.doc.doc_id, self.user, self.data["review"], self.data["summary"])

        if self.doc is None:
            return None

        self.update_terms()

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

        if term_rel is not None:
            utils.log()("CRA CRA ADDED TAG ! %r", term_rel)
        self._tag_count += 1

    def update_terms(self):
        if self.data["tags"] is not None:
            _tags = str(self.data["tags"]).split(",")
            # We only allow a max of 5 tags per doc
            for _tag in _tags:
                self._attach_tag(_tag)
