#Models

This wiki page is to outline the state of development for the "Doc Docs" projects database. This page
will only be informative to "Doc Docs" contributors and may be removed in future versions. It is not 
meant to be a manual but just an overview of our current schema. If your a plugin developer and have
suggestions on how these models could be enhanced feel free to get in touch.


##Tables

#### user

|     id     | username |     email     | confirmed_at | password | active | last_login_at  | current_login_at | last_login_ip | login_count | roles |
|--------------------------------------------------------------------------------------------------------------------------------------|
|  int(10)   |  str(32) |    str(64)    |  datetime    | str(255) |  bool  |    datetime    |     datetime     |    str(64)    |   int()     | int() |
|  primary   |  unique  |    unique     |                         |        |                |                  |               |             |       |


#### roles
|    id    |   name   |   description   |
|-----------------------------------|
|   int()  |  str(64) |  str(255)       |
|          |          |                 |


#### user_roles
This table manages which user has what role so the flask security is able to protect the site from unwanted actions
taken by non authorized accounts.



#### profile_data
The `profile_data` table has information which is public about a user. This is data which they are able to change 
in their profile page and which will be displayed to other members of the site that come to view a users profile.

| profile_id | display_name | first_name | last_name  | homepage   | github  | facebook | stackoverflow | twitter | bio_text_id  |
|--------------------------------------------------------------------------------------------------------------------|
|  int(10)   | str(40)      |  str(40)   |  str(40)   |  str(80)   | str(30) | str(30)  | str(30)       | str(30) |    int(10)   |
|   primary  | unique       |            |            |            | unique  |          |               |         |    serial    |  

** Notes: It is possible to signup to stackoverflow with a long username. I decided to limit each username to 30 chars. 
Possibly in the future I may pull all social usernames and ids into a meta table because popular sites are always 
changing.


#### profile_map
Map the profiles to a user_id. This keeps a bit of separation between the user table and the profile table. The profiles 
will be used in urls so I think it could be better to not show the users actual id in the url.

| profile_id | user_id |
|--------------------|
| int(10)   | int(10)  |
| primary   | primary  |


#### user_bio_text
This is part of the profiles but abstracted to prevent bloating the `profile_data` table which has data which will be 
accessed a lot more and is a lot slimmer. The bios will only be seen on profile pages where the data in the 
`profile_data` table will be used all over the site and plugins to give general info about the author of a review or 
detour.

| user_bio_id | bio_text |
|----------------------|
|  int(10)    |  text    |
| primary     |          |


#### doc_doc
These are the subjects of this application. Webpages which contain information which our members can review, rate, and 
detour for the benefit of the rest of our community.

|   doc_id   | full_url | base_url | pathname |  fragment |  query  | port  | discoverer | discovered |  visits |
|-----------------------------------------------------------------------------------------------------|
| int(12)    | str()    | str(100) | str(100) | str(100)  | int(10) | int() | datetime   |  datetime  | int(10) |
| primary    |          |          |           |         |       |            |            |         |


#### doc_review

| doc_review_id | doc_id     | reviewer  | reviewed_on  | summary  | review_body_id |
|-----------------------------------------------------------------------|
| int(12)       | int(12)    |  int(10)  |   datetime   | str(255) | int(12)        |
| primary       | unique +   | + unique  |              |          | foreign        |


#### doc_rating

| doc_doc_id    | user_id | rating   | rated_on |
|------------------------------------------|
|   int(12)     | int(12) | int(2)   | datetime |
|   primary     | primary |          |          |


#### doc_review_body

| doc_review_id  | review_body |
|---------------------------|
| int(12)        |    text     |
| primary fk     |             |


#### doc_detour

| doc_detour_id | doc_doc_id | author_id | url      | review_body_id |
|-------------------------------------------------------------|
| int(12)       | int(12)    |  int(10)  | str(255) | int(12)        |
| primary       | unique +   | + unique  |          | foreign        |


#### community_approval

| vote_id  | doc_id   | user_id  |   type   |    date  | vote |
|-------------------------------------------------------|
| int(12)  | int(12)  |  int(10) |  str(12) | datetime | bool |
| primary  |          |          |          |          |      |
