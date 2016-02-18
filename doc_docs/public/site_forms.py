from flask.ext.wtf import Form
from wtforms import StringField, IntegerField, TextAreaField, DecimalField, HiddenField
from wtforms.validators import DataRequired, URL, NumberRange, Optional, Email


class ReviewForm(Form):
    """
    The Review Form for users to critic a website with a textual explaination. This form
    also allows the user to add a detour and rating at the same time. However those are
    optional fields in the Review Form.
    """
    # doc_url The URL of the document which is being reviewed
    doc_url = StringField('Full URL of the Documentation / Article (include hashtag)',
                          validators=[DataRequired(), URL()])
    # rating The numeric rating given to the document by the reviewer.
    rating = DecimalField('rating', validators=[NumberRange(1, 10)])
    # review Actual review written by the user about the site that they entered as doc_url
    review = TextAreaField('Review (Max 1000 words)', default="", validators=[DataRequired()])
    # summary This is the Title of the review (excerpt)
    summary = StringField('Excerpt/Summary (optional)', validators=[Optional()])
    # detour An optional URL that the author suggests users should visit.
    detour = StringField('Detour Full URL (Must relate directly to reviewed content)',
                         validators=[Optional(), URL()])
    # tags For search reasons
    tags = StringField('Tags, comma, seperated, max, 5 (optional)', validators=[Optional()])

    def get_fields(self):
        return dict(doc_url=self.doc_url, rating=self.rating, review=self.review,
                    summary=self.summary, detour=self.detour, tags=self.tags)


class ReviewEditForm(Form):
    """
    The Review Form for users to critic a website with a textual explaination. This form
    also allows the user to add a detour and rating at the same time. However those are
    optional fields in the Review Form.
    """
    # doc_url The URL of the document which is being reviewed
    doc_url = HiddenField('Full URL of the Documentation / Article (include hashtag)',
                          validators=[DataRequired(), URL()])
    # rating The numeric rating given to the document by the reviewer.
    rating = DecimalField('rating', validators=[NumberRange(1, 10)])
    # review Actual review written by the user about the site that they entered as doc_url
    review = TextAreaField('Review (Max 1000 words)', default="", validators=[DataRequired()])
    # summary This is the Title of the review (excerpt)
    summary = StringField('Excerpt/Summary (optional)', validators=[Optional()])
    # detour An optional URL that the author suggests users should visit.
    detour = StringField('Detour Full URL (Must relate directly to reviewed content)',
                         validators=[Optional(), URL()])
    # tags For search reasons
    tags = StringField('Tags, comma, seperated, max, 5 (optional)', validators=[Optional()])

    def get_fields(self):
        return dict(doc_url=self.doc_url, rating=self.rating, review=self.review,
                    summary=self.summary, detour=self.detour, tags=self.tags)


class RatingForm(Form):
    """
    The Rating Form is simple, users can give a 1 - 10 rating of an article or piece of
    documentation that they have come across on their journeys.
    """
    # doc_url The URL of the document which is being reviewed
    doc_url = StringField('Full URL of the Documentation / Article (include hashtag)',
                          validators=[DataRequired(), URL()])
    # rating The numeric rating given to the document by the reviewer.
    rating = IntegerField('rating', validators=[DataRequired(),
                                                NumberRange(1, 10, "Choose a number 1 - 10")])


class DetourForm(Form):
    """
    The Detour Form is simple, users can leave an alternative source of information for
    future users to follow instead of reading the document or article detoured (or in
    combination with). Detours are meant to offer solutions to issues that users point out in
    documentation. They should not be used to point to better technology, only to better practices.
    """
    # doc_url The URL of the document which is being reviewed
    doc_url = StringField('Full URL of the Documentation / Article (include hashtag)',
                          validators=[DataRequired(), URL()])
    # detour An optional URL that the author suggests users should visit.
    detour = StringField('Detour Full URL (Must relate directly to reviewed content)',
                         validators=[DataRequired(), URL()])


class ProfileForm(Form):
    """
    A Profile is information pertaining to a user that doesn't concern site security or
    functionality. The profile is a means for users to put a public face to their fellow
    Doc Docs community members so when they publish helpful material on Doc Docs, they can
    drive traffic to their outside social sites and/or homepage.
    """

    first_name = StringField('First Name', validators=[Optional()])
    last_name = StringField('Last Name', validators=[Optional()])
    homepage = StringField('Homepage URL', validators=[Optional()])
    github = StringField('GitHub ID', validators=[Optional()])
    facebook = StringField('Facebook ID', validators=[Optional()])
    stackoverflow = StringField('StackOverflow', validators=[Optional()])
    twitter = StringField('Twitter ID', validators=[Optional()])
    bio_text = TextAreaField('Bio Text', validators=[Optional()])




