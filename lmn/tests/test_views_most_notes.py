from ..models import Venue, Artist, Note, Show
from django.urls import reverse
from django.test import TestCase
from ..models import Artist, Venue, Show, Note, User
from django.utils import timezone


class TestTopShows(TestCase):

    def setUp(self):
        user = User(username='user', password='password')
        user.save()

        # Set up provides sample data for your test
        # Data destroyed after the test is done
        # Creating 5 Shows, Artist, Notes and Venues 
        for i in range(5):
            artist = Artist(name=f'Number{i+1}')
            artist.save()
            venue = Venue(name=f'venue{i+1}', city=f'city{i+1}', state=f'state{i+1}')
            venue.save()
            show = Show(show_date=timezone.now(), artist=Artist(id=i+1), venue=Venue(i+1))
            show.save()
            note = Note(show=Show(f'{i+1}'), user=User(id=1), title=f'title{i+2}', text=f'text{i+1}') 
            note.save()

        # Creating more note for show 1
        for i in range(4):
            more_note = Note(show=Show(f'{1}'), user=User(id=1), title=f'title{2}', text=f'text{2}')
            more_note.save()

        # Creating more note for show 2
        for i in range(3):
            more_note = Note(show=Show(f'{2}'), user=User(id=1), title=f'title{2}', text=f'text{2}')
            more_note.save()

        # Creating more note for show 3
        for i in range(2):
            more_note = Note(show=Show(f'{3}'), user=User(id=1), title=f'title{2}', text=f'text{2}')
            more_note.save()

        # Creating more note for show 4
        for i in range(1):
            more_note = Note(show=Show(f'{4}'), user=User(id=1), title=f'title{2}', text=f'text{2}')
            more_note.save()

    # Testing shows in chronological order from show with most to least notes
    def test_first_show_5_notes(self):

        response = self.client.get(reverse('show_most_notes'))
        
        # list of shows expected shows
        show1 = Show.objects.get(pk=1)
        show2 = Show.objects.get(pk=2)
        show3 = Show.objects.get(pk=3)
        show4 = Show.objects.get(pk=4)
        show5 = Show.objects.get(pk=5)
        expected_shows = [show1, show2, show3, show4, show5]
        
        # Shows displayed in the list
        shows_provided = list(response.context['shows'])
        
        self.assertEqual(shows_provided, expected_shows)

        self.assertTemplateUsed(response, 'lmn/notes/show_most_notes.html')


class TestShowWithOutNotes(TestCase):

    def setUp(self):
        user = User(username='user', password='password')
        user.save()

        # Set up provides sample data for your test
        # Data will be destroyed after the test.
        
        for i in range(4):
            artist = Artist(name=f'Number{i+1}')
            artist.save()
            venue = Venue(name=f'venue{i+1}', city=f'city{i+1}', state=f'state{i+1}')
            venue.save()
            show = Show(show_date=timezone.now(), artist=Artist(id=i+1), venue=Venue(i+1))
            show.save()
            note = Note(show=Show(f'{i+1}'), user=User(id=1), title=f'title{i+2}', text=f'text{i+1}') 
            note.save()

        # Creating more note for show 1 
        for i in range(4):
            more_note = Note(show=Show(f'{1}'), user=User(id=1), title=f'title{2}', text=f'text{2}')
            more_note.save()

        # Creating more note for show 2
        for i in range(3):
            more_note = Note(show=Show(f'{2}'), user=User(id=1), title=f'title{2}', text=f'text{2}')
            more_note.save()

        # Creating more note for show 3 
        for i in range(2):
            more_note = Note(show=Show(f'{3}'), user=User(id=1), title=f'title{2}', text=f'text{2}')
            more_note.save()
        
        # Adding an extra show without notes to test a show without note.
        show = Show(show_date=timezone.now(), artist=Artist(id=1), venue=Venue(id=1))
        show.save()
    
    #Testing the fifth show that has no notes 
    def test_show_without_notes(self):
  
        response = self.client.get(reverse('show_most_notes'))
        
        # list of expected shows 
        show1 = Show.objects.get(pk=1)
        show2 = Show.objects.get(pk=3)
        show3 = Show.objects.get(pk=2)
        show4 = Show.objects.get(pk=4)
        expected_shows = [show1, show3, show2, show4]
        
        # Shows displayed.
        shows_provided = list(response.context['shows'])
        
        self.assertEqual(expected_shows, shows_provided)



class TestShowSameNumbersOfNotes(TestCase):


    def setUp(self):
        user = User(username='user', password='password')
        user.save()

        # Set up provides sample data for your test
        # sample data will be destroyed after test
        for i in range(5):
            artist = Artist(name=f'Number{i+1}')
            artist.save()
            venue = Venue(name=f'venue{i+1}', city=f'city{i+1}', state=f'state{i+1}')
            venue.save()
            show = Show(show_date=timezone.now(), artist=Artist(id=i+1), venue=Venue(i+1))
            show.save()
            note = Note(show=Show(f'{i+1}'), user=User(id=1), title=f'title{2}', text=f'text{2}')
            note.save()
        
        # Adding 4 more notes to show 1
        for i in range(4):
            more_note = Note(show=Show(f'{1}'), user=User(id=1), title=f'title{2}', text=f'text{2}')
            more_note.save()

        # Adding 3 more notes to show 2
        for i in range(3):
            more_note = Note(show=Show(f'{2}'), user=User(id=1), title=f'title{2}', text=f'text{2}')
            more_note.save()
        
    # Test three shows with the same number of notes and display all three in the list 
    def test_show_with_same_number_of_notes(self):

        response = self.client.get(reverse('show_most_notes'))
        
        show1 = Show.objects.get(pk=1)
        show2 = Show.objects.get(pk=2)
        show3 = Show.objects.get(pk=5)
        show4 = Show.objects.get(pk=4)
        show5 = Show.objects.get(pk=3)   
        expected_shows = [show1, show2, show5, show4, show3]
        
        shows_provided = list(response.context['shows'])  
        self.assertEqual(shows_provided, expected_shows)

    # Testing user to authorized see show with most notes list
    def test_authorized_user_can_see_list_of_most_notes(self):

         user = User.objects.create_user("Paul","acero@hotmail.com", "password")
         self.client.force_login(user=user)
         response = self.client.get(reverse("login"))
         self.assertEqual(response.status_code, 200)
