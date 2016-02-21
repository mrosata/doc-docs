
"""
This is a small collection of some of the resources used throughout the app. It might be
easier to manage these locations here rather than spread out through the application. The
resources file is not to be confused as a config file, just references.
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
delete_review = {'html': 'public/doc-data/delete-review.html'}
# Client Secrets for OAuth2
client_secrets = {
    'google': 'doc_docs/conf/client_secrets.json',
    'github': 'doc_docs/conf/github_client_secrets.json',
    'fb': 'doc_docs/conf/fb_client_secrets.json'
}

