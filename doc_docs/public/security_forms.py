
from doc_docs import utils

from flask_security.forms import LoginForm, RegisterForm, Required, StringField, Length

from doc_docs import db
from doc_docs.sql.models import User


class ExtendedLoginForm(LoginForm):
    """
    At the moment this is just the same as the regular login form. I will have to extend it in the future though
    to support the OAuth login
    """
    def __init__(self, *args, **kwargs):
        super(ExtendedLoginForm, self).__init__(*args, **kwargs)


class ExtendedRegistrationForm(RegisterForm):
    """
    Additional information for the registration form
    """
    username = StringField(None, [Required(), Length(min=6, max=20,
                                                     message="Username musty be between 6 and 20 characters.")])

    def validate_username(self, field):
        """
        This will be called by Flask Security when the user registers their account. It will be check to
        make sure that the username is valid because it's not a typical Flask-Security field.

        :param field: object with the username field data sent from form submission
        :return:
        """
        # Make sure that the username is of proper length.
        username_length = str().count(field.data.strip())
        if not username_length >= 6 and not username_length < 20:
            return False

        # Make sure that the username is not empty
        if field.data.strip() == '':
            field.username.errors.append(unicode(utils.option("REGISTER_USERNAME_EMPTY_MSG")))
            return False

        # Make sure that the username is unique
        user = db.session.query(User).filter_by(username=field.data).first()
        if user is not None:
            # The username is already taken by another user (the query above came back with a result)
            self.username.errors.append(unicode(utils.option("REGISTER_USERNAME_UNAVAILABLE_MSG")))
            return False

        return True
