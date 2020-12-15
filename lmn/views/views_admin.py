from ..ticketmaster import extract_music_details, get_ticketMaster
from django.http import HttpResponse

def get_music_data():
    data = get_ticketMaster()
    extract_music_details(data)
    return HttpResponse('ok')
