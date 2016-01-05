"""
Doc Docs >> 2015 - 2016
    by: Michael Rosata <<  doc_docs/sql/retriever.py
"""
from sqlalchemy import func

from doc_docs import app, db
from doc_docs.sql import models


class Finder:
    """
    Finder is the parent class for objects exposed through the QueryHelper class (see bottom of file). The purpose of
    this class is really just to house all the models that are utilized through the other classes which enheriet from
    Finder
    """
    User = models.User
    Profile = models.UserProfile
    Bio = models.UserBioText
    Doc = models.DocDoc
    Meta = models.DocSiteMeta
    Review = models.DocReview
    Body = models.DocReviewBody
    Term = models.DocTerm
    TermRelationship = models.DocTermRelationship

    def __init__(self, _q):
        self._q = _q

    def __repr__(self):
        return "<class Finder User: %, Profile: {0!r:s}, Bio: {1!r:s}, Doc: {2!r:s}, Review: {3!r:s}, Body: {4!r:s}, " \
               "Term: {0!r:s}, TermRelationship: {1!r:s}>" \
            .format(self.User, self.Profile, self.Bio, self.Doc, self.Review, self.Body, self.Term,
                    self.TermRelationship)


class UserFinder(Finder):

    def by_username(self, username):
        user = db.session.query(self.User).filter_by(username=username).first()
        return user


class ProfileFinder(Finder):

    def by_name(self, username, full_bio=True, create=False):
        """
        Get a profile using a user_id. full_bio argument determines whether the bio text should be returned or just
        the basics of the profile such as username and social data.
        :param create: boolean - Create the profile if account exists but the profile does not.
        :param full_bio: boolean - Should the bio text be returned as well
        :param username: Name of the user to query
        """
        profile = self.query(self.User.username, username, full_bio)
        if not profile and create is True:
            user = db.session.query(self.User).filter_by(username=username).first()
            if user is not None:
                profile = self.Profile(user)

        return profile

    def by_id(self, user_id, full_bio=True):
        """
        Get a profile using a user_id. full_bio argument determines whether the bio text should be returned or just
        the basics of the profile such as username and social data.
        :param full_bio:
        :param user_id:
        """
        return self.query(self.Profile.user_id, user_id, full_bio)

    def query(self, constraint, constraint_value, full_bio=True):
        p = self.Profile
        b = self.Bio
        u = self.User

        if full_bio is True:
            profile = \
                db.session.\
                query(u.username, p.user_id, p.first_name, p.last_name, p.twitter, p.facebook, p.github,
                      p.homepage, p.stackoverflow, b.bio_text).\
                filter(p.bio_text_id == b.bio_text_id).\
                filter(p.user_id == u.id). \
                filter(constraint == constraint_value). \
                first()
        else:
            profile = \
                db.session.\
                query(u.username, p.user_id, p.first_name, p.last_name, p.twitter, p.facebook, p.github, p.homepage).\
                filter(p.user_id == u.id).\
                filter(constraint == constraint_value).\
                first()
            
        return profile


class ReviewFinder(Finder):

    def get_feed(self, _limit=10, _offset=0):
        """
        Get a feed of recent reviews along with the doc_doc that belongs to it.

        :param _offset: default 10 - to help with paging the offset value
        :param _limit: default 10 - the amount of results to be returned at most.
        :return: - list of results with props doc_review_id, reviewed_on, summary, user, term_relationship,
                    doc_doc, site_meta
        """
        r = self.Review
        # p = db.aliased(self.Profile, name="user_profile")
        u = db.aliased(self.User, name="user_info")
        m = db.aliased(self.Meta, name="doc_site_meta")
        d = db.aliased(self.Doc, name="doc_doc")

        recent_feed = db.session.query(r.doc_review_id, r.reviewed_on, r.summary, u, r.term_relationship, d, m).\
            filter(r.doc_id == d.doc_id).\
            filter(r.reviewer == u.id).\
            order_by(r.reviewed_on.desc()).offset(_offset).limit(_limit).all()

        return recent_feed

    def by_username(self, username, full_text=False, with_meta=False):
        user = _q.user.by_username(username)
        user_id = None
        if isinstance(user, self.User):
            user_id = user.id
        return self.query(self.Review.reviewer, user_id)

    def by_user_id(self, user_id, full_text=False, with_meta=False):
        return self.query(self.Review.reviewer, user_id, full_text=full_text, with_meta=with_meta)
        pass

    def query(self, constraint, constraint_value, full_text=False, with_meta=False):
        """
        Make a query for a Review. This method is best called using one of the other methods provided on this class.
        :param full_text:
        :param constraint_value:
        :param constraint:
        :return:
        """
        r = self.Review
        d = self.Doc
        m = db.aliased(self.Meta, name="site_doc_meta")
        b = self.Body
        u = self.User

        if with_meta is True:
            reviews = db.session.query(r, m). \
                filter(r.doc_id == d.doc_id).\
                filter(constraint == constraint_value). \
                order_by(r.reviewed_on.desc()).all()
        else:
            reviews = db.session.query(r). \
                filter(constraint == constraint_value). \
                order_by(r.reviewed_on.desc()).all()
        return reviews


class TermFinder(Finder):

    def by_object_id(self, object_id):
        return self.query(self.TermRelationship.object_id, object_id)

    def query(self, constraint, constraint_value, max_results=5):
        t = self.Term
        dt = self.TermRelationship

        terms = db.session.query(t). \
            join(dt).filter(constraint == constraint_value).limit(max_results).all()

        return terms


class QueryHelper:
    """
    QueryHelper is an abstraction of the work that has to be done around the site such as returning user profiles,
    reviews, docdocs and such. Hopefully it will increase the readability of the rest of the code by making functions
    smaller as well as cut down on duplicated code in some places.

    To use QueryHelper just import _q which is an instance of this class created at the bottom of this file.
    The properties exposed by QueryHelper are all just references to members of the Finder class which is defined
    above. Finder classes expose methods that express how they should find something. For example with the ProfileFinder
    there are methods .by_id() .by_username() and this helps to keep similar functionality grouped and DRY.
    """
    def __init__(self):
        self.profile = ProfileFinder(self)
        self.review = ReviewFinder(self)
        self.user = UserFinder(self)
        self.term = TermFinder(self)
        pass

    @staticmethod
    def site_totals():
        """
        Total up all objects for displaying count information on the main page. Just for showing the community
        what all the work adds up to.
        :return: dict with doc_doc, doc_detour, doc_rating, doc_review
        """
        # TODO: Check how effecient this is.
        the_totals = {"doc_count": db.session.query(func.count("*")).select_from(models.DocDoc).scalar(),
                      "detour_count": db.session.query(func.count("*")).select_from(models.DocDetour).scalar(),
                      "rating_count": db.session.query(func.count("*")).select_from(models.DocRating).scalar(),
                      "review_count": db.session.query(func.count("*")).select_from(models.DocReview).scalar()}
        return the_totals

    def __call__(self, *args, **kwargs):
        """
        If the object is instanciated with arguments then treat it as a function which acts as db.session.query
        I'm not sure that this will work well as it is just an idea I had.

        :param args:
        :param kwargs:
        :return:
        """
        if not args and not kwargs:
            return self

        return db.session.query(*args, **kwargs)

    def __repr__(self):
        return "<class _q profile: %r, review: %r>" % (self.profile, self.review)


_q = QueryHelper()