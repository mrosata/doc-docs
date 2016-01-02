"""
Doc Docs >> 2015 - 2016
    by: Michael Rosata <<
"""

import os
from urlparse import urlparse

from flask import current_app
from doc_docs.config import options


class DocDocsUtilities:
    """
    Collection of utilities that are available and useful throughout different parts of the application.
    These are all static methods, to use them simply import utils (which is an instance of DocDocsUtilities).
    There are methods for logging, getting custom option values, getting url parts for the doc docs model + more
    """

    def __init__(self):
        pass

    @staticmethod
    def log(msg=None, obj=None):
        """
        Log a message to current app stdout
        If the caller doesn't pass any arguments then the function will return the logging function. This is so that
        the logger will give an acurrate file location in the std
        :param msg:
        :param obj:
        :return:
        """
        if msg is None and obj is None:
            return current_app.logger.info
        current_app.logger.info(msg, obj)

    @staticmethod
    def option(option_name):
        """
        Get Option setup from config.py file
        Right now the options dict only has my custom config items in it.
        :param option_name:
        :return:
        """
        return options.get(option_name)

    @staticmethod
    def get_url_parts(url):
        """
        Basically this returns the same output as urlparse but shaped a little bit more like the columns in the
        doc docs table. This also ensures that we have '//' or an https? scheme preceding the url. It's needed or
        else the base_url ends up as the pathname because urlparse assumes a relative path.
        :param url:
        :return:
        """
        if type(url) is not "str":
            url = str(url)

        if url.find('http') != 0 and url.find('//') != 0:
            url = '//' + url

        parts = urlparse(url)
        url_dict = {
            'pathname': parts.path,
            'query_string': parts.query,
            'fragment': parts.fragment,
            'params': parts.params,
            'base_url': parts.netloc,
            'full_url': parts.geturl(),
            'scheme': parts.scheme
        }

        return url_dict

    @staticmethod
    def get_app_base_path():
        """
        Returns the base path of the app (because it will be called from the main module maintaining the app).
        :return:
        """
        return os.path.dirname(os.path.realpath(__file__))

    @staticmethod
    def get_inst_path():
        return os.path.join(DocDocsUtilities.get_app_base_path(), 'instance')


utils = DocDocsUtilities
