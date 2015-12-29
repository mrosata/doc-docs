"""
Doc Docs >> 2015 - 2016
    by: Michael Rosata <<
"""

import os
from urlparse import urlparse

from flask import current_app


class DocDocsUtilities:

    def __init__(self):
        pass

    @staticmethod
    def log(msg):
        current_app.logger.info(msg)

    @staticmethod
    def get_url_parts(url):
        """
        Basically this returns the same output as urlparse but shaped a little bit more like the columns in the
        doc docs table. This also ensures that we have '//' or an https? scheme preceding the url. It's needed or
        else the base_url ends up as the pathname because urlparse assumes a relative path.
        :param url:
        :return:
        """
        if url.find('http') != 0 and url.find('//') != 0:
            url = '//' + url
        parts = urlparse(url)
        return dict(base_url=parts.netloc, pathname=parts.path, query=parts.query, fragment=parts.fragment
                    , scheme=parts.scheme, full_url=parts.geturl())

    @staticmethod
    def get_app_base_path():
        """
        Returns the base path of the app (because it will be called from the main module maintaining the app).
        :return:
        """
        return os.path.dirname(os.path.realpath(__file__))

    @staticmethod
    def get_instance_folder_path():
        return os.path.join(DocDocsUtilities.get_app_base_path(), 'instance')


utils = DocDocsUtilities
