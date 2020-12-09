from django.test import TestCase
from lmnop_project import helpers
from lmn.models import Artist, Venue, Show, Note, User
from datetime import datetime
from django.utils import timezone




# test will take a small sample of data using the pg_records function and assertequals
class TestListWithPageData(TestCase):

    # setUp provides sample data to test data base. Data is created everytime tests are run and test db is destroyed
    # after tests are complete
    def setUp(self):
        user = User(username='user', password='password')
        user.save()
        for i in range(3):
            artist = Artist(name=f'Number{i+1}')
            artist.save()
            venue = Venue(name=f'venue{i+1}', city=f'city{i+1}', state=f'state{i+1}')
            venue.save()
            # timezone will check the django settings to get the appropriate time for now
            show = Show(show_date=timezone.now(), artist=Artist(id=i+1), venue=Venue(i+1))
            show.save()
            note = Note(show=Show(f'{i+1}'), user=User(id=1), title=f'title{i+1}', text=f'text{i+1}')
            note.save()

    # check that names returned from db are correct on first loaded page
    def test_first_page_correct_entries_artist(self):
        artists = Artist.objects.all().order_by('name')
        paged_list = helpers.pg_records(1, artists, 2)
        self.assertEqual(artists[0].name, paged_list[0].name)
        self.assertEqual(artists[1].name, paged_list[1].name)

    # check that names returned from db are correct on second loaded page
    def test_second_page_correct_entries_artist(self):
        artists = Artist.objects.all().order_by('name')
        paged_list = helpers.pg_records(2, artists, 2)
        self.assertEqual(artists[2].name, paged_list[0].name)

    # check that the desired number of items are displayed per page
    def test_correct_number_of_items_returned_page_one_artist(self):
        artists = Artist.objects.all().order_by('name')
        paged_list = helpers.pg_records(1, artists, 2)
        self.assertEqual(len(paged_list), 2)

    # check that the desired number of items are displayed per page
    def test_correct_number_of_items_returned_page_two_artist(self):
        artists = Artist.objects.all().order_by('name')
        paged_list = helpers.pg_records(2, artists, 2)
        self.assertEqual(len(paged_list), 1)

    # compares each note attribute for each note object on page one to expected positions in object list from db
    def test_first_page_correct_entries_note(self):
        notes = Note.objects.all().order_by('id')
        paged_list = helpers.pg_records(1, notes, 2)
        self.assertEqual(notes[0].id, paged_list[0].id)
        self.assertEqual(notes[1].id, paged_list[1].id)
        self.assertEqual(notes[0].title, paged_list[0].title)
        self.assertEqual(notes[1].title, paged_list[1].title)
        self.assertEqual(notes[0].text, paged_list[0].text)
        self.assertEqual(notes[1].text, paged_list[1].text)
        self.assertEqual(notes[0].show_id, paged_list[0].show_id)
        self.assertEqual(notes[1].show_id, paged_list[1].show_id)
        self.assertEqual(notes[0].user_id, paged_list[0].user_id)
        self.assertEqual(notes[1].user_id, paged_list[1].user_id)
        self.assertEqual(notes[0].posted_date, paged_list[0].posted_date)
        self.assertEqual(notes[1].posted_date, paged_list[1].posted_date)

    # compares each note attribute for each note object on page two to expected positions in object list from db
    def test_second_page_correct_entries_note(self):
        notes = Note.objects.all().order_by('id')
        paged_list = helpers.pg_records(2, notes, 2)
        self.assertEqual(notes[2].id, paged_list[0].id)
        self.assertEqual(notes[2].title, paged_list[0].title)
        self.assertEqual(notes[2].text, paged_list[0].text)
        self.assertEqual(notes[2].show_id, paged_list[0].show_id)
        self.assertEqual(notes[2].user_id, paged_list[0].user_id)
        self.assertEqual(notes[2].posted_date, paged_list[0].posted_date)

    # check that the desired number of items are displayed per page
    def test_correct_number_of_items_returned_page_one_note(self):
        notes = Note.objects.all().order_by('id')
        paged_list = helpers.pg_records(1, notes, 2)
        self.assertEqual(len(paged_list), 2)

    # check that the desired number of items are displayed per page
    def test_correct_number_of_items_returned_page_two_note(self):
        notes = Note.objects.all().order_by('id')
        paged_list = helpers.pg_records(2, notes, 2)
        self.assertEqual(len(paged_list), 1)

    # test to ensure that when no valid page number is supplied page number is set to 1
    def test_no_page_number_supplied(self):
        notes = Note.objects.all().order_by('id')
        paged_list_exists = helpers.pg_records(1, notes, 2)
        paged_list_no_page_supplied = helpers.pg_records('', notes, 2)
        self.assertEquals(str(paged_list_exists), str(paged_list_no_page_supplied))
        paged_list_no_page_supplied = helpers.pg_records('j', notes, 2)
        self.assertEquals(str(paged_list_exists), str(paged_list_no_page_supplied))
        paged_list_no_page_supplied = helpers.pg_records(45.6, notes, 2)
        self.assertEquals(str(paged_list_exists), str(paged_list_no_page_supplied))
        paged_list_no_page_supplied = helpers.pg_records(u"\2191", notes, 2)
        self.assertEquals(str(paged_list_exists), str(paged_list_no_page_supplied))


    # check that goes to last page when page entered is higher than number of existing pages
    def test_page_number_higher_than_exists(self):
        artists = Artist.objects.all().order_by('name')
        paged_list_exists = helpers.pg_records(2, artists, 2)
        paged_list_out_of_bounds = helpers.pg_records(4000, artists, 2)
        self.assertEquals(str(paged_list_exists), str(paged_list_out_of_bounds))
        paged_list_out_of_bounds = helpers.pg_records(10000, artists, 2)
        self.assertEquals(str(paged_list_exists), str(paged_list_out_of_bounds))
        paged_list_out_of_bounds = helpers.pg_records(50000, artists, 2)
        self.assertEquals(str(paged_list_exists), str(paged_list_out_of_bounds))
        paged_list_out_of_bounds = helpers.pg_records(100000, artists, 2)
        self.assertEquals(str(paged_list_exists), str(paged_list_out_of_bounds))

    # test that when negative numbers are supplied as the page number that page by default is set to 1
    def test_page_number_lower_than_exists(self):
        artists = Artist.objects.all().order_by('name')
        paged_list_exists = helpers.pg_records(1, artists, 2)
        paged_list_out_of_bounds = helpers.pg_records(-5, artists, 2)
        self.assertEquals(str(paged_list_exists), str(paged_list_out_of_bounds))
        paged_list_out_of_bounds = helpers.pg_records(-10, artists, 2)
        self.assertEquals(str(paged_list_exists), str(paged_list_out_of_bounds))
        paged_list_out_of_bounds = helpers.pg_records(-100, artists, 2)
        self.assertEquals(str(paged_list_exists), str(paged_list_out_of_bounds))
        paged_list_out_of_bounds = helpers.pg_records(-1000, artists, 2)
        self.assertEquals(str(paged_list_exists), str(paged_list_out_of_bounds))

