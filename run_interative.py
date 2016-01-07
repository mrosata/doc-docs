# Interactive Testing Shell for the DocDocs application.

from sqlalchemy import func

from doc_docs import app, db, utils
from doc_docs.sql.models import UserProfile, User, UserBioText, UserMixin, CommunityApproval, \
    DocTerm, DocReview, DocDetour, DocDoc, DocRating, DocReviewBody, Role, RoleMixin, DocSiteMeta

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


def delete_all(delete_docdocs=True):
    """
    This will delete all the database entries except for users and user profiles. Pass in False as delete_docdocs
    to not delete the docs and their meta.
    :param delete_docdocs:
    :return:
    """
    print "Deleting all "
    if delete_docdocs is True:
        print "DocDoc and DocSiteMeta, "
        _q()(DocDoc).delete()
        _q()(DocSiteMeta).delete()
    print "DocTerm, DocReview, DocReviewBody, DocRating, DocDetour"
    _q()(DocReviewBody).delete()
    _q()(DocReview).delete()
    _q()(DocRating).delete()
    _q()(DocDetour).delete()
    _q()(DocTerm).delete()
    db.session.commit()


def snapshot(*args):
    for a in args:
        _items = _q()(a)
        print "Snapshot: %r, count: %r\n   %r" % (a, _items.count(), _items.all())


def get_context(*args):
    ctx = app.test_request_context(*args)
    ctx.push()
    return ctx


setup()
