# Interactive Testing Shell for the DocDocs application.

from sqlalchemy import func

from doc_docs import app, db, utils
from doc_docs.sql.models import UserProfile, User, UserBioText, UserMixin, CommunityApproval, \
    DocTerm, DocReview, DocTermRelationship, DocDetour, DocDoc, DocRating, DocReviewBody, Role, RoleMixin


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


def get_context():
    ctx = app.test_request_context()
    ctx.push()
    return ctx


if __name__ != '__main__':
    exit()

setup()

