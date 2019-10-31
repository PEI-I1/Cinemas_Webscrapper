from django.shortcuts import render
from . import request_handler
from django.core import serializers
from django.http import HttpResponse
from .models import *

# Create your views here.
def list_movies(request):
    request_handler.updateMovieSessions()

# Test function here.
def test1(request):
    """ get next sessions of specific movie
    """
    sessions = request_handler.next_sessions_specific_movie(original_title="Joker",date="2019-10-17",time="17:00:00",location="Braga Parque")
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

def test5(request):
    """ get movies of cinema
    """
    movies_as_json = serializers.serialize('json', request_handler.get_movies_by_cinema("Braga"))
    return HttpResponse(movies_as_json, content_type='json')