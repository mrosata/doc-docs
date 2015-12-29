"""
Doc Docs >> 2015 - 2016
    by: Michael Rosata <<

Models
------
Database models (tables) used through the application.
"""
import datetime

from flask.ext.sqlalchemy import SQLAlchemy
# from flask_security import UserMixin, RoleMixin

from doc_docs.utilities import utils

db = SQLAlchemy()


class DocDoc(db.Model):
    """
    Every Document or Article will be stored similar to a user. This will make it easier to
    aggregate data on an article over time. I am thinking to maybe abstract base_url in the
    future to another table so that the base_url of a page is like a category and entire
    sites could be cataloged. This way when a new article is added to a page and a user surfs
    to that page while having the "doc doc browser extension" installed the extension will be
    smart enough to ask for a review or at least note the page somehow.
    """
    __tablename__ = 'doc_doc'
    doc_id = db.Column('doc_id', db.Integer, primary_key=True)
    full_url = db.Column(db.String)
    port = db.Column(db.Integer, nullable=True)
    base_url = db.Column(db.String(100))
    pathname = db.Column(db.String(100))
    fragment = db.Column(db.String(100), nullable=True)
    query = db.Column(db.String(240), nullable=True)
    discoverer = db.Column(db.Integer, db.ForeignKey('user.id'))
    discovered = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    visits = db.Column(db.Integer)

    def __init__(self, url, discoverer, discovered):
        # Sanitize the url (break it into parts)
        url_parts = utils.get_url_parts(url)

        self.full_url = url_parts.full_url
        self.base_url = url_parts.base_url
        self.pathname = url_parts.pathname
        self.fragment = url_parts.fragment
        self.scheme = url_parts.scheme
        self.query = url_parts.query
        self.discoverer = discoverer
        self.discovered = discovered
        self.visits = 1

    def __repr__(self):
        return '<DocDoc %r>' % self.doc_id


class DocReview(db.Model):
    """
    A Review is a written item to be cataloged on behalf of a user. The review explains why they
    thought a certain way about a document/article. This will help other users to better be able
    to make a decision on whether or not to use a certain document for their personal use.
    """
    __tablename__ = 'doc_review'
    doc_review_id = db.Column('doc_review_id', db.Integer, primary_key=True)
    doc_id = db.Column('doc_id', db.Integer, db.ForeignKey('doc_doc.doc_id'))
    reviewer = db.Column(db.Integer, db.ForeignKey('user.id'))
    reviewed_on = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    summary = db.Column(db.Text(350))
    review_body_id = db.Column(db.Integer, db.ForeignKey('review_body.review_body_id'))

    def __init__(self, doc_id, reviewer, reviewed_on, summary):
        self.doc_id = doc_id
        self.reviewer = reviewer
        self.reviewed_on = reviewed_on
        self.summary = summary

    def __repr__(self):
        return '<class DocReview %r>' % self.doc_review_id


class DocRating(db.Model):
    """
    A simple rating, since a user may only rate a page once there is no need to have an explicit primary
    key for this table. Instead we use the unique combination of 'doc_doc_id' and 'user_id' as a primary
    key.
    """
    __tablename__ = 'doc_rating'
    doc_doc_id = db.Column('doc_doc_id', db.Integer, db.ForeignKey('doc_doc.doc_id'), primary_key=True)
    user_id = db.Column('reviewer', db.Integer, db.ForeignKey('user.id'))
    rating = db.Column(db.Integer(2))
    rated_on = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    db.PrimaryKeyConstraint('doc_doc_id', 'reviewer', name='doc_review_pk')

    def __init__(self, doc_id, user_id, rating, rated_on=None):
        self.doc_id = doc_id
        self.user_id = user_id
        self.rating = rating
        self.rated_on = rated_on

    def __repr__(self):
        return '<class DocRating %r>' % self.doc_doc_id


class DocReviewBody(db.Model):
    """
    This table holds the body of the review. The reviews table could grow large and since the text
    is variable in size and doesn't need to be seen unless a user navigates to that reviews page I
    think it's better to link it through another table. The table uses the same primary key as the
    DocReview object
    """
    __tablename__ = 'doc_review_body'
    doc_review_id = db.Column(db.Integer, db.ForeignKey('doc_review.doc_review_id'), primary_key=True)
    review_body = db.Column(db.Text)

    def __init__(self, doc_review_id, review_body):
        self.doc_review_id = doc_review_id
        self.review_body = review_body

    def __repr__(self):
        return '<class DocReviewBody %r>' % self.doc_review_id


class DocDetour(db.Model):
    """
    Doc Detours are just links to alternative articles. Since the alternative articles qualify to be docs, that
    is what they must be to be added into the table. When a user adds a detour the system will have to register
    it as a doc_doc first.
    """
    __tablename__ = 'doc_detour'
    target_doc_id = db.Column('target_doc_id', db.Integer, db.ForeignKey('doc_review.doc_review_id'), primary_key=True)
    detour_doc_id = db.Column('detour_doc_id', db.Integer, db.ForeignKey('doc_review.doc_review_id'), primary_key=True)
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
    # I'm not sure if this is an optimization or a de-optimization. I think using a 3 column primary key is smart ;)
    # I could be idiot though. Only deltatime will tell.
    db.PrimaryKeyConstraint('target_doc_id', 'detour_doc_id', 'user_id')
    review_body = db.Column(db.Text)

    def __init__(self, doc_review_id, review_body):
        self.doc_review_id = doc_review_id
        self.review_body = review_body

    def __repr__(self):
        return '<class DocReviewBody %r>' % self.doc_review_id


class CommunityApproval(db.Model):
    """
    Community Approvals are the votes made by users on reviews, ratings, and detours that other users have
    made. It's possible that there won't be a need to approval on a rating so I will stick to using the
    detours and reviews. Each user can only vote one time on their approval of a thing.
    """
    __tablename__ = 'community_approval'
    vote_id = db.Column(db.Integer, primary_key=True)
    doc_id = db.Column('doc_id', db.Integer, db.ForeignKey('doc_review.doc_review_id'))
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('doc_review.doc_review_id'))
    # Possible values for type are 'rating', 'review', 'detour'.
    type = db.Column('type', db.String(12), default='review')
    # True = up-vote and False = down-vote
    vote = db.Column(db.Boolean, default=True)
    db.UniqueConstraint('doc_id', 'user_id', 'type')

    def __init__(self, doc_review_id, review_body):
        self.doc_review_id = doc_review_id
        self.review_body = review_body

    def __repr__(self):
        return '<class DocReviewBody %r>' % self.doc_review_id
