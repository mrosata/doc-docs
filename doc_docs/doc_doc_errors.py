"""
Doc Docs >> 2015 - 2016
    by: Michael Rosata << doc_docs.doc_doc_errors.py

---------
Custom errors and exceptions for the app
"""


class PreviousReviewException(Exception):

    def __init__(self, *args, **kwargs):
        super(PreviousReviewException, self).__init__(*args, **kwargs)