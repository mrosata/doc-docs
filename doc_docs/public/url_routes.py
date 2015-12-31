"""
Doc Docs >> 2015 - 2016
    by: Michael Rosata <<

Public URL Routes
-----------------
Most of the sites urls reside here in the public folder.
"""
from flask import Blueprint, render_template, current_app, request, url_for, redirect, flash

from flask_security import current_user, login_required, logout_user, forms

from . import resources, site_forms

from doc_docs.public.security_forms import ExtendedRegistrationForm
from doc_docs.public.creator import DocReviewCreator
from doc_docs.utilities import utils


from doc_docs import db
from doc_docs.sql import models
from sqlalchemy.orm.exc import NoResultFound

public = Blueprint('public', __name__, template_folder='../templates')


@public.context_processor
def public_context_processor():
    # Need to include the login form because integrating flask-security as sub template.
    register_user_form = ExtendedRegistrationForm()
    return dict(login_user_form=forms.LoginForm(), register_user_form=register_user_form)


@public.route('/')
@public.route('/index')
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
        review_form = creator.form()
        # Shortcut for is_submitted() and validate()
        if review_form.validate_on_submit():
            doc = creator.return_or_create_doc(creator, review_form.doc_url.data)
            creator.push(rating=review_form.rating.data, review=review_form.review.data, tags=review_form.tags.data,
                         detour=review_form.detour.data, summary=review_form.summary.data, discoverer=current_user)

            creator.create()

            return render_template(resources.add_new['html'], new_review_form=review_form)
        utils.log("YOU HAVE FAILED ME BIG TIME BRO!")
        return render_template(resources.add_new['html'], new_review_form=review_form)
    else:
        review_form = site_forms.ReviewForm()
        """PAGE VIEW (we must assume for now)"""
        return render_template(resources.add_new['html'], new_review_form=review_form)


@login_required
@public.route('/new_review')
def new_review():
    review_form = site_forms.ReviewForm()
    return render_template(resources.add_new['html'], new_review_form=review_form)


@public.route('/profile/<string:username>/')
def public_profile(username):
    user = db.session.query(models.User).filter_by(username=username).first()
    if user is not None:
        user_profile = db.session.query(models.UserProfile).filter_by(user_id=user.id).first()
        if user_profile is not None:
            profile_bio = db.session.query(models.UserBioText).filter_by(bio_text_id=user_profile.bio_text_id).first()
            return render_template(resources.personal_profile['html'], profile=user_profile, bio=profile_bio)

    # There is no user profile associated with the username used in the url, so redirect users to profile, else index
    return redirect(url_for('public.profile'))


@login_required
@public.route('/profile/')
def profile():
    """
    /profile - a user is able to see their own profile. It is the same as the view to view another persons profile
               except no "Edit Profile" button.
    :return:
    """
    try:
        user_profile = db.session.query(models.UserProfile).filter_by(user_id=current_user.id).one()
    except NoResultFound, e:
        current_app.logger.info("Current user %s had no profile! <<GENERATING PROFILE>>", current_user.id)
        user_profile = models.UserProfile(current_user)

    profile_bio = db.session.query(models.UserBioText).filter_by(bio_text_id=user_profile.bio_text_id).first()

    reviews = list()
    for r, p in db.session.query(models.DocReview, models.UserProfile).\
            filter(models.DocReview.reviewer == models.UserProfile.user_id).\
            filter(models.UserProfile.user_id == current_user.id).all():
        reviews.append(dict(review=r, username=p.user.username, doc=r.doc_doc))

    utils.log("These are the reviews this user has made thus far::::::: %r", reviews)

    body = db.session.query(models.DocReviewBody).all()
    utils.log("This is the labor of your review!!!!::  %r", body)

    return render_template(resources.personal_profile['html'], profile=user_profile, bio=profile_bio, reviews=reviews)


@login_required
@public.route('/profile/edit', methods=['POST', 'GET'])
def edit_profile():
    """
    This is the Edit Profile page. Upon POST it shall attempt to update the users profile before displaying the edit
    form.
    :return:
    """
    the_form = site_forms.ProfileForm()
    user_profile = db.session.query(models.UserProfile).filter_by(user_id=current_user.id).one()

    if user_profile is None:
        current_app.logger.info("Current user %s had no profile! <<GENERATING PROFILE>>", current_user.id)
        user_profile = models.UserProfile(current_user)
    bio = db.session.query(models.UserBioText).filter_by(bio_text_id=user_profile.bio_text_id).first()

    if str(request.method).lower() == 'post':
        # This is a submission. We should update the users profile.
        if the_form.validate_on_submit():
            utils.log(request.form)
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

    return render_template(resources.edit_profile['html'], profile_form=the_form, profile=user_profile, bio=bio)


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
    return "coming soon to a browser near you!"
