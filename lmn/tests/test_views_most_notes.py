from django.http import response
from lmn.views.views_most_notes import show_most_notes
from django.shortcuts import render, redirect, get_object_or_404
from ..models import Venue, Artist, Note, Show
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from django.db.models.functions import Lower

from django.test import TestCase
from ..models import Artist, Venue, Show, Note, User
from datetime import datetime
from django.utils import timezone
from django.db.models import Count




class TestTopShows(TestCase):


    def setUp(self):
        user = User(username='user', password='password')
        user.save()

        # Set up provides sample data for your test
        for i in range(5):
            artist = Artist(name=f'Number{i+1}')
            artist.save()
            venue = Venue(name=f'venue{i+1}', city=f'city{i+1}', state=f'state{i+1}')
            venue.save()
            show = Show(show_date=timezone.now(), artist=Artist(id=i+1), venue=Venue(i+1))
            show.save()
            note = Note(show=Show(f'{i+1}'), user=User(id=1), title=f'title{i+2}', text=f'text{i+1}') 
            note.save()

        for i in range(4):
            more_note = Note(show=Show(f'{1}'), user=User(id=1), title=f'title{2}', text=f'text{2}')
            more_note.save()

        for i in range(3):
            more_note = Note(show=Show(f'{2}'), user=User(id=1), title=f'title{2}', text=f'text{2}')
            more_note.save()

        for i in range(2):
            more_note = Note(show=Show(f'{3}'), user=User(id=1), title=f'title{2}', text=f'text{2}')
            more_note.save()

        for i in range(1):
            more_note = Note(show=Show(f'{4}'), user=User(id=1), title=f'title{2}', text=f'text{2}')
            more_note.save()


    def test_first_show_5_notes(self):

        
        
        response = self.client.get(reverse('show_most_notes'))
        
        # list of shows 
        show1 = Show.objects.get(pk=1)
        show2 = Show.objects.get(pk=2)
        show3 = Show.objects.get(pk=3)
        show4 = Show.objects.get(pk=4)
        show5 = Show.objects.get(pk=5)
        expected_shows = [show1, show2, show3, show4, show5]
        

        shows_provided = list(response.context['shows'])
        
        self.assertEqual(shows_provided, expected_shows)

        self.assertTemplateUsed(response, 'lmn/notes/show_most_notes.html')





class TestShowWithOutNotes(TestCase):


    def setUp(self):
        user = User(username='user', password='password')
        user.save()

        # Set up provides sample data for your test
        for i in range(4):
            artist = Artist(name=f'Number{i+1}')
            artist.save()
            venue = Venue(name=f'venue{i+1}', city=f'city{i+1}', state=f'state{i+1}')
            venue.save()
            show = Show(show_date=timezone.now(), artist=Artist(id=i+1), venue=Venue(i+1))
            show.save()
            note = Note(show=Show(f'{i+1}'), user=User(id=1), title=f'title{i+2}', text=f'text{i+1}') 
            note.save()

        for i in range(4):
            more_note = Note(show=Show(f'{1}'), user=User(id=1), title=f'title{2}', text=f'text{2}')
            more_note.save()

        for i in range(3):
            more_note = Note(show=Show(f'{2}'), user=User(id=1), title=f'title{2}', text=f'text{2}')
            more_note.save()

        for i in range(2):
            more_note = Note(show=Show(f'{3}'), user=User(id=1), title=f'title{2}', text=f'text{2}')
            more_note.save()

        show = Show(show_date=timezone.now(), artist=Artist(id=1), venue=Venue(id=1))
        show.save()


    def test_show_without_notes(self):

        
        
        response = self.client.get(reverse('show_most_notes'))
        
        # list of shows 
        show1 = Show.objects.get(pk=1)
        show2 = Show.objects.get(pk=2)
        show3 = Show.objects.get(pk=3)
        show4 = Show.objects.get(pk=4)

        
        
        
        expected_shows = [show1, show2, show3, show4]
        

        shows_provided = list(response.context['shows'])
        
        self.assertEqual(expected_shows, shows_provided)



class TestShowSameNumbersOfNotes(TestCase):


    def setUp(self):
        user = User(username='user', password='password')
        user.save()

        # Set up provides sample data for your test
        for i in range(5):
            artist = Artist(name=f'Number{i+1}')
            artist.save()
            venue = Venue(name=f'venue{i+1}', city=f'city{i+1}', state=f'state{i+1}')
            venue.save()
            show = Show(show_date=timezone.now(), artist=Artist(id=i+1), venue=Venue(i+1))
            show.save()
            note = Note(show=Show(f'{i+1}'), user=User(id=1), title=f'title{2}', text=f'text{2}')
            note.save()
            
        for i in range(4):
            more_note = Note(show=Show(f'{1}'), user=User(id=1), title=f'title{2}', text=f'text{2}')
            more_note.save()

        for i in range(3):
            more_note = Note(show=Show(f'{2}'), user=User(id=1), title=f'title{2}', text=f'text{2}')
            more_note.save()
        

    def test_show_with_same_number_of_notes(self):

        response = self.client.get(reverse('show_most_notes'))
        
        show1 = Show.objects.get(pk=1)
        show2 = Show.objects.get(pk=2)
        show3 = Show.objects.get(pk=3)
        show4 = Show.objects.get(pk=4)
        show5 = Show.objects.get(pk=5)
       
        expected_shows = [show5, show4, show3, show1, show2 ]
        

        shows_provided = list(response.context['shows'])
    
        self.assertEqual(shows_provided, expected_shows)









    # def test_authorized_user_can_see_list_of_most_notes(self):

    #      user = User.objects.create_user("Paul","acero@hotmail.com", "password")
    #      self.client.force_login(user=user)
    #      response = self.client.get(reverse("login"))
    #      self.assertEqual(response.status_code, 200)
