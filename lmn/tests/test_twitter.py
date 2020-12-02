from django.test import TestCase, Client

from django.urls import reverse
from django.contrib import auth
from django.contrib.auth import authenticate

from lmn.models import Venue, Artist, Note, Show
from django.contrib.auth.models import User

import re, datetime
from datetime import timezone

from lmn import twitter  # fixme

from unittest.mock import patch

class TestTwitter(TestCase):

    @patch('twitter.authorize')
    @patch('twitter.post_status')
    def test_tweet_success(self, mock_post, mock_auth):
        response = self.client.post(reverse('new_note'), {'post_type': 'Tweet and Add Note'})
        self.assertContains(response, 'Successfully Tweeted your note to our site account!')


    @patch('twitter.authorize', return_value='error')
    @patch('twitter.post_status')
    def test_tweet_tweepy_auth_issue(self, mock_post, mock_auth):
        response = self.client.post(reverse('new_note'), {'post_type': 'Tweet and Add Note'})
        self.assertContains(response, 'Sorry cant tweet right now')


    # consider selenium