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
    Rating = models.DocRating
    Review = models.DocReview
    Body = models.DocReviewBody
    Term = models.DocTerm

    def __init__(self, _q):
        self._q = _q

    def __repr__(self):
        return "<class Finder User: {0!r:s}, Profile: {1!r:s}, Bio: {2!r:s}, Doc: {3!r:s}, Review: {4!r:s}, " \
               "Body: {5!r:s}, Term: {6!r:s}>". \
            format(self.User, self.Profile, self.Bio, self.Doc, self.Review, self.Body, self.Term)


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
                db.session.commit()

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
                db.session. \
                    query(u.username, p.user_id, p.first_name, p.last_name, p.twitter, p.facebook,
                          p.github,
                          p.homepage, p.stackoverflow, b.bio_text). \
                    filter(p.bio_text_id == b.bio_text_id). \
                    filter(p.user_id == u.id). \
                    filter(constraint == constraint_value). \
                    first()
        else:
            profile = \
                db.session. \
                    query(u.username, p.user_id, p.first_name, p.last_name, p.twitter, p.facebook,
                          p.github, p.homepage). \
                    filter(p.user_id == u.id). \
                    filter(constraint == constraint_value). \
                    first()

        return profile


class RatingFinder(Finder):
    def by_review(self, review, community=True):
        if not isinstance(review, self.Review):
            return None
        doc_id = review.doc_id
        user_id = review.reviewer

        return self.query(doc_id, user_id=user_id, community=community)

    def query(self, doc_id, user_id=None, community=True):
        ra = self.Rating

        results = dict()

        if user_id is not None:
            results["user"] = (db.session.query(ra.rating).
                               filter_by(doc_doc_id=doc_id, user_id=user_id).scalar())
        if community is True:
            results["community"] = \
                (db.session.query(func.avg(ra.rating).label("average")).
                 filter(ra.doc_doc_id == doc_id).scalar())

        if community is False:
            # return all ratings.
            ratings = (db.session.query(ra).filter_by(doc_doc_id=doc_id).all())
            if user_id is None:
                # then just return ratings no dict()
                return ratings
            results["ratings"] = ratings

        return results


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

        recent_feed = db.session.query(r.doc_review_id, r.reviewed_on, r.summary, u, r.terms, d, m). \
            filter(r.doc_id == d.doc_id). \
            filter(r.reviewer == u.id). \
            group_by(r.doc_review_id). \
            order_by(r.reviewed_on.desc()).offset(_offset).limit(_limit).all()

        return recent_feed

    def by_username(self, username, with_rating=False):
        user = _q.user.by_username(username)
        user_id = None
        if isinstance(user, self.User):
            user_id = user.id
        return self.query(self.Review.reviewer, user_id, with_rating=with_rating)

    def by_user_id(self, user_id, with_rating=False, full_text=False, with_meta=False):
        return self.query(self.Review.reviewer, user_id, with_rating=with_rating,
                          full_text=full_text, with_meta=with_meta)

    def by_id(self, review_id, with_rating=True, full_text=False, with_meta=False):
        return self.query(self.Review.doc_review_id, review_id, with_rating=with_rating,
                          full_text=full_text, with_meta=with_meta, single=True)

    def query(self, constraint, constraint_value, with_rating=False, full_text=False,
              with_meta=False, single=False):
        """
        Make a query for a Review. This method is best called using one of the other methods provided on this class.
        :param single:
        :param with_meta:
        :type with_rating: object
        :param full_text:
        :param constraint_value:
        :param constraint:
        :return:
        """
        r = self.Review
        ra = self.Rating
        d = self.Doc

        if with_meta is True:
            # Get reviews and meta (and optionally rating)
            if with_rating is True:
                r_query = db.session.query(r, ra). \
                    filter(ra.doc_doc_id == r.doc_id). \
                    filter(
                      constraint_value == constraint_value)
            else:
                r_query = db.session.query(r)

            # Now that the r_query is settled we can get reviews
            reviews = r_query. \
                filter(r.doc_id == d.doc_id). \
                filter(constraint == constraint_value). \
                group_by(r.doc_id). \
                order_by(r.reviewed_on.desc())
        else:
            # get reviews without meta (and optionally rating)
            if with_rating is True:
                r_query = db.session.query(r, ra).filter(
                      ra.doc_doc_id == r.doc_id).filter(ra.user_id == r.reviewer)
            else:
                r_query = db.session.query(r)
            reviews = r_query. \
                filter(constraint == constraint_value). \
                group_by(r.doc_id). \
                order_by(r.reviewed_on.desc())

        if single is True:
            reviews = reviews.first()[0]
        else:
            reviews = reviews.all()

        return reviews


class QueryHelper:
    """
    QueryHelper is an abstraction of the work that has to be done around the site such as
    returning user profiles, reviews, docdocs and such. Hopefully it will increase the
    readability of the rest of the code by making functions smaller as well as cut down on
    duplicated code in some places. To use QueryHelper just import _q which is an instance  of
    this class created at the bottom of this file. The properties exposed by QueryHelper are all
    just references to members of the Finder class which is defined above. Finder classes expose
    methods that express how they should find something. For example with the ProfileFinder
    there are methods .by_id() .by_username() and this helps to keep similar functionality
    grouped and DRY.
    """

    def __init__(self):
        self.profile = ProfileFinder(self)
        self.review = ReviewFinder(self)
        self.rating = RatingFinder(self)
        self.user = UserFinder(self)
        pass

    @staticmethod
    def site_totals():
        """
        Total up all objects for displaying count information on the main page. Just for showing
        the community what all the work adds up to.

        :return: dict with doc_doc, doc_detour, doc_rating, doc_review
        """
        # TODO: Check how effecient this is.
        totals = {
            "doc_count": db.session.query(func.count("*")).select_from(
                  models.DocDoc).scalar(),
            "detour_count": db.session.query(func.count("*")).select_from(
                models.DocDetour).scalar(),
            "rating_count": db.session.query(func.count("*")).select_from(
                models.DocRating).scalar(),
            "review_count": db.session.query(func.count("*")).select_from(
                models.DocReview).scalar()}
        return totals

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
