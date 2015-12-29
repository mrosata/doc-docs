"""
Doc Docs >> 2015 - 2016
    by: Michael Rosata <<

Models
------
Database models (tables) used through the application.
"""
from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
# from flask_security import UserMixin, RoleMixin

db = SQLAlchemy()


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
        bio_text = UserBioText('<<empty cuz i sayzso>>')
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

    def __init__(self, bio_text):
        self.bio_text = bio_text

        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<class BioText bio_text_id: %r, bio_text: %r>' % (self.bio_text_id, self.bio_text)

