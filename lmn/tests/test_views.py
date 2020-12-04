from django.test import TestCase, Client

from django.urls import reverse
from django.contrib import auth
from django.contrib.auth import authenticate

from lmn.models import Venue, Artist, Note, Show
from django.contrib.auth.models import User

import re, datetime
from datetime import timezone
import os

import tempfile
from PIL import Image
import filecmp


# TODO verify correct templates are rendered.

class TestEmptyViews(TestCase):

    ''' main views - the ones in the navigation menu'''
    def test_with_no_artists_returns_empty_list(self):
        response = self.client.get(reverse('artist_list'))
        self.assertFalse(response.context['artists'])  # An empty list is false

    def test_with_no_venues_returns_empty_list(self):
        response = self.client.get(reverse('venue_list'))
        self.assertFalse(response.context['venues'])  # An empty list is false

    def test_with_no_notes_returns_empty_list(self):
        response = self.client.get(reverse('latest_notes'))
        self.assertFalse(response.context['notes'])  # An empty list is false


class TestArtistViews(TestCase):

    fixtures = ['testing_artists', 'testing_venues', 'testing_shows']

    def test_all_artists_displays_all_alphabetically(self):
        response = self.client.get(reverse('artist_list'))

        # .* matches 0 or more of any character. Test to see if
        # these names are present, in the right order

        regex = '.*ACDC.*REM.*Yes.*'
        response_text = str(response.content)

        self.assertTrue(re.match(regex, response_text))
        self.assertEqual(len(response.context['artists']), 3)


    def test_artists_search_clear_link(self):
        response = self.client.get( reverse('artist_list') , {'search_name' : 'ACDC'} )

        # There is a clear link, it's url is the main venue page
        all_artists_url = reverse('artist_list')
        self.assertContains(response, all_artists_url)


    def test_artist_search_no_search_results(self):
        response = self.client.get( reverse('artist_list') , {'search_name' : 'Queen'} )
        self.assertNotContains(response, 'Yes')
        self.assertNotContains(response, 'REM')
        self.assertNotContains(response, 'ACDC')
        # Check the length of artists list is 0
        self.assertEqual(len(response.context['artists']), 0)


    def test_artist_search_partial_match_search_results(self):

        response = self.client.get(reverse('artist_list'), {'search_name' : 'e'})
        # Should be two responses, Yes and REM
        self.assertContains(response, 'Yes')
        self.assertContains(response, 'REM')
        self.assertNotContains(response, 'ACDC')
        # Check the length of artists list is 2
        self.assertEqual(len(response.context['artists']), 2)


    def test_artist_search_one_search_result(self):

        response = self.client.get(reverse('artist_list'), {'search_name' : 'ACDC'} )
        self.assertNotContains(response, 'REM')
        self.assertNotContains(response, 'Yes')
        self.assertContains(response, 'ACDC')
        # Check the length of artists list is 1
        self.assertEqual(len(response.context['artists']), 1)


    def test_correct_template_used_for_artists(self):
        # Show all
        response = self.client.get(reverse('artist_list'))
        self.assertTemplateUsed(response, 'lmn/artists/artist_list.html')

        # Search with matches
        response = self.client.get(reverse('artist_list'), {'search_name' : 'ACDC'} )
        self.assertTemplateUsed(response, 'lmn/artists/artist_list.html')
        # Search no matches
        response = self.client.get(reverse('artist_list'), {'search_name' : 'Non Existant Band'})
        self.assertTemplateUsed(response, 'lmn/artists/artist_list.html')

        # Artist detail
        response = self.client.get(reverse('artist_detail', kwargs={'artist_pk':1}))
        self.assertTemplateUsed(response, 'lmn/artists/artist_detail.html')

        # Artist list for venue
        response = self.client.get(reverse('artists_at_venue', kwargs={'venue_pk':1}))
        self.assertTemplateUsed(response, 'lmn/artists/artist_list_for_venue.html')


    def test_artist_detail(self):

        ''' Artist 1 details displayed in correct template '''
        # kwargs to fill in parts of url. Not get or post params

        response = self.client.get(reverse('artist_detail', kwargs={'artist_pk' : 1} ))
        self.assertContains(response, 'REM')
        self.assertEqual(response.context['artist'].name, 'REM')
        self.assertEqual(response.context['artist'].pk, 1)


    def test_get_artist_that_does_not_exist_returns_404(self):
        response = self.client.get(reverse('artist_detail', kwargs={'artist_pk' : 10} ))
        self.assertEqual(response.status_code, 404)


    def test_venues_played_at_most_recent_shows_first(self):
        ''' For each artist, display a list of venues they have played shows at '''

        # Artist 1 (REM) has played at venue 2 (Turf Club) on two dates

        url = reverse('venues_for_artist', kwargs={'artist_pk':1})
        response = self.client.get(url)
        shows = list(response.context['shows'].all())
        show1, show2 = shows[0], shows[1]
        self.assertEqual(2, len(shows))

        self.assertEqual(show1.artist.name, 'REM')
        self.assertEqual(show1.venue.name, 'The Turf Club')

        expected_date = datetime.datetime(2017, 2, 2, 0, 0, tzinfo=timezone.utc)
        self.assertEqual(21600, (show1.show_date - expected_date).total_seconds())

        self.assertEqual(show2.artist.name, 'REM')
        self.assertEqual(show2.venue.name, 'The Turf Club')
        expected_date = datetime.datetime(2017, 1, 2, 0, 0, tzinfo=timezone.utc)
        self.assertEqual(21600, (show2.show_date - expected_date).total_seconds())

        # Artist 2 (ACDC) has played at venue 1 (First Ave)

        url = reverse('venues_for_artist', kwargs={'artist_pk':2})
        response = self.client.get(url)
        shows = list(response.context['shows'].all())
        show1 = shows[0]
        self.assertEqual(1, len(shows))

        self.assertEqual(show1.artist.name, 'ACDC')
        self.assertEqual(show1.venue.name, 'First Avenue')
        expected_date = datetime.datetime(2017, 1, 21, 0, 0, tzinfo=timezone.utc)
        self.assertEqual(21600, (show1.show_date - expected_date).total_seconds())

        # Artist 3 , no shows

        url = reverse('venues_for_artist', kwargs={'artist_pk':3})
        response = self.client.get(url)
        shows = list(response.context['shows'].all())
        self.assertEqual(0, len(shows))



class TestVenues(TestCase):

        fixtures = ['testing_venues', 'testing_artists', 'testing_shows']

        def test_with_venues_displays_all_alphabetically(self):
            response = self.client.get(reverse('venue_list'))

            # .* matches 0 or more of any character. Test to see if
            # these names are present, in the right order

            regex = '.*First Avenue.*Target Center.*The Turf Club.*'
            response_text = str(response.content)

            self.assertTrue(re.match(regex, response_text))

            self.assertEqual(len(response.context['venues']), 3)
            self.assertTemplateUsed(response, 'lmn/venues/venue_list.html')


        def test_venue_search_clear_link(self):
            response = self.client.get( reverse('venue_list') , {'search_name' : 'Fine Line'} )

            # There is a clear link, it's url is the main venue page
            all_venues_url = reverse('venue_list')
            self.assertContains(response, all_venues_url)


        def test_venue_search_no_search_results(self):
            response = self.client.get( reverse('venue_list') , {'search_name' : 'Fine Line'} )
            self.assertNotContains(response, 'First Avenue')
            self.assertNotContains(response, 'Turf Club')
            self.assertNotContains(response, 'Target Center')
            # Check the length of venues list is 0
            self.assertEqual(len(response.context['venues']), 0)
            self.assertTemplateUsed(response, 'lmn/venues/venue_list.html')


        def test_venue_search_partial_match_search_results(self):
            response = self.client.get(reverse('venue_list'), {'search_name' : 'c'})
            # Should be two responses, Yes and REM
            self.assertNotContains(response, 'First Avenue')
            self.assertContains(response, 'Turf Club')
            self.assertContains(response, 'Target Center')
            # Check the length of venues list is 2
            self.assertEqual(len(response.context['venues']), 2)
            self.assertTemplateUsed(response, 'lmn/venues/venue_list.html')


        def test_venue_search_one_search_result(self):

            response = self.client.get(reverse('venue_list'), {'search_name' : 'Target'} )
            self.assertNotContains(response, 'First Avenue')
            self.assertNotContains(response, 'Turf Club')
            self.assertContains(response, 'Target Center')
            # Check the length of venues list is 1
            self.assertEqual(len(response.context['venues']), 1)
            self.assertTemplateUsed(response, 'lmn/venues/venue_list.html')


        def test_venue_detail(self):

            ''' venue 1 details displayed in correct template '''
            # kwargs to fill in parts of url. Not get or post params

            response = self.client.get(reverse('venue_detail', kwargs={'venue_pk' : 1} ))
            self.assertContains(response, 'First Avenue')
            self.assertEqual(response.context['venue'].name, 'First Avenue')
            self.assertEqual(response.context['venue'].pk, 1)

            self.assertTemplateUsed(response, 'lmn/venues/venue_detail.html')


        def test_get_venue_that_does_not_exist_returns_404(self):
            response = self.client.get(reverse('venue_detail', kwargs={'venue_pk' : 10} ))
            self.assertEqual(response.status_code, 404)


        def test_artists_played_at_venue_most_recent_first(self):
            # Artist 1 (REM) has played at venue 2 (Turf Club) on two dates

            url = reverse('artists_at_venue', kwargs={'venue_pk':2})
            response = self.client.get(url)
            shows = list(response.context['shows'].all())
            show1, show2 = shows[0], shows[1]
            self.assertEqual(2, len(shows))

            self.assertEqual(show1.artist.name, 'REM')
            self.assertEqual(show1.venue.name, 'The Turf Club')

            expected_date = datetime.datetime(2017, 2, 2, 0, 0, tzinfo=timezone.utc)
            self.assertEqual(21600, (show1.show_date - expected_date).total_seconds())

            self.assertEqual(show2.artist.name, 'REM')
            self.assertEqual(show2.venue.name, 'The Turf Club')
            expected_date = datetime.datetime(2017, 1, 2, 0, 0, tzinfo=timezone.utc)
            self.assertEqual(21600, (show2.show_date - expected_date).total_seconds())

            # Artist 2 (ACDC) has played at venue 1 (First Ave)

            url = reverse('artists_at_venue', kwargs={'venue_pk':1})
            response = self.client.get(url)
            shows = list(response.context['shows'].all())
            show1 = shows[0]
            self.assertEqual(1, len(shows))

            self.assertEqual(show1.artist.name, 'ACDC')
            self.assertEqual(show1.venue.name, 'First Avenue')
            expected_date = datetime.datetime(2017, 1, 21, 0, 0, tzinfo=timezone.utc)
            self.assertEqual(21600, (show1.show_date - expected_date).total_seconds())

            # Venue 3 has not had any shows

            url = reverse('artists_at_venue', kwargs={'venue_pk':3})
            response = self.client.get(url)
            shows = list(response.context['shows'].all())
            self.assertEqual(0, len(shows))


        def test_correct_template_used_for_venues(self):
            # Show all
            response = self.client.get(reverse('venue_list'))
            self.assertTemplateUsed(response, 'lmn/venues/venue_list.html')

            # Search with matches
            response = self.client.get(reverse('venue_list'), {'search_name' : 'First'} )
            self.assertTemplateUsed(response, 'lmn/venues/venue_list.html')
            # Search no matches
            response = self.client.get(reverse('venue_list'), {'search_name' : 'Non Existant Venue'})
            self.assertTemplateUsed(response, 'lmn/venues/venue_list.html')

            # Venue detail
            response = self.client.get(reverse('venue_detail', kwargs={'venue_pk':1}))
            self.assertTemplateUsed(response, 'lmn/venues/venue_detail.html')

            response = self.client.get(reverse('artists_at_venue', kwargs={'venue_pk':1}))
            self.assertTemplateUsed(response, 'lmn/artists/artist_list_for_venue.html')



class TestAddNoteUnauthentictedUser(TestCase):

    fixtures = [ 'testing_artists', 'testing_venues', 'testing_shows' ]  # Have to add artists and venues because of foreign key constrains in show

    def test_add_note_unauthenticated_user_redirects_to_login(self):
        response = self.client.get( '/notes/add/1/', follow=True)  # Use reverse() if you can, but not required.
        # Should redirect to login; which will then redirect to the notes/add/1 page on success.
        self.assertRedirects(response, '/accounts/login/?next=/notes/add/1/')


class TestAddNotesWhenUserLoggedIn(TestCase):
    fixtures = ['testing_users', 'testing_artists', 'testing_shows', 'testing_venues', 'testing_notes']

    def setUp(self):
        user = User.objects.first()
        self.client.force_login(user)


    def test_save_note_for_non_existent_show_is_error(self):
        new_note_url = reverse('new_note', kwargs={'show_pk':100})
        response = self.client.post(new_note_url)
        self.assertEqual(response.status_code, 404)


    def test_can_save_new_note_for_show_blank_data_is_error(self):

        initial_note_count = Note.objects.count()

        new_note_url = reverse('new_note', kwargs={'show_pk':1})

        # No post params
        response = self.client.post(new_note_url, follow=True)
        # No note saved, should show same page
        self.assertTemplateUsed('lmn/notes/new_note.html')

        # no title
        response = self.client.post(new_note_url, {'text':'blah blah' }, follow=True)
        self.assertTemplateUsed('lmn/notes/new_note.html')

        # no text
        response = self.client.post(new_note_url, {'title':'blah blah' }, follow=True)
        self.assertTemplateUsed('lmn/notes/new_note.html')

        # nothing added to database
        self.assertEqual(Note.objects.count(), initial_note_count)   # 2 test notes provided in fixture, should still be 2


    def test_add_note_database_updated_correctly(self):

        initial_note_count = Note.objects.count()

        new_note_url = reverse('new_note', kwargs={'show_pk':1})

        response = self.client.post(new_note_url, {'text':'ok', 'title':'blah blah' }, follow=True)

        # Verify note is in database
        new_note_query = Note.objects.filter(text='ok', title='blah blah')
        self.assertEqual(new_note_query.count(), 1)

        # And one more note in DB than before
        self.assertEqual(Note.objects.count(), initial_note_count + 1)

        # Date correct?
        #now = datetime.datetime.today()
        #posted_date = new_note_query.first().posted_date
        #self.assertEqual(now.date(), posted_date.date())  # TODO check time too


    def test_redirect_to_user_profile_after_save(self):

        initial_note_count = Note.objects.count()

        new_note_url = reverse('new_note', kwargs={'show_pk':1})
        response = self.client.post(new_note_url, {'text':'ok', 'title':'blah blah' }, follow=True)
        new_note = Note.objects.filter(text='ok', title='blah blah').first()

        self.assertRedirects(response, reverse('user_profile' , kwargs = {'user_pk': 1}))
        

class TestDeleteNote(TestCase):
    #populate test db with info 
    fixtures = [ 'testing_users', 'testing_artists', 'testing_venues', 'testing_shows', 'testing_notes' ]  # Have to add artists and venues because of foreign key constrains in show
    
    def setUp(self): #this method needed because before delete, user must be owner of note is tested
            user = User.objects.first()
            self.client.force_login(user)

    def test_delete_own_note(self):
        #delete note with note_pk of 1 (user1)
        response = self.client.post(reverse('delete_note', args=(1,)), follow=True)
        note_1 = Note.objects.filter(pk=1).first()
        self.assertIsNone(note_1) #after deletion, there will be no note with pk of 1

    def test_delete_someone_else_note_not_auth(self):
        #user 1 trying to delete note of user 2
        response = self.client.post(reverse('delete_note', args=(2,)), follow=True)
        self.assertEqual(403, response.status_code) #403 is forbidden
        note_2 = Note.objects.get(pk=2)
        self.assertIsNotNone(note_2) #note is still in dbase

    def test_delete_note_database_updated_correctly(self):
        initial_note_count = Note.objects.count() 
        #delete one note
        response = self.client.post(reverse('delete_note', args=(1,)), follow=True)
        self.assertEqual(Note.objects.count(), initial_note_count -1)




class TestUserProfile(TestCase):
    fixtures = [ 'testing_users', 'testing_artists', 'testing_venues', 'testing_shows', 'testing_notes' ]  # Have to add artists and venues because of foreign key constrains in show

    # verify correct list of reviews for a user
    def test_user_profile_show_list_of_their_notes(self):
        # get user profile for user 2. Should have 2 reviews for show 1 and 2.
        response = self.client.get(reverse('user_profile', kwargs={'user_pk':2}))
        notes_expected = list(Note.objects.filter(user=2).order_by('-posted_date'))
        notes_provided = list(response.context['notes'])
        self.assertTemplateUsed('lmn/users/user_profile.html')
        self.assertEqual(notes_expected, notes_provided)

        # test notes are in date order, most recent first.
        # Note PK 3 should be first, then PK 2
        first_note = response.context['notes'][0]
        self.assertEqual(first_note.pk, 3)

        second_note = response.context['notes'][1]
        self.assertEqual(second_note.pk, 2)


    def test_user_with_no_notes(self):
        response = self.client.get(reverse('user_profile', kwargs={'user_pk':3}))
        self.assertFalse(response.context['notes'])


    def test_username_shown_on_profile_page(self):
        # A string "username's notes" is visible
        response = self.client.get(reverse('user_profile', kwargs={'user_pk':1}))
        self.assertContains(response, 'alice\'s notes')
        
        response = self.client.get(reverse('user_profile', kwargs={'user_pk':2}))
        self.assertContains(response, 'bob\'s notes')


    def test_correct_user_name_shown_different_profiles(self):
        logged_in_user = User.objects.get(pk=2)
        self.client.force_login(logged_in_user)  # bob
        response = self.client.get(reverse('user_profile', kwargs={'user_pk':2}))
        self.assertContains(response, 'You are logged in, <a href="/user/profile/2/">bob</a>.')
        
        # Same message on another user's profile. Should still see logged in message 
        # for currently logged in user, in this case, bob
        response = self.client.get(reverse('user_profile', kwargs={'user_pk':3}))
        self.assertContains(response, 'You are logged in, <a href="/user/profile/2/">bob</a>.')
        

class TestNotes(TestCase):
    fixtures = [ 'testing_users', 'testing_artists', 'testing_venues', 'testing_shows', 'testing_notes' ]  # Have to add artists and venues because of foreign key constrains in show

    def test_latest_notes(self):
        response = self.client.get(reverse('latest_notes'))
        expected_notes = list(Note.objects.all())
        # Should be note 3, then 2, then 1
        context = response.context['notes']
        first, second, third = context[0], context[1], context[2]
        self.assertEqual(first.pk, 3)
        self.assertEqual(second.pk, 2)
        self.assertEqual(third.pk, 1)


    def test_notes_for_show_view(self):
        # Verify correct list of notes shown for a Show, most recent first
        # Show 1 has 2 notes with PK = 2 (most recent) and PK = 1
        response = self.client.get(reverse('notes_for_show', kwargs={'show_pk':1}))
        context = response.context['notes']
        first, second = context[0], context[1]
        self.assertEqual(first.pk, 2)
        self.assertEqual(second.pk, 1)


    def test_correct_templates_uses_for_notes(self):
        response = self.client.get(reverse('latest_notes'))
        self.assertTemplateUsed(response, 'lmn/notes/note_list.html')

        response = self.client.get(reverse('note_detail', kwargs={'note_pk':1}))
        self.assertTemplateUsed(response, 'lmn/notes/note_detail.html')

        response = self.client.get(reverse('notes_for_show', kwargs={'show_pk':1}))
        self.assertTemplateUsed(response, 'lmn/notes/notes_for_show.html')

        # Log someone in
        self.client.force_login(User.objects.first())
        response = self.client.get(reverse('new_note', kwargs={'show_pk':1}))
        self.assertTemplateUsed(response, 'lmn/notes/new_note.html')
  

class TestSearchNotes(TestCase):
    fixtures = ['testing_artists', 'testing_venues', 'testing_shows','testing_notes', 'testing_users']
   
    def test_note_search_matches(self):
        
        response = self.client.get(reverse('latest_notes'), {'search_term' :'super'} )
        self.assertEqual(len(response.context['notes']), 1)
        notes = list(response.context['notes'].all())
        note1 = notes[0]
        self.assertEqual(note1.text, 'woo hoo!')


    def test_note_search_not_matches(self):
        response = self.client.get(reverse('latest_notes'), {'search_term' :'best'} )
        self.assertEqual(len(response.context['notes']), 0)
       

    def test_note_search_caseinsensitive_matches(self):
        response = self.client.get(reverse('latest_notes'), {'search_term' :'SUPER'} )
        self.assertEqual(len(response.context['notes']), 1)
        notes = list(response.context['notes'].all())
        note1 = notes[0]
        self.assertEqual(note1.text, 'woo hoo!')
    
    def test_note_search_partial_match_search_results(self):
        response = self.client.get(reverse('latest_notes'), {'search_term' : 'o'})
        # Should be two responses, Yes and REM
        self.assertNotContains(response, 'super')
        self.assertContains(response, 'awesome')
        self.assertContains(response, 'ok')
        # Check the length of notes list is 2
        self.assertEqual(len(response.context['notes']), 2)
        self.assertTemplateUsed(response, 'lmn/notes/note_list.html')


class TestUserAuthentication(TestCase):

    ''' Some aspects of registration (e.g. missing data, duplicate username) covered in test_forms '''
    ''' Currently using much of Django's built-in login and registration system'''

    def test_user_registration_logs_user_in(self):
        response = self.client.post(reverse('register'), {'username':'sam12345', 'email':'sam@sam.com', 'password1':'feRpj4w4pso3az', 'password2':'feRpj4w4pso3az', 'first_name':'sam', 'last_name' : 'sam'}, follow=True)

        # Assert user is logged in - one way to do it...
        user = auth.get_user(self.client)
        self.assertEqual(user.username, 'sam12345')

        # This works too. Don't need both tests, added this one for reference.
        # sam12345 = User.objects.filter(username='sam12345').first()
        # auth_user_id = int(self.client.session['_auth_user_id'])
        # self.assertEqual(auth_user_id, sam12345.pk)


    def test_user_registration_redirects_to_correct_page(self):
        # TODO If user is browsing site, then registers, once they have registered, they should
        # be redirected to the last page they were at, not the homepage.
        response = self.client.post(reverse('register'), {'username':'sam12345', 'email':'sam@sam.com', 'password1':'feRpj4w4pso3az@1!2', 'password2':'feRpj4w4pso3az@1!2', 'first_name':'sam', 'last_name' : 'sam'}, follow=True)
        new_user = authenticate(username='sam12345', password='feRpj4w4pso3az@1!2')
        self.assertRedirects(response, reverse('user_profile', kwargs={"user_pk": new_user.pk}))   
        self.assertContains(response, 'sam12345')  # page has user's name on it


class TestNoteDetail(TestCase):
    #load data into database
    fixtures = [ 'testing_users', 'testing_artists', 'testing_venues', 'testing_shows', 'testing_notes' ]  # Have to add artists and venues because of foreign key constrains in show
 
    def setUp(self):
        user = User.objects.first() #retrieve user1 and log them in
        self.client.force_login(user)


    def test_modify_note_database_updated_correctly(self):
        #note w pk of 1 currently has title= ok and text = kinda ok  
        #get initial count of notes to make sure note was edited and overwritten, not new one created
        initial_note_count = Note.objects.count()
        
        #update note w/ pk=1
        response = self.client.post('/notes/1/edit', {'title': 'okok', 'text': 'melodic'})

        #retrieve that updated note
        updated_note_1 = Note.objects.get(pk=1)

       #  no more notes in DB than before
        self.assertEqual(Note.objects.count(), initial_note_count )
        # was the db updated?
        self.assertEqual('melodic', updated_note_1.text)
        self.assertEqual('okok', updated_note_1.title)
        

    def test_modify_someone_elses_note_detail_not_authorized(self):#note pk_3 belongs to user 2, not user 1
        #note w/pk=2 belongs to user2; setup logs in user 1
        response = self.client.post('/notes/2/edit', {'title': 'okok', 'text': 'melodic'})
        note_2 = Note.objects.get(pk=2)

        self.assertEqual(403, response.status_code)  #403 = forbidden - this is not owner of this note
        #make sure note 2 not changed
        self.assertEqual('yay!' , note_2.text)


class TestImageUpload(TestCase):

    fixtures = ['testing_users', 'testing_artists', 'testing_venues', 'testing_shows', 'testing_notes' ]    

    def setUp(self):
        user = User.objects.get(pk=1)
        self.client.force_login(user)
        self.MEDIA_ROOT = tempfile.mkdtemp()

    def create_temp_image_file(self):
        handle, tmp_img_file = tempfile.mkstemp(suffix='.jpg')
        img = Image.new('RGB', (10, 10) )
        img.save(tmp_img_file, format='JPEG')
        return tmp_img_file
    # User tests uploading new along with note
    def test_upload_new_image_for_own_note(self):
        
        img_file_path = self.create_temp_image_file()
        with self.settings(MEDIA_ROOT=self.MEDIA_ROOT):
        
            with open(img_file_path, 'rb') as img_file:
                resp = self.client.post(reverse('new_note', kwargs={'show_pk': 1} ), {'photo': img_file }, follow=True)               
                self.assertEqual(200, resp.status_code)
                note_1 = Note.objects.get(pk=1)
            
                self.assertIsNotNone(note_1.photo)
               
    # note will be deleted along with picture 

    def test_delete_note_with_image_image_deleted(self):
        
        img_file_path = self.create_temp_image_file()
        with self.settings(MEDIA_ROOT=self.MEDIA_ROOT):    
            with open(img_file_path, 'rb') as img_file:
                resp = self.client.post(reverse('note_detail', kwargs={'note_pk': 1} ), {'photo': img_file }, follow=True)
                
                self.assertEqual(200, resp.status_code)

                note_1 = Note.objects.get(pk=1)
                img_file_name = os.path.basename(img_file_path)
                
                uploaded_file_path = os.path.join(self.MEDIA_ROOT, 'user_images', img_file_name)

                note_1 = Note.objects.get(pk=1)
                note_1.delete()

                self.assertFalse(os.path.exists(uploaded_file_path))

    # User won't be able to upload a picture for someone else's note 
    def test_upload_image_for_someone_else_note(self):

        with self.settings(MEDIA_ROOT=self.MEDIA_ROOT): 
            img_file = self.create_temp_image_file()
            with open(img_file, 'rb') as image:
                resp = self.client.post(reverse('note_detail', kwargs={'note_pk':2 } ), {'photo': image }, follow=True)
                self.assertEqual(403, resp.status_code)
                note_2 = Note.objects.get(pk=2)
                self.assertFalse(note_2.photo)  
