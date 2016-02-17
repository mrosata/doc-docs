"""
Doc Docs >> 2015 - 2016
    by: Michael Rosata << doc_doc/public/creator/creator.py

------
Creator will assist in creating things like doc_docs by combining logic from database models
and from site forms
"""
from datetime import datetime

from .doc_scraper import fetch_meta
from doc_docs.sql import models
from doc_docs.public.site_forms import ReviewForm
from doc_docs.utilities import utils
from doc_docs import db, current_user, PreviousReviewException, ReviewNotExistException, \
    MissingInformationException


class Creator:
    """
    _data is a list of attributes this object (or child) will accept and data is where the
    values are populated after being pushed in by push(). They are really methods meant to be
    implemented on child classes
    """
    _data = tuple()
    data = dict()
    doc = None
    review = None
    rating = None

    def __init__(self):
        self.session = db.session
        pass

    def return_or_create_doc(self, doc_url, user_id=None):
        """
        Returns the doc doc matching doc_url. If the url has never been added to our system
        then return_or_create_doc will add the DocDoc URL and mark the current user as the
        user who had discovered the url for the site. A doc doc is shared between all the
        users on the site.

        :param user_id: user to mark as discoverer (will us current_user if not supplied)
        :param doc_url: string - url to lookup.
        :return DocDoc:
        """
        parsed_url = utils.get_url_parts(doc_url)
        doc = None
        if user_id is None:
            user_id = current_user.id

        if self.session.query(models.DocDoc).all().count > 0:
            doc = self.session.query(models.DocDoc). \
                filter(models.DocDoc.full_url == parsed_url['full_url']). \
                filter(models.DocDoc.base_url == parsed_url['base_url']). \
                filter(models.DocDoc.pathname == parsed_url['pathname']). \
                filter(models.DocDoc.fragment == parsed_url['fragment']).first()

        if doc is None:
            # Create the og_meta and the doc
            og_meta = fetch_meta(doc_url)

            doc = models \
                .DocDoc(full_url=parsed_url["full_url"], base_url=parsed_url["base_url"],
                        pathname=parsed_url["pathname"], fragment=parsed_url["fragment"],
                        query_string=parsed_url["query_string"], params=parsed_url["params"],
                        discoverer=user_id, discovered=datetime.utcnow(), visits=1)
            doc_meta = models.DocSiteMeta(**og_meta)

            doc.doc_site_meta = doc_meta
            db.session.add(doc)
            db.session.add(doc_meta)
            db.session.commit()

        self.doc = doc
        return doc

    def push(self, **kwargs):
        """
        Each creator object can list kwargs that it will accept and they can be arbitrarily
        pushed to it.
        :param kwargs:
        :return:
        """
        for key in kwargs:
            if key in self._data:
                self.data[key] = kwargs[key]


class DocRatingCreator(Creator):
    @staticmethod
    def rate(doc_id, user_id, rating):
        """
        Pass in a DocDoc, User and rating to set it in the database. It's really just a buffer
        between the model.DocRating object and potentially could depracate in near future.
        Depends on usefulness.
        :param doc_id:
        :param user_id:
        :param rating:
        :return:
        """
        # doc_id = doc_doc.doc_id
        rating = rating

        the_rating = models.DocRating(doc_doc_id=doc_id, user_id=user_id, rating=rating)
        db.session.add(the_rating)

        return the_rating


class DocReviewCreator(Creator):
    _data = ('summary', 'review', 'rating', 'discoverer', 'tags')
    form = ReviewForm
    model = models.DocReview
    _tag_count = 0
    tags = list()

    def __init__(self, user):
        self.user = user
        Creator.__init__(self)

    @staticmethod
    def convert_to_summary(passage="", max_chars=300, max_words=70):
        """
        Take a passage of text and turn it into a summary by splitting words. Keeps it under
        a minumum word and character length
        :param passage: The passage to use in making the summary
        :param max_chars: 300
        :param max_words:  70
        """
        summary = ""

        words = passage.encode('ascii', 'ignore').split(' ')
        word_count = 0
        while len(words) > 0 and word_count < max_words \
              and len(summary) + len(words[0]) <= max_chars:
            summary = "{0}{1} ".format(summary, words[0])
            words = words[1:]
            word_count += 1

        return summary

    def create(self, edit=False):
        """
        This will create a review after we already have set self.doc which is done through
        the inherieted method return_or_create_doc()
        :return self.doc:
        """
        if self.doc is None:
            return False

        # Check for all the required fields before moving on.
        # add fields through .push() inherited via creator.
        for x in self._data:
            if x not in self.data:
                raise MissingInformationException(x)

        # Was there a previous review by this user on this doc?
        self.review = self.session.query(models.DocReview). \
            filter_by(doc_id=self.doc.doc_id). \
            filter_by(reviewer=self.user.id). \
            first()

        # A Reviewer may only review an article/document 1 time.
        if self.review is not None and edit is False:
            raise PreviousReviewException()
        elif self.review is None and edit is True:
            raise ReviewNotExistException()

        review_text = self.data["review"].encode('ascii', 'ignore')
        if self.data["summary"] == '' or not self.data["summary"]:
            self.data["summary"] = self.convert_to_summary(review_text)

        # Review will be None only if this is a create
        if edit is True:
            # This is an edit. First check to see if there is a review body
            review_body = self.review.doc_review_body

            # Remove any relationship from terms related to review (below we'll attach/add new)
            terms = models.DocTerm.query.filter(models.DocTerm.reviews.contains(self.review))
            for t in terms:
                t.reviews.remove(self.review)

            rating = self.session.query(models.DocRating). \
                filter(models.DocRating.doc_doc_id == self.doc.doc_id). \
                filter(models.DocRating.user_id == self.user.id)

            if rating.first() is not None:
                # Update the users rating (they already made)
                rating.update({models.DocRating.rating: int(self.data["rating"])})
            else:
                # create a new rating since there new has been one.
                DocRatingCreator().rate(self.doc.doc_id, self.user.id, int(self.data["rating"]))

            # Update the doc review (summary)
            self.review.query.\
                filter_by(doc_id=self.doc.doc_id). \
                filter_by(reviewer=self.user.id). \
                update({models.DocReview.summary: self.data["summary"]},
                       synchronize_session='fetch')
            self.review.doc_review_body.review_body = self.data["review"]
        else:
            # This is a new review being created
            self.review = models.DocReview(doc_id=self.doc.doc_id, reviewer=self.user.id,
                                           summary=self.data["summary"])
            review_body = models.DocReviewBody(review_body=review_text)
            # Create a new rating
            if self.data["rating"]:
                # This will add the rating but not commit
                DocRatingCreator().rate(self.doc.doc_id, self.user.id, int(self.data["rating"]))

        if self.review is None:
            return None

        # This will add the terms but not commit
        self.update_terms()

        self.review.doc_review_body = review_body
        db.session.add(self.review)
        db.session.add(review_body)
        # Now we commit them all together.
        db.session.commit()
        return self.doc

    def _attach_tag(self, tag):
        """
        Check if a tag already exists and then attach it to the doc_review in the db (if not
        exists then create it).
        :param tag:
        :return:
        """
        if self.review is None:
            return None

        session = self.session
        if self._tag_count > 5 or self.doc is None:
            return False
        tag = str(tag.strip())
        # Get or create a new term
        term = session.query(models.DocTerm).filter_by(term=tag).first()
        if term is None:
            term = models.DocTerm(term=tag)

        self.review.terms.append(term)
        db.session.add(term)

        # Keep track of tag count in order to enforce set limits
        self._tag_count += 1

    def update_terms(self):
        if self.data["tags"] is not None:
            _tags = str(self.data["tags"]).split(",")
            # We only allow a max of 5 tags per doc
            # TODO: Abstract that value to a config setting might be better.
            for _tag in _tags:
                self._attach_tag(_tag)
