"""
Doc Docs >> 2015 - 2016
    by: Michael Rosata <<

Configurations
--------------
Extend the BaseConfig class to create new configuration setups.
"""

import os

# Map of configuration options
configurations = {
    "development": "doc_docs.config.DevConfig",
    "default": "doc_docs.config.DevConfig"
}
options = {
    "REGISTER_USERNAME_EMPTY_MSG": "The Username field Can't be empty.",
    "REGISTER_USERNAME_UNAVAILABLE_MSG": "Please choose another username, that name is unavailable.",
}


def configure_app(app):
    config_name = os.getenv('FLASK_CONFIGURATION', 'default')
    app.config.from_object(configurations[config_name])
    # Uncomment to take configurations from a file (located at doc_docs/config/
    # app.config.from_pyfile('app.conf', silent=False)


class BaseConfig(object):
    """
    These are saftey precaution settings. Minimal settings that an app
    would need to run. Every other setting class shall simply extend
    this base class and overwrite/add options for that particular setup.
    """
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:////vagrant/pro-docdocs.db'
    SECRET_KEY = '2-90d324d13nlSEa4l-EASc35Ldgfhfsd-34gkl-LF24s'
    SECURITY_CONFIRM = None
    SECURITY_CONFIRMABLE = None
    SECURITY_REGISTERABLE = True
    SECURITY_TRACKABLE = True
    SECURITY_PASSWORD_HASH = 'plaintext' #'pbkdf2_sha512'
    SECURITY_PASSWORD_SALT = 'pizza-party-exo-skeleton-base-bass-bayshe'
    # These are defaults of the Flask Security, I just like them listed
    SECURITY_TOKEN_AUTHENTICATION_KEY = 'auth_token'
    SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authentication-Token'
    SECURITY_FLASH_MESSAGES = True
    SECURITY_BLUEPRINT_NAME = 'security'
    SECURITY_LOGIN_URL = '/login'
    SECURITY_LOGOUT_URL = '/logout'
    SECURITY_REGISTER_URL = '/register'
    SECURITY_RESET_URL = '/reset'
    SECURITY_CHANGE_URL = '/change'
    # SECURITY_CONFIRM_URL = '/confirm'
    SECURITY_POST_LOGIN_VIEW = '/'
    SECURITY_POST_LOGOUT_VIEW = '/'
    SECURITY_CONFIRM_ERROR_VIEW = None
    SECURITY_POST_REGISTER_VIEW = None
    SECURITY_POST_CONFIRM_VIEW = None
    SECURITY_POST_RESET_VIEW = None
    SECURITY_POST_CHANGE_VIEW = None
    SECURITY_UNAUTHORIZED_VIEW = None
    SECURITY_PASSWORDLESS = False
    SECURITY_CHANGEABLE = False
    SECURITY_RECOVERABLE = False

    SEND_REGISTER_EMAIL = None


class DevConfig(BaseConfig):
    """
    This is the configuration for the app in Development mode.
    Show debug messages, host on 0,0,0,0 which port forwards from
    Vagrant to localhost 127.0.0.1, don't require email confirmations
    when user signup is done in DevConfig.
    """
    DEBUG = True
    TESTING = False
    HOST = '0.0.0.0'
    PORT = 5000
    SQLALCHEMY_DATABASE_URI = 'sqlite:////vagrant/dev-docdocs.db'
    # We don't need to verify email addresses in development
    SECURITY_CONFIRMABLE = None
    SECURITY_CONFIRM_URL = None
    SECURITY_REGISTERABLE = True
    SECURITY_CONFIRM_ERROR_VIEW = '/error'
    SEND_REGISTER_EMAIL = False
    SECURITY_SEND_REGISTER_EMAIL = False
    SECRET_KEY = '213nlSEal-EASc35Lhfsd-34gkl-LF'
    SECURITY_UNAUTHORIZED_VIEW = '/index'


class ProductionConfig(BaseConfig):
    """
    Configuration to use on live (production) servers.
    """
    # TODO: Define production configuration
