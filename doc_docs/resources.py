
"""
This is a list of the resources for use in the app. Not all resources are listed in here but I'm trying to get a
little collection of file locations so there is one place where everything can be edited or changed. Sort of the
way config options work. The reason I chose not to use the config.py file is because these aren't really settings
and there is already enough clutter from all the different options provided by flask, flask-security, sqlalchemy...
"""
# A generic error page. Located outside of public blueprint
error = {'html': 'layouts/_error.html'}
# The main page for both logged in and anonymous users
index = {'html': 'public/index.html'}
site_blog = {'html': 'public/blog.html'}
# Forms for logged in users to add a new {review/detour/rating}
add_new = {'html': 'public/doc-data/add-new.html'}

personal_profile = {'html': 'public/user/profile.html'}
edit_profile = {'html': 'public/user/edit-profile.html'}
# DocReviews linked to Tags
single_term = {'html': 'public/tag/doc_review.html'}
# A Single DocReview
doc_review = {'html': 'public/doc-data/review.html'}
edit_review = {'html': 'public/doc-data/edit-review.html'}
# Client Secrets for OAuth2
client_secrets = {
    'google': '/conf/client_secrets.json',
    'fb': 'doc_docs/conf/fb_client_secrets.json'
}