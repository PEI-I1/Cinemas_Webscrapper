from django.shortcuts import render
from . import request_handler
from django.core import serializers
from django.http import HttpResponse
from .models import *
import json

# Create your views here.
def list_movies(request):
    request_handler.updateMovieSessions()

# Test function here.
def test1(request):
    """ get next sessions of specific movie
    """
    sessions = request_handler.next_sessions_specific_movie(original_title="Joker",date="2019-10-31",time="17:00:00",location="Braga Parque")
    sessions_as_json = serializers.serialize('json', sessions)
    return HttpResponse(sessions_as_json, content_type='json')

def test2(request):
    """ get next releases
    """
    movies = request_handler.upcoming_releases()
    movies_as_json = serializers.serialize('json', movies)
    return HttpResponse(movies_as_json, content_type='json')

def test3(request):
    """ get all cinemas
    """
    cinemas_as_json = serializers.serialize('json', Cinema.objects.all())
    return HttpResponse(cinemas_as_json, content_type='json')

def test4(request):
    """ get all movies
    """
    movies_as_json = serializers.serialize('json', Movie.objects.all())
    return HttpResponse(movies_as_json, content_type='json')

def req37(request):
    """ get movies of cinema
    """
    movies_as_json = json.dumps(request_handler.get_movies_by_cinema(coordinates=[41.5807204, -8.4293997]))
    return HttpResponse(movies_as_json, content_type='json')

def req38(request):
    """ get movies of cinema
    """
    movies_as_json = json.dumps(request_handler.get_sessions_by_duration(date="2019-10-31", duration=300, search_term="Nascente"))
    return HttpResponse(movies_as_json, content_type='json')

def req39(request):
    """ get upcoming sessions
    """
    sessions_as_json = json.dumps(request_handler.next_sessions(coordinates=[41.5807204, -8.4293997]))
    return HttpResponse(sessions_as_json, content_type='json')
