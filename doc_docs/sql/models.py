"""
Doc Docs >> 2015 - 2016
    by: Michael Rosata <<

db.Models
------
Database models (tables) used through the application.
"""
from datetime import datetime
from flask.ext.security import UserMixin, RoleMixin

from doc_docs import db


# This is the association for Flask_Security linking Users and Roles One-to-Many
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

# This is the apps association linking Reviews to Terms (Tags) Many-to-Many
reviews_terms = db.Table('reviews_terms',
                         db.Column("review", db.Integer, db.ForeignKey("doc_review.doc_review_id")),
                         db.Column("term", db.Integer, db.ForeignKey("doc_term.term_id")))


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
    # provider is the
    provider = db.Column(db.Integer(1), default=0)
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

    provider_list = ["client", "facebook", "google", "github"]

    def get_provider_id(self, provider=None):
        """
        Get the provider id by looking it up in this list. The provider is who provided the
        users initial account information upon registration. There is no tightly coupled behavior
        linked to this data, meaning it is more informational than functional at this time. It
        could be useful for instance if a user signed up and then came back to the site after being
        away for a few months and they tried to use the login form or to reset their password
        forgetting that they signed up with Facebook and not the user form. We could inform the
        user to sign in using Facebook.

        :param provider:
        :return integer:
        """
        if provider in self.provider_list:
            return self.provider_list.index(provider)
        return 0

    def __repr__(self):
        return '<User %r>' % self.email


class UserProfile(db.Model, UserMixin):
    """
    User Profile Data. I'm torn between keeping social data on the profile. It could be
    just as easily done in a meta data table. I will store data here now to keep the application
    simple atm. Note: that the UserProfile is one of the only tables that is using a custom
    __init__ method. This makes the insert with the bio easier.
    """
    __tablename__ = 'user_profile'
    profile_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    first_name = db.Column(db.String(45), default='')
    last_name = db.Column(db.String(45), default='')
    homepage = db.Column(db.String(100), default='')
    github = db.Column(db.String(50), default='')
    google = db.Column(db.String(50), default='')
    facebook = db.Column(db.String(50), default='')
    stackoverflow = db.Column(db.String(50), default='')
    twitter = db.Column(db.String(50), default='')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow())
    bio_text_id = db.Column(db.Integer, db.ForeignKey('user_bio_text.bio_text_id'))

    user = db.relationship('User', uselist=False)
    user_bio_text = db.relationship('UserBioText', uselist=False)

    bio_text = None

    def __init_old__(self, user, first_name='', last_name='', homepage='', github='', facebook='',
                 stackoverflow='', twitter='', updated_at=None, bio_text=""):
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

        # Create bio text entry also when creating a new profile and link it back to here.
        bio_text = UserBioText()
        self.bio_text_id = bio_text.bio_text_id
        self.bio_text = bio_text.bio_text

        db.session.add(self)
        db.session.add(bio_text)

    def __repr__(self):
        return '<class UserProfile user_id: %r, first_name: %r, last_name: %r, homepage: %r, ' \
               'github: %r, facebook: %r, stackoverflow: %r, twitter: %r>' \
               % (self.user_id, self.first_name, self.last_name, self.homepage, self.github,
                  self.facebook,
                  self.stackoverflow, self.twitter)


class UserBioText(db.Model):
    """
    Bio Text is a bio written by a user about themselves. It links from the profile table and
    every user is able to write one.
    """
    __tablename__ = 'user_bio_text'
    bio_text_id = db.Column('bio_text_id', db.Integer, primary_key=True)
    bio_text = db.Column(db.Text, default='')

    def __repr__(self):
        return '<class BioText bio_text_id: %r, bio_text: %r>' % (self.bio_text_id, self.bio_text)


class DocSiteMeta(db.Model):
    """
    Site meta is the og:meta data parsed from a site when it is initially added to DocDocs.
    The image right now will just be a link but in the future it would probably be good to save
    the image. I'm not sure. I know that a lot of sites are trying to stop people from remotely
    displaying their content so it might be needed to actually download the images from sites.
    But that's a lot of images, although they could be compressed a lot.
    """
    __tablename__ = "doc_site_meta"
    meta_id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(255), nullable=True, default="")
    title = db.Column(db.String(255), nullable=True, default="")
    url = db.Column(db.String(300))
    site_type = db.Column(db.String(255), nullable=True, default="")
    locale = db.Column(db.String(20), nullable=True, default="")
    locale_alternate = db.Column(db.String(100), nullable=True, default="")
    site_name = db.Column(db.String(255), nullable=True, default="")
    description = db.Column(db.String(300), nullable=True, default="")
    determiner = db.Column(db.String(10), nullable=True, default="")
    video = db.Column(db.String(140), nullable=True, default="")
    audio = db.Column(db.String(140), nullable=True, default="")

    doc_doc = db.relationship("DocDoc")


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
    meta_data_id = db.Column(db.Integer, db.ForeignKey("doc_site_meta.meta_id"))

    # doc_site_meta = db.relationship("DocSiteMeta", lazy="joined")
    doc_site_meta = db.relationship("DocSiteMeta")
    user = db.relationship("User")

    def __repr__(self):
        return '<class DocDoc doc_id: %r, base_url: %r, pathname: %r, fragment: %r, ' \
               'query_string: %r, params %r, discoverer: %r, discovered: %r, visits: %r, ' \
               'meta_data_id: %r, doc_site_meta: %r, user: %r>' % \
               (self.doc_id, self.base_url, self.pathname, self.fragment,
                self.query_string, self.params, self.discoverer, self.discovered, self.visits,
                self.meta_data_id, self.doc_site_meta, self.user)


class DocReviewBody(db.Model):
    """
    This table holds the body of the review. The reviews table could grow large and since
    the text is variable in size and doesn't need to be seen unless a user navigates to that
    reviews page I think it's better to link it through another table. The table uses the same
    primary key as the DocReview object
    """
    __tablename__ = 'doc_review_body'
    review_body_id = db.Column(db.Integer, primary_key=True)
    review_body = db.Column(db.Text)

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
    review_body_id = db.Column(db.Integer, db.ForeignKey("doc_review_body"))
    summary = db.Column(db.Text(350))

    terms = db.relationship("DocTerm", secondary=reviews_terms, back_populates="reviews")

    doc_review_body = db.relationship("DocReviewBody")
    user = db.relationship("User")
    doc_doc = db.relationship("DocDoc")

    def get_form_data(self, key):
        """
        Get back data from the DocReview that matches a form key. This is for easy retrieval of
        data in a readable form and by common semantic reference. Notice the first line of the
        function adds self to db.session, the reason for this is that in off cases (testing from
        cli especially) the DocReview is not added to the session which prevents lazy loading of
        model instances referenced through the DocReview model instance. For example:
        self.doc_review_body.review_body

        :param key:
        :return:
        """
        db.session.add(self)
        rv = ""
        if key == 'url' or key == 'full_url':
            rv = self.doc_doc.full_url

        elif key == 'review':
            rv = self.doc_review_body.review_body

        elif key == 'tags' or key == 'terms':
            l = list()
            for i in self.terms:
                l.append(i.term)
            rv = ', '.join(l)

        elif key == 'rating':
            # Return the scalar rating value for a doc rating made by the user who wrote review.
            rating = db.session.query(DocRating).filter_by(
                  doc_doc_id=self.doc_id, user_id=self.reviewer).first()
            if rating is not None:
                rv = int(rating.rating)
        elif key in self.__dict__:
            rv = self.__dict__[key]

        return rv

    def __repr__(self):
        return "<class DocReview doc_review_id: %r, doc_id: %r, review_body_id: %r, " \
               "reviewer: %r, reviewed_on: %r, summary: %r, user: %r, doc_doc: %r, " \
               "doc_review_body: %r>" % \
               (self.doc_review_id, self.doc_id, self.review_body_id, self.reviewer,
                self.reviewed_on, self.summary,
                self.user, self.doc_doc, self.doc_review_body)


class DocRating(db.Model):
    """
    A simple rating, since a user may only rate a page once there is no need to have an explicit
    primary key for this table. Instead we use the unique combination of 'doc_doc_id' and
    'user_id' as a primary key.
    """
    __tablename__ = 'doc_rating'
    doc_doc_id = db.Column(db.Integer, db.ForeignKey('doc_doc.doc_id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    rating = db.Column(db.Integer)
    rated_on = db.Column(db.DateTime, default=datetime.utcnow())
    db.PrimaryKeyConstraint('doc_doc_id', 'user_id', name='doc_rating_pk')

    doc_doc = db.relationship("DocDoc")
    user = db.relationship("User")

    def __repr__(self):
        return '<class DocRating doc_doc_id: %r, user_id: %r, rating: %r, rated_on: %r>' % \
               (self.doc_doc_id, self.user_id, self.rating, self.rated_on)


class DocDetour(db.Model):
    """
    Doc Detours are just links to alternative articles. Since the alternative articles qualify
    to be docs, that is what they must be to be added into the table. When a user adds a detour
    the system will have to register it as a doc_doc first.
    """
    __tablename__ = 'doc_detour'
    target_doc_id = db.Column(
          'target_doc_id', db.Integer, db.ForeignKey('doc_review.doc_review_id'), primary_key=True)
    detour_doc_id = db.Column(
          'detour_doc_id', db.Integer, db.ForeignKey('doc_review.doc_review_id'), primary_key=True)
    user_id = db.Column(
          'user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)

    # I'm not sure if this is an optimization or a de-optimization.
    # I think using a 3 column primary key is smart ;)
    db.PrimaryKeyConstraint('target_doc_id', 'detour_doc_id', 'user_id')
    review_body = db.Column(db.Text)

    def __repr__(self):
        return '<class DocDetour target_doc_id: %r, detour_doc_id: %r, user_id: %r>' % \
               self.target_doc_id, self.detour_doc_id, self.user_id


class DocTerm(db.Model):
    """
    A Term can relate to any object. Right now it only links using Reviews through the
    review_term association (top of file). This is many-to-many relationship handled by
    SQL Alchemy.
    """
    __tablename__ = "doc_term"
    term_id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(64))
    # reviews = db.relationship("DocReview", secondary=reviews_terms, back_populates="terms")
    reviews = db.relationship("DocReview", secondary=reviews_terms)

    def __repr__(self):
        return "<class DocTerm term_id: %r, term: %r>" % \
               (self.term_id, self.term)


class CommunityApproval(db.Model):
    """
    Community Approvals are the votes made by users on reviews, ratings, and detours that
    other users have made. It's possible that there won't be a need to approval on a rating so I
    will stick to using the detours and reviews. Each user can only vote one time on their
    approval of a thing.
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

    def __repr__(self):
        return """<class DocReviewBody %r>""" % self.doc_review_id


db.create_all()
db.session.commit()
