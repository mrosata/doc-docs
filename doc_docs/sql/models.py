"""
Doc Docs >> 2015 - 2016
    by: Michael Rosata <<

Models
------
Database models (tables) used through the application.
"""
from datetime import datetime
from flask.ext.security import UserMixin, RoleMixin

from doc_docs import utils, app, db


roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    """
    Roles indicate the actions that a user is able to take on the site as well
    as the pages that they would be allowed to access.
    """
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    """
    User private information. This table is used for registration, security and
    tracking. See `UserProfile` for a more public/social description of a user.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    # Time user confirmed registration via email
    confirmed_at = db.Column(db.DateTime())
    # Login tracking extras integrated via flask_security.
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(64))
    current_login_ip = db.Column(db.String(64))
    login_count = db.Column(db.Integer())
    # For roles, required to give varied levels of security through permissions to
    # perform certain tasks described by a users role.
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return '<User %r>' % self.email


class UserProfile(db.Model, UserMixin):
    """
    User Profile Data. I'm torn between keeping social data on the profile. It could be just as easily done as
    meta data. I will do this for now to keep the application simple though.
    """
    __tablename__ = 'user_profile'
    profile_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    first_name = db.Column(db.String(45), default='')
    last_name = db.Column(db.String(45), default='')
    homepage = db.Column(db.String(100), default='')
    github = db.Column(db.String(50), default='')
    facebook = db.Column(db.String(50), default='')
    stackoverflow = db.Column(db.String(50), default='')
    twitter = db.Column(db.String(50), default='')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow())
    bio_text_id = db.Column(db.Integer, db.ForeignKey('user_bio_text.bio_text_id'))

    user = db.relationship('User', uselist=False)
    user_bio_text = db.relationship('UserBioText', uselist=False)

    bio_text = None

    def __init__(self, user, first_name='', last_name='', homepage='', github='', facebook='',
                       stackoverflow='', twitter='', updated_at=None):
        self.user = user
        self.first_name = first_name
        self.last_name = last_name
        self.homepage = homepage
        self.github = github
        self.facebook = facebook
        self.stackoverflow = stackoverflow
        self.twitter = twitter

        if updated_at is None:
            updated_at = datetime.utcnow()

        self.updated_at = updated_at

        # We have to create a bio text entry as well when we create a new profile and link it back to here.
        bio_text = UserBioText()
        self.bio_text_id = bio_text.bio_text_id
        self.bio_text = bio_text.bio_text

        db.session.add(self)
        db.session.commit()


    def __repr__(self):
        return '<class UserProfile user_id: %r, first_name: %r, last_name: %r, homepage: %r, ' \
               'github: %r, facebook: %r, stackoverflow: %r, twitter: %r>'\
               % (self.user_id, self.first_name, self.last_name, self.homepage, self.github, self.facebook,
                  self.stackoverflow, self.twitter)


class UserBioText(db.Model):
    """
    Bio Text is a bio written by a user about themselves. It links from the profile table and every
    user is able to write one.
    """
    __tablename__ = 'user_bio_text'
    bio_text_id = db.Column('bio_text_id', db.Integer, primary_key=True)
    bio_text = db.Column(db.Text, default='')

    def __init__(self, bio_text=None):
        self.bio_text = bio_text

        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<class BioText bio_text_id: %r, bio_text: %r>' % (self.bio_text_id, self.bio_text)


class DocDoc(db.Model):
    """
    Every Document or Article will be stored similar to a user. This will make it easier to
    aggregate data on an article over time. I am thinking to maybe abstract base_url in the
    future to another table so that the base_url of a page is like a category and entire
    sites could be cataloged. This way when a new article is added to a page and a user surfs
    to that page while having the "doc doc browser extension" installed the extension will be
    smart enough to ask for a review or at least note the page somehow.
    """
    __tablename__ = "doc_doc"
    doc_id = db.Column("doc_id", db.Integer, primary_key=True)
    full_url = db.Column(db.String(440), nullable=False)
    port = db.Column(db.Integer, nullable=True)
    base_url = db.Column(db.String(120), nullable=False)
    pathname = db.Column(db.String(120), default="", nullable=False)
    fragment = db.Column(db.String(100), default="", nullable=True)
    query_string = db.Column(db.String(100), default="", nullable=True)
    params = db.Column(db.String(100), default="", nullable=True)
    discoverer = db.Column(db.Integer, db.ForeignKey("user.id"))
    discovered = db.Column(db.DateTime, default=datetime.utcnow())
    visits = db.Column(db.Integer, default=1)

    user = db.relationship("User")

    def __init__(self, url, discoverer, discovered=None):
        # Sanitize the url (break it into parts)
        url_parts = utils.get_url_parts(url)

        self.full_url = url_parts["full_url"]
        self.base_url = url_parts["base_url"]
        self.pathname = url_parts["pathname"]
        self.fragment = url_parts["fragment"]
        self.query_string = url_parts["query_string"]
        self.params = url_parts["params"]
        self.discoverer = discoverer.id
        if discovered is None:
            discovered = datetime.utcnow()
        self.discovered = discovered
        self.visits = 1

        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<class DocDoc doc_id: %r, base_url: %r, pathname: %r, fragment: %r, query_string: %r, ' \
               'params %r, discoverer: %r, discovered: %r, visits: %r>' %\
               (self.doc_id, self.base_url, self.pathname, self.fragment,
                self.query_string, self.params, self.discoverer, self.discovered, self.visits)


class DocReviewBody(db.Model):
    """
    This table holds the body of the review. The reviews table could grow large and since the text
    is variable in size and doesn't need to be seen unless a user navigates to that reviews page I
    think it's better to link it through another table. The table uses the same primary key as the
    DocReview object
    """
    __tablename__ = 'doc_review_body'
    review_body_id = db.Column(db.Integer, primary_key=True)
    review_body = db.Column(db.Text)

    def __init__(self, review_body):
        self.review_body = review_body

        db.session.add(self)

    def __repr__(self):
        return '<class DocReviewBody review_body_id: %r, review_body: %r>' % \
               (self.review_body_id, self.review_body)


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
    reviewed_on = db.Column(db.DateTime, default=datetime.utcnow())
    summary = db.Column(db.Text(350))
    review_body_id = db.Column(db.Integer, db.ForeignKey('doc_review_body.review_body_id'))

    # terms = db.relationship("DocTerm", backref="doc_review")
    # doc_review_body = DocReviewBody("DocReviewBody")
    doc_review_body = db.relationship("DocReviewBody")
    user = db.relationship("User")
    doc_doc = db.relationship("DocDoc")
    term_relationship = db.relationship("DocTermRelationship")

    def __init__(self, doc_id, reviewer, review, summary, reviewed_on=None):
        self.doc_id = doc_id
        self.reviewer = reviewer.id
        self.review = review
        self.summary = summary
        # Set the time to be current time if wasn't passed in.
        if reviewed_on is None:
            reviewed_on = datetime.utcnow()
        self.reviewed_on = reviewed_on

        # We create the review and then sqlalchemy will reference it in the review_body_id field
        self.doc_review_body = DocReviewBody(review)

        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<class DocReview doc_review_id: %r, doc_id: %r, review_body_id: %r, reviewer: %r, ' \
               'reviewed_on: %r, summary: %r, user: %r, doc_doc: %r, doc_review_body: %r>' % \
               (self.doc_review_id, self.doc_id, self.review_body_id, self.reviewer, self.reviewed_on, self.summary,
                self.user, self.doc_doc, self.doc_review_body)


class DocRating(db.Model):
    """
    A simple rating, since a user may only rate a page once there is no need to have an explicit primary
    key for this table. Instead we use the unique combination of 'doc_doc_id' and 'user_id' as a primary
    key.
    """
    __tablename__ = 'doc_rating'
    doc_doc_id = db.Column(db.Integer, db.ForeignKey('doc_doc.doc_id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    rating = db.Column(db.Integer(2))
    rated_on = db.Column(db.DateTime, default=datetime.utcnow())
    db.PrimaryKeyConstraint('doc_doc_id', 'reviewer', name='doc_review_pk')

    def __init__(self, doc_id, user_id, rating, rated_on=None):
        self.doc_id = doc_id
        self.user_id = user_id
        self.rating = rating
        self.rated_on = rated_on

        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<class DocRating %r>' % self.doc_doc_id


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

        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<class DocReviewBody %r>' % self.doc_review_id


class DocTerm(db.Model):
    """
    A Term can relate to any object. They should link to a term through a table such as DocTermRelationship
    """
    __tablename__ = "term"
    term_id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(64))

    def __init__(self, term):
        self.term = term

        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return "<class DocTerm term_id: %r, term: %r>" %\
               (self.term_id, self.term)


class DocTermRelationship(db.Model):
    """
    This sets the relationship from a term to a doc
    """
    __tablename__ = "term_relationship"
    term_id = db.Column(db.Integer, db.ForeignKey("term.term_id"), primary_key=True)
    object_id = db.Column(db.Integer, db.ForeignKey("doc_review.doc_review_id"), primary_key=True)
    object_type = db.Column(db.String(16), default="doc")

    db.PrimaryKeyConstraint("term_id", "object_id", name="term_relationship_pk")

    doc_review = db.relationship("DocReview")
    term = db.relationship("DocTerm")

    def __init__(self, term_id, object_id, object_type="doc_review"):
        self.term_id = term_id
        self.object_id = object_id
        self.object_type = object_type

        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return "<class DocTermRelationship term_id: %r, object_id: %r, object_type: %r>" %\
               (self.term_id, self.object_id, self.object_type)


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

        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return """<class DocReviewBody %r>""" % self.doc_review_id


db.create_all()
db.session.commit()