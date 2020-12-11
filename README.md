# LMNOP

## Live Music Notes, Opinions, Photographs
###New features:
* Now connected to the ticketmaster api which populates the database 
accessing 127.0.0.1:8000/ticket_master locally, or is updated automatically 
each Monday at 9 AM on the hosted site.
* User is now able to create new notes for shows, as well as upload photos

![alt text](media/readme_images/new_note.png)
* Site is connected to twitter, allowing user to post to the LMNOP twitter account 
when they create a new show note. Post may be viewed at https://twitter.com/LMNOP_Group4

* Site now limits the number of entries shown per page for user notes, shows, and venues

![alt text](media/readme_images/paginate.png)
* User is now able to provide and edit details about themselves on their profile page, and 
allows other users to view these details as well as a list of their notes.

![alt text](media/readme_images/edit.png)
![alt text](media/readme_images/profile.png)
* Page now sports a new and improved look 
* Notes are now easily searched from the notes tab

![alt text](media/readme_images/search.png)
* When the user logs out, they are provided with a goodbye message

![alt text](media/readme_images/goodbye.png)
* Users are now able to delete and edit their own notes

![alt text](media/readme_images/del_edit.png)
* Added a new tab link that allows the user to view the top 5 pages with the most notes
* Added feature that lets the user add a rating to their notes.
***
### To install

Create and activate a virtual environment. Use Python3 
as the interpreter. Suggest locating the venv/ directory 
outside of the code directory. In addition several environment 
variables are required for the program to run correctly locally.
The names of the variables must match exactly as displayed below. 

###Required environment variables:
####Ticketmaster:
Register at: https://developer-acct.ticketmaster.com/user/register
```
env variable: TICKETMASTER_KEY=put_your_key_here
```
####Twitter:
Register at: https://developer.twitter.com/en/docs/developer-portal/overview

env variables:
```
T_API_KEY=your_key_here
T_API_KEY_SEC=your_key_here
T_ACCESS_TOK=your_key_here 
T_ACCESS_TOK_SEC=your_key_here
```
##Windows Version:
####Create and run virtual environment:
```
python -m venv env
env\Scripts\activate
```
####Install required modules:
```
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
##Mac Version:
####Create and run virtual environment:
```
python3 -m venv env
source env/bin/activate
```
####Install required modules:

```
pip3 install -r requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver
```
Local site available at:

http://127.0.0.1:8000

Google Cloud Platform site:

https://www.google.com/url?q=https%3A%2F%2Flmnop-project5.uc.r.appspot.com
***
### Create superuser

`python manage.py createsuperuser`

enter username and password

will be able to use these to log into admin console at

127.0.0.1:8000/admin

***
### Run tests


```
python manage.py test lmn.tests
```

Or just some of the tests,

```
python manage.py test lmn.tests.test_views
python manage.py test lmn.tests.test_views.TestUserAuthentication
python manage.py test lmn.tests.test_views.TestUserAuthentication.test_user_registration_logs_user_in
```

***
### Functional Tests with Selenium

Make sure you have the latest version of Chrome or Firefox, and the most recent chromedriver or geckodriver, and latest Selenium.

chromedriver/geckodriver needs to be in path or you need to tell Selenium where it is. Pick an approach: http://stackoverflow.com/questions/40208051/selenium-using-python-geckodriver-executable-needs-to-be-in-path

If your DB is hosted at Elephant, your tests might time out, and you might need to use longer waits http://selenium-python.readthedocs.io/waits.html

Run tests with

```
python manage.py test lmn.tests.functional_tests
```

Or select tests, for example,
```
python manage.py test lmn.tests.functional_tests.HomePageTest
python manage.py test lmn.tests.functional_tests.BrowseArtists.test_searching_artists
```

***
### Test coverage

From directory with manage.py in it,

```
coverage run --source='.' manage.py test lmn.tests
coverage report
```

***
### PostgreSQL

Recommend using PaaS Postgres such as Elephant, instead of installing local Postgres. 
