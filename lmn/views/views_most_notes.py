from django.shortcuts import render
from ..models import Show
from django.contrib.auth.decorators import login_required

from django.db.models import Count
from ..models import  Show

def show_most_notes(request):
# Query collects 5 shows with most notes and displays the 5 most reviewed
# If show does not have a note it won't be displayed because will be excluded out of the list .
    shows = Show.objects.annotate(num_notes=Count('note')).exclude(num_notes=0).order_by('-num_notes')[:5]
    print(shows)
    return render(request, 'lmn/notes/show_most_notes.html', {'shows': shows})

    