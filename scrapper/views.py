from django.shortcuts import render
from . import request_handler
from django.core import serializers
from django.http import HttpResponse
from .models import *
import json
from datetime import datetime, time

# [41.5807204, -8.4293997]

# Create your views here.
def update_DB(request):
    request_handler.updateMovieSessions()
    res = { 'success': True }
    res_as_json = json.dumps(res)
    return HttpResponse(res_as_json, content_type='json')

def get_movies_by_cinema(request):
    """ get movies of cinema
    """
    search_term = request.GET.get('search_term', '')
    lat = request.GET.get('lat', '')
    lon = request.GET.get('lon', '')
    if lat and lon:
        movies_as_json = json.dumps(request_handler.get_movies_by_cinema(coordinates=[float(lat), float(lon)]))
    elif search_term:
        movies_as_json = json.dumps(request_handler.get_movies_by_cinema(search_term=search_term))
    else:
        movies_as_json = json.dumps({'error': 'Bad parameters'})
    return HttpResponse(movies_as_json, content_type='json')


def get_sessions_by_duration(request):
    """ get sessions by duration
    """
    duration = request.GET.get('duration', '')
    if not duration:
        sessions_as_json = json.dumps({'error': 'Duration parameter missing'})
    else:
        search_term = request.GET.get('search_term', '')
        lat = request.GET.get('lat', '')
        lon = request.GET.get('lon', '')
        start_date = request.GET.get('date', datetime.now().strftime('%Y-%m-%d'))
        start_time = request.GET.get('time', time(12, 0, 0).strftime('%H:%M:%S'))
        if lat and lon:
            sessions_as_json = json.dumps(request_handler.get_sessions_by_duration(date=start_date, time=start_time, duration=int(duration), coordinates=[float(lat), float(lon)]))
        elif search_term:
            sessions_as_json = json.dumps(request_handler.get_sessions_by_duration(date=start_date, time=start_time, duration=int(duration), search_term=search_term))
        else:
            sessions_as_json = json.dumps({'error': 'Bad parameters'})
    return HttpResponse(sessions_as_json, content_type='json')


def req3(request):
    """ get upcoming sessions
    """
    sessions_as_json = json.dumps(request_handler.next_sessions(coordinates=[41.5807204, -8.4293997]))
    return HttpResponse(sessions_as_json, content_type='json')


def req4(request):
    sessions_as_json = json.dumps(request_handler.get_sessions_by_movie(search_term='Braga', movie='Gemini'))
    return HttpResponse(sessions_as_json, content_type='json')


def req5(request):
    sessions_as_json = json.dumps(request_handler.get_sessions_by_date(search_term='Evora'))
    return HttpResponse(sessions_as_json, content_type='json')


def req6(request):
    """ search movies based on the genre
    """
    movies_as_json = json.dumps(request_handler.search_movies(genre='comédia'))
    return HttpResponse(movies_as_json, content_type='json')


def req7(request):
    """ search movies based on the producer
    """
    movies_as_json = json.dumps(request_handler.search_movies(producer='Woody'))
    return HttpResponse(movies_as_json, content_type='json')


def req8(request):
    """ search movies based on cast
    """
    movies_as_json = json.dumps(request_handler.search_movies(cast=['Cena', 'Leguizamo']))
    return HttpResponse(movies_as_json, content_type='json')


def req9(request):
    """ search movies based on synopsis
    """
    movies_as_json = json.dumps(request_handler.search_movies(synopsis=['Nova Iorque', 'planos']))
    return HttpResponse(movies_as_json, content_type='json')


def req10(request):
    """ search movies based on age restriction
    """
    movies_as_json = json.dumps(request_handler.search_movies(age=10))
    return HttpResponse(movies_as_json, content_type='json')


def req11(request):
    """ get next releases
    """
    movies_as_json = json.dumps(request_handler.upcoming_releases())
    return HttpResponse(movies_as_json, content_type='json')


def req13(request):
    movies_as_json = json.dumps(request_handler.get_movie_details(movie='Gemini'))
    return HttpResponse(movies_as_json, content_type='json')
