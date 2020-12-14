
import os
import requests
from .models import Artist, Venue, Show


import logging
"""Getting data from ticketmaster api and saving to the database"""


key = os.environ.get('TICKETMASTER_KEY')
url = 'https://app.ticketmaster.com/discovery/v2/events'
classificationName = 'music'
city = 'Minneapolis'

def get_ticketMaster():
    """The api call to Ticketmaster

    :return: data json response
    :raises exception
    """
    try:
        query= {'classificationName': classificationName, 'city' : city, 'apikey': key}
        response = requests.get(url, params=query)
        data = response.json()
        return data
    except Exception as e:
        logging.error(e)
        
    
def extract_music_details(data):
    """Extract relevant data from the response;
    saving data to the database avoiding duplicates

    :params: data - json response from ticketmaster
    """
    events = data['_embedded']['events']
    
    for event in events: 
        performer = event['name']
        venue_name = event['_embedded']['venues'][0]['name']
        venue_city = event['_embedded']['venues'][0]['city']['name']
        venue_state = event['_embedded']['venues'][0]['state']['stateCode']
        show_date_time = event['dates']['start']['dateTime']   
        
        
        ##linking info to models and saving it 
        try:
            artist =  Artist.objects.get(name=performer)
        except :# otherwise add a new artist 
            artist = Artist(name=performer)
            artist.save() #must save the new artist, then get id
            artist.id

        try:#if this venue already in the database, don't add it again
            venue=Venue.objects.get(name=venue_name)
        except: #if not already in dbase, create new Venue object and save it
            venue = Venue(name=venue_name, city=venue_city, state=venue_state)
            venue.save()
            venue.id

        try: #if this show already in dbase, don't add it again
            show = Show.objects.get(show_date=show_date_time, artist_id = artist.id, venue_id = venue.id)
        except: #otherwise, make a new Show object and save it
            show=Show(show_date=show_date_time, artist_id = artist.id, venue_id = venue.id)
            show.save()
    
            
    


            