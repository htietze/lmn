from django.test import TestCase, Client

from django.urls import reverse
from django.contrib import auth
from django.contrib.auth import authenticate

from lmn.models import Venue, Artist, Note, Show
from django.contrib.auth.models import User
# from lmnop_project import helpers
# import re, datetime
# from datetime import timezone
# import os


class TestRatingsAddedWithNotes(TestCase):
    fixtures = ['testing_users', 'testing_artists', 'testing_shows', 'testing_venues', 'testing_ratings']
    
    def setUp(self):
        user = User.objects.first()
        self.client.force_login(user)

    def test_add_note_without_rating(self):

        initial = Note.objects.count()

        new_url = reverse('new_note', kwargs={'show_pk':1})

        response = self.client.post(new_url, {'text':'some text', 'title':'a title'})

        note_query = Note.objects.filter(text='some text')
        self.assertEqual(note_query.count(), 1)
        self.assertEqual(Note.objects.count(), initial + 1)

    def test_add_note_with_rating(self):

        intial = Note.objects.count()

        new_url = reverse('new_note', kwargs={'show_pk':1})
    
        response = self.client.post(new_url, {'text':'some more text', 'title':'another title', 'rating':'3'})

        note_query = Note.objects.filter(text='some more text')
        self.assertEqual(note_query.count(), 1)
        self.assertEqual(Note.objects.count(), intial + 1)
