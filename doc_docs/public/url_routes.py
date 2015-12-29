"""
Doc Docs >> 2015 - 2016
    by: Michael Rosata <<

Public URL Routes
-----------------
Most of the sites urls reside here in the public folder.
"""

from flask import Blueprint, render_template, current_app, request, _request_ctx_stack, redirect, flash

from flask_security import current_user, login_required, logout_user, login_user, utils, forms

# This is a file with resources in dicts.
from doc_docs.public import resources, site_forms
from doc_docs.sql import DocReview, DocReviewBody, DocDoc, DocDetour, DocRating, UserProfile, UserBioText, db
from doc_docs.utilities import utils

import pprint

public = Blueprint('public', __name__, template_folder='../templates')


@public.context_processor
def public_context_processor():
    # Need to include the login form because integrating flask-security as sub template.
    return dict(login_user_form=forms.LoginForm(), register_user_form=forms.RegisterForm())


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
    if str(request.method).upper() == 'POST':
        """FROM SUBMISSION"""
        review_form = site_forms.ReviewForm(request.form)
        current_app.logger.info('REVIEW FORM %s')
        # Shortcut for is_submitted() and validate()
        if review_form.validate_on_submit():
            # TODO: WHAT THE CRAP YO, Figure out how to turn the form into a doc review!
            #DocReview(review_form.get_fields())
            return "Here you go bro YOU PASS!"
        return "Here you go bro. YOU FAIL!"
    else:
        review_form = site_forms.ReviewForm()
        """PAGE VIEW (we must assume for now)"""
        return render_template(resources.add_new['html'], new_review_form=review_form)


@login_required
@public.route('/new_review')
def new_review():
    review_form = site_forms.ReviewForm()
    return render_template(resources.add_new['html'], new_review_form=review_form)


@login_required
@public.route('/profile/')
def profile():
    user_profile = db.session.query(UserProfile).filter_by(user_id=current_user.id).one()

    if user_profile is None:
        current_app.logger.info("Current user %s had no profile! <<GENERATING PROFILE>>", current_user.id)
        user_profile = UserProfile(current_user)

    profile_bio = db.session.query(UserBioText).filter_by(bio_text_id=user_profile.bio_text_id).first()

    return render_template(resources.personal_profile['html'], profile=user_profile, bio=profile_bio)


@login_required
@public.route('/profile/edit', methods=['POST', 'GET'])
def edit_profile():
    """
    This is the Edit Profile page. Upon POST it shall attempt to update the users profile before displaying the edit
    form.
    :return:
    """
    the_form = site_forms.ProfileForm()
    user_profile = db.session.query(UserProfile).filter_by(user_id=current_user.id).one()

    if user_profile is None:
        current_app.logger.info("Current user %s had no profile! <<GENERATING PROFILE>>", current_user.id)
        user_profile = UserProfile(current_user)
    bio = db.session.query(UserBioText).filter_by(bio_text_id=user_profile.bio_text_id).first()

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
