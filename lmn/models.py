from django.db import models

from django.db import models
from django.contrib.auth.models import User
import datetime
from django.core.files.storage import default_storage

# Every model gets a primary key field by default.

# Users, venues, shows, artists, notes

# User is provided by Django. The email field is not unique by
# default, so add this to prevent more than one user with the same email.
User._meta.get_field('email')._unique = True

#Require email, first name and last name
User._meta.get_field('email')._blank = False
User._meta.get_field('last_name')._blank = False
User._meta.get_field('first_name')._blank = False


""" A music artist """
class Artist(models.Model):
    name = models.CharField(max_length=200, blank=False, unique=True)

    def __str__(self):
        return f'Name: {self.name}'


""" A venue, that hosts shows. """
class Venue(models.Model):
    name = models.CharField(max_length=200, blank=False)
    city = models.CharField(max_length=200, blank=False)
    state = models.CharField(max_length=2, blank=False) 
    class Meta:
        #to avoid adding the same venue twice, a Venue's name, city and state together are a unique entity
        unique_together = [[ 'name', 'city', 'state']]
    def __str__(self):
        return f'Name: {self.name} in {self.city}, {self.state}'


""" A show - one artist playing at one venue at a particular date. """
class Show(models.Model):
    show_date = models.DateTimeField(blank=False)  
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)


    class Meta:
        #to avoid adding a duplicate show, these 3 elements considered together must be unique
        #if a show with the same 3 elements is found, it will not be added to the database
        unique_together = [['show_date', 'artist', 'venue']]

    def __str__(self):
        return f'Artist: {self.artist} at: {self.venue} on: {self.show_date}'


""" One user's opinion of one show. """
class Note(models.Model):
    show = models.ForeignKey(Show, blank=False, on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', blank=False, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=False)
    text = models.TextField(max_length=1000, blank=False)
    posted_date = models.DateTimeField(auto_now_add=True, blank=False)

    photo = models.ImageField(upload_to='user_images/', blank=True, null=True)

    

    def save(self, *args, **kwargs):
        #get reference to previous versionof this note
        old_note = Note.objects.filter(pk=self.pk).first()
        if old_note and old_note.photo: #check if an old note exists and has a photo
            if old_note.photo != self.photo: # check if the photo has been changed
                self.delete_photo(old_note.photo) #delete the old photo
        super().save(*args, **kwargs) 

    def delete_photo(self, photo):
        if default_storage.exists(photo.name):
            default_storage.delete(photo.name)

    #when a Note is deleted, delete the photo file too
    def delete(self, *args, **kwargs):
        if self.photo:
            self.delete_photo(self.photo)

        super().delete(*args, **kwargs)



    def __str__(self):
        return f'User: {self.user} Show: {self.show} Note title: {self.title} Text: {self.text} Posted on: {self.posted_date} Photo: {self.photo}'

