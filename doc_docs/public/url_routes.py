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
from doc_docs.sql.models import UserMixin, User, RoleMixin, Role, UserProfile, UserBioText, CommunityApproval
from doc_docs.sql.models import DocDoc, DocReviewBody, DocReview, DocRating, DocDetour, DocTerm, DocTermRelationship
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
    user = db.session.query(User).filter_by(username=username).first()
    if user is not None:
        user_profile = db.session.query(UserProfile).filter_by(user_id=user.id).first()
        if user_profile is not None:
            profile_bio = db.session.query(UserBioText).filter_by(bio_text_id=user_profile.bio_text_id).first()
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
        user_profile = db.session.query(UserProfile).filter_by(user_id=current_user.id).one()
    except NoResultFound, e:
        current_app.logger.info("Current user %s had no profile! <<GENERATING PROFILE>>", current_user.id)
        user_profile = UserProfile(current_user)

    profile_bio = db.session.query(UserBioText).filter_by(bio_text_id=user_profile.bio_text_id).first()

    reviews = list()
    for r, p in db.session.query(DocReview, UserProfile).\
            filter(DocReview.reviewer == UserProfile.user_id).\
            filter(UserProfile.user_id == current_user.id).\
            order_by(DocReview.reviewed_on.desc()).all():

        # TODO: Put this into an abstracted class to litter less in the url_routes page
        """Need to get the tags that are related to this review. First make a join from the term_relationship
        table to the term table matching relationships between the current doc_review in loop. We then make
        a list and populate it with any results before appending the next review to the list

        a_alias = db.aliased(DocTerm)
        _terms = db.session.query(DocTermRelationship).\
            join(a_alias, DocTermRelationship.term).\
            filter(a_alias.term_id == DocTermRelationship.term_id).\
            filter(DocTermRelationship.object_id == r.doc_review_id).\
            limit(5)
        """
        _terms = db.session.query(DocTerm).\
            join(DocTermRelationship).\
            filter(DocTermRelationship.object_id == r.doc_review_id).limit(5)
        terms = list()
        if _terms is not None:
            for term in _terms:
                terms.append({"term": term.term, "term_id": term.term_id})

        utils.log()("TERMS QUERIED THROUGH JOIN IN Profile Page: %r", terms)

        # Finally, we append all the data for this review and then goto next review
        reviews.append(dict(review=r, tags=terms, username=p.user.username, doc=r.doc_doc))

    utils.log("These are the reviews this user has made thus far::::::: %r", reviews)

    body = db.session.query(DocReviewBody).all()

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
        term_name = str(db.session.query(DocTerm).filter_by(term_id=term_id).first())

    # related_objects will hold the data to be rendered in the template (reviews linked to term).
    related_objects = list()
    # We want to find any object (DocReview) which has term_name as a term to display on page.
    linked_reviews = db.session.query(DocTermRelationship.term_id, DocTerm.term, DocReview).\
        filter(DocReview.doc_review_id == DocTermRelationship.object_id).\
        filter(DocTermRelationship.term_id == DocTerm.term_id).\
        filter(DocTerm.term == term_name).all()

    for r in linked_reviews:
        related_objects.append({
            "term_id": r[0],
            "term": r[1],
            "review": r[2],
        })

    return render_template(resources.single_term["html"], term_name=term_name, related_objects=related_objects)


@public.route('/review/<int:review_id>')
def review(review_id):
    r = db.session.query(DocReview).filter_by(doc_review_id=review_id).first()

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
    return "coming soon to a browser near you!"
