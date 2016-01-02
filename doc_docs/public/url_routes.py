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
            filter(models.UserProfile.user_id == current_user.id).\
            order_by(models.DocReview.reviewed_on.desc()).all():

        # TODO: Put this into an abstracted class to litter less in the url_routes page
        """Need to get the tags that are related to this review. First make a join from the term_relationship
        table to the term table matching relationships between the current doc_review in loop. We then make
        a list and populate it with any results before appending the next review to the list

        a_alias = db.aliased(models.DocTerm)
        _terms = db.session.query(models.DocTermRelationship).\
            join(a_alias, models.DocTermRelationship.term).\
            filter(a_alias.term_id == models.DocTermRelationship.term_id).\
            filter(models.DocTermRelationship.object_id == r.doc_review_id).\
            limit(5)
        """
        _terms = db.session.query(models.DocTerm).\
            join(models.DocTermRelationship).\
            filter(models.DocTermRelationship.object_id == r.doc_review_id).limit(5)
        terms = list()
        if _terms is not None:
            for term in _terms:
                terms.append({"term": term.term, "term_id": term.term_id})

        utils.log()("TERMS QUERIED THROUGH JOIN IN Profile Page: %r", terms)

        # Finally, we append all the data for this review and then goto next review
        reviews.append(dict(review=r, tags=terms, username=p.user.username, doc=r.doc_doc))

    utils.log("These are the reviews this user has made thus far::::::: %r", reviews)

    body = db.session.query(models.DocReviewBody).all()

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
    site_objects = list()
    if term_name is not None:
        _objects = db.session.query(models.DocTermRelationship).join(models.DocTerm).\
            filter(models.DocTermRelationship.term_id == models.DocTerm.term_id).\
            filter(models.DocTerm.term == term_name)
        if _objects is not None:
            for obj in _objects:
                _doc_review = db.session.query(models.DocReview).filter_by(doc_review_id=obj.object_id).first()
                doc_review = dict()
                if _doc_review is not None:
                    doc_review["summary"] = _doc_review.summary
                    doc_review["doc_doc"] = _doc_review.doc_doc
                    doc_review["reviewer"] = _doc_review.reviewer

                site_objects.append({
                    "term_id": obj.term_id,
                    "object_id": obj.object_id,
                    "doc_review": _doc_review
                })

    return "You wanna see my %s: %r" % (term_name, site_objects)


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
