# Interactive Testing Shell for the DocDocs application.

from sqlalchemy import func

from doc_docs import app, db, utils
from doc_docs.sql.models import UserProfile, User, UserBioText, UserMixin, CommunityApproval, \
    DocTerm, DocReview, DocTermRelationship, DocDetour, DocDoc, DocRating, DocReviewBody, Role, RoleMixin, DocSiteMeta

from doc_docs.sql.retriever import _q


def setup():
    print "\n\n\n" \
          "|/`===============================================`\\|\n" \
          "|~^   Welcome to the Docdocs interactive shell:   ^~|\n" \
          "|}                                                 {|\n" \
          "|._________________________________________________.|\n" \
          ""


def q():
    """
    Just a wrapper for db.session.query to make SQLAlchemy easier to perform from within the shell
    :return:
    """
    return db.session.query


def get_context(*args):
    ctx = app.test_request_context(*args)
    ctx.push()
    return ctx


setup()
