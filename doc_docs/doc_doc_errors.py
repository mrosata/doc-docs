"""
Doc Docs >> 2015 - 2016
    by: Michael Rosata << doc_docs.doc_doc_errors.py

---------
Custom errors and exceptions for the app
"""


class PreviousReviewException(Exception):
    """
    User has tried to perform an action which would create a review on their behalf
    on a doc doc url which they already have reviewed.
    """
    pass


class ReviewNotExistException(Exception):
    """
    User has tried to perform an action which would require a review which they have
    already created, and that review can't be found.
    """
    pass
