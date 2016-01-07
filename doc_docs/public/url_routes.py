"""
Doc Docs >> 2015 - 2016
    by: Michael Rosata <<

Public URL Routes
-----------------
Most of the sites urls reside here in the public folder.

http://onethingsimple.com/2015/07/thinking-forward-just-for-a-moment/
This was a good article. It was not completely based in fact however. It seemed that the author came to a lot of the conclusions on his own thinking. Which is ok, but that really isn't what a doc is now is it? I said now is it? I said that is not what a doc truely is now shouldn't we take this author out to the wood shed and end him? No no no, that would be too easy.

"""
from flask import Blueprint, render_template, current_app, request, url_for, redirect, flash

from flask_security import current_user, login_required, logout_user, forms

from . import site_forms

from doc_docs.public.security_forms import ExtendedRegistrationForm
from doc_docs.public.creator import DocReviewCreator

from doc_docs.utilities import utils

from doc_docs import db, resources, PreviousReviewException
from doc_docs.sql.retriever import _q
from doc_docs.sql.models import UserMixin, User, RoleMixin, Role, UserProfile, UserBioText, CommunityApproval
from doc_docs.sql.models import DocReviewBody, DocReview, DocRating, DocDetour, DocTerm
from doc_docs.sql.models import DocDoc, DocSiteMeta
from doc_docs.sql.retriever import _q
from sqlalchemy.orm.exc import NoResultFound

public = Blueprint('public', __name__, template_folder='../templates')


@public.context_processor
def public_context_processor():
    # Need to include the login form because integrating flask-security as sub template.
    register_form = ExtendedRegistrationForm()
    login_form = forms.LoginForm()

    item_totals = _q.site_totals()
    recent_reviews = _q.review.get_feed(10)
    return dict(login_user_form=login_form, register_user_form=register_form, recently_added=recent_reviews,
                **item_totals)


@public.route('/forgot')
def forgot_password():
    return "I don't care! Be more careful next time!"


@public.route('/')
@public.route('/index/')
def index():
    return render_template(resources.index['html'])


@login_required
@public.route('/logout')
def logout():
    """
    Simple logout, returns the visitor to the main page
    :return:
    """
    logout_user()
    return redirect('/')


@login_required
@public.route('/docs/add_new', methods=['POST', 'GET'])
def add_new():
    creator = DocReviewCreator(current_user)
    if str(request.method).upper() == 'POST':
        """FROM SUBMISSION"""
        review_form = site_forms.ReviewForm()
        # Shortcut for is_submitted() and validate()
        if review_form.validate_on_submit():
            doc = creator.return_or_create_doc(review_form.doc_url.data)
            creator.push(rating=review_form.rating.data, review=review_form.review.data, tags=review_form.tags.data,
                         detour=review_form.detour.data, summary=review_form.summary.data, discoverer=current_user)

            try:
                creator.create()
                # TODO: This is temporary, send back to profile after successful review posted
                return redirect("/profile")
            except PreviousReviewException:
                # We want to render the error to the review form to let user know they can't make 2 reviews on 1 doc.
                review_form.doc_url.errors.append("It seems you have already reviewed this Document in the past!")

            return render_template(resources.add_new['html'], new_review_form=review_form)
        # There was a problem with the form, so we will return the from w/errors
        return render_template(resources.add_new['html'], new_review_form=review_form)
    else:
        review_form = site_forms.ReviewForm()
        # The regular page with form for adding a new review/rating/detour
        return render_template(resources.add_new['html'], new_review_form=review_form)


@login_required
@public.route('/new_review')
def new_review():
    review_form = site_forms.ReviewForm()
    return render_template(resources.add_new['html'], new_review_form=review_form)


@public.route('/profile/')
@public.route('/profile/<string:username>/')
def profile(username=None):
    if username is None:
        username = current_user.username

    p = _q.profile.by_name(username, create=True)

    reviews = list()
    for r, m in _q.review.by_user_id(current_user.id, with_meta=True, with_rating=False):
        ratings = _q.rating.by_review(r, community=True)
        reviews.append(dict(review=r, doc_meta=m, username=username, ratings=ratings))

    return render_template(resources.personal_profile['html'], profile=p, reviews=reviews)
    # There is no user profile associated with the username used in the url, so redirect users to profile, else index


@login_required
@public.route('/profile/edit', methods=['POST', 'GET'])
def edit_profile():
    """
    This is the Edit Profile page. Upon POST it shall attempt to update the users profile before displaying the edit
    form.
    :return:
    """
    the_form = site_forms.ProfileForm()
    user_profile = db.session.query(UserProfile).filter_by(user_id=current_user.id).first()

    if user_profile is None:
        user_profile = UserProfile(current_user)
        db.session.commit()

    bio = db.session.query(UserBioText).filter_by(bio_text_id=user_profile.bio_text_id).first()

    if str(request.method).lower() == 'post':
        # This is a submission. We should update the users profile.
        if the_form.validate_on_submit():
            rform = request.form

            user_profile.first_name = rform['first_name']
            user_profile.last_name = rform['last_name']
            user_profile.twitter = rform['twitter']
            user_profile.github = rform['github']
            user_profile.facebook = rform['facebook']
            user_profile.stackoverflow = rform['stackoverflow']
            user_profile.homepage = rform['homepage']
            bio.bio_text = rform['bio_text']

            db.session.add(user_profile)
            db.session.commit()

            # On Successful Edit we will redirect the user back to their profile
            return redirect(url_for("public.profile"))

    # On non-successful update or initial page load/GET request we will show the edit form
    return render_template(resources.edit_profile['html'], profile_form=the_form, profile=user_profile, bio=bio)


@public.route('/tag/<string:term_name>/')
@public.route('/tag/<int:term_id>/')
def tag(term_name=None, term_id=None):
    """
    The Tags page is where all the resources on the site which have been filed using a certain tag are listed. This
    makes searching for relevant content a bit simplier.
    :param term_name:
    :param term_id:
    :return:
    """
    if term_name is None:
        if term_id is None:
            # Can't render a term without knowing its name or id
            return redirect("/", 404)
        term = str(db.session.query(DocTerm).filter_by(term_id=term_id).first())
    else:
        # We want to find any object (DocReview) which has term_name as a term to display on page.
        term = db.session.query(DocTerm).\
            filter(DocTerm.term == term_name).first()
    return render_template(resources.single_term["html"], term=term)


@public.route('/review/<int:review_id>')
def review(review_id):

    r = db.session.query(DocReview, ).filter_by(doc_review_id=review_id).first()

    if r is None:
        return redirect("/", 404)

    return render_template(resources.doc_review["html"], data=r)


@public.route('/discussion')
def discussion():
    return "coming soon to a browser near you!"


@public.route('/developers')
def developers():
    return "coming soon to a browser near you!"


@public.route('/feeds')
def the_feeds():
    return "coming soon to a browser near you!"


@public.route('/archive')
def the_archive():
    return "coming soon to a browser near you!"


@public.route('/blog')
def the_blog():
    return render_template(resources.site_blog["html"], body_classes=["the-blog"])
