
"""
This is a list of the resources for use in the public module. The public module shows all the
main pages of the website. Pulling in locations like this is just an experiment that I am
doing for the moment. It might be in the future that I go back to doing things the "norm"
and just put the static resources inline in each file.
"""
# The main page for both logged in and anonymous users
index = {'html': 'public/index.html'}
# Forms for logged in users to add a new {review/detour/rating}
add_new = {'html': 'public/doc-data/add-new.html'}
personal_profile = {'html': 'public/user/profile.html'}
edit_profile = {'html': 'public/user/edit-profile.html'}
