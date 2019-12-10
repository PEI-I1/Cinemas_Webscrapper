from django.shortcuts import render
from . import request_handler
from django.core import serializers
from django.http import HttpResponse
from .models import *
import json
from datetime import datetime, time

# lat=41.5807204&lon=-8.4293997

def get_matching_cinemas(request):
    search_term = request.GET.get('search_term', '')
    lat = request.GET.get('lat', '')
    lon = request.GET.get('lon', '')
    if lat and lon:
        cinemas_as_json = json.dumps(request_handler.search_cinemas(coordinates=[float(lat), float(lon)]))
    elif search_term:
        cinemas_as_json = json.dumps(request_handler.search_cinemas(search_term=search_term))
    else:
        cinemas_as_json = json.dumps({'error': 'Bad parameters'})
    return HttpResponse(cinemas_as_json, content_type='json')


def get_movies_by_cinema(request):
    """ Search for movies in given cinema
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
    """ Search for sessions for movies under a certain duratio
    """
    duration = request.GET.get('duration', '')
    if not duration:
        sessions_as_json = json.dumps({'error': 'Duration parameter missing'})
    else:
        search_term = request.GET.get('search_term', '')
        lat = request.GET.get('lat', '')
        lon = request.GET.get('lon', '')
        start_date = request.GET.get('date', datetime.now().strftime('%Y-%m-%d'))
        start_time = request.GET.get('start_time', datetime.now().strftime('%H:%M:%S'))
        if lat and lon:
            sessions_as_json = json.dumps(request_handler.get_sessions_by_duration(date=start_date,
                                                                                   time=start_time,
                                                                                   duration=int(duration),
                                                                                   coordinates=[float(lat), float(lon)]))
        elif search_term:
            sessions_as_json = json.dumps(request_handler.get_sessions_by_duration(date=start_date,
                                                                                   time=start_time,
                                                                                   duration=int(duration),
                                                                                   search_term=search_term))
        else:
            sessions_as_json = json.dumps({'error': 'Bad parameters'})
    return HttpResponse(sessions_as_json, content_type='json')


def next_sessions(request):
    """ Get the next sessions in a given cinema
    """
    search_term = request.GET.get('search_term', '')
    lat = request.GET.get('lat', '')
    lon = request.GET.get('lon', '')
    if lat and lon:
        sessions_as_json = json.dumps(request_handler.next_sessions(coordinates=[float(lat), float(lon)]))
    elif search_term:
        sessions_as_json = json.dumps(request_handler.next_sessions(search_term=search_term))
    else:
        sessions_as_json = json.dumps({'error': 'Bad parameters'})
    return HttpResponse(sessions_as_json, content_type='json')


def get_sessions_by_movie(request):
    """ Get all sessions for a given movie in a collection of cinemas
    """
    movie = request.GET.get('movie', '')
    if not movie:
        sessions_as_json = json.dumps({'error': 'Movie parameter missing'})
    else:
        search_term = request.GET.get('search_term', '')
        lat = request.GET.get('lat', '')
        lon = request.GET.get('lon', '')
        start_date = request.GET.get('date', datetime.now().strftime('%Y-%m-%d'))
        start_time = request.GET.get('time', datetime.now().strftime('%H:%M:%S'))
        if lat and lon:
            sessions_as_json = json.dumps(request_handler.get_sessions_by_movie(date=start_date, time=start_time, movie=movie, coordinates=[float(lat), float(lon)]))
        elif search_term:
            sessions_as_json = json.dumps(request_handler.get_sessions_by_movie(date=start_date, time=start_time, movie=movie, search_term=search_term))
        else:
            sessions_as_json = json.dumps({'error': 'Bad parameters'})
    return HttpResponse(sessions_as_json, content_type='json')


def get_sessions_by_date(request):
    """ Get the sessions by date
    """
    search_term = request.GET.get('search_term', '')
    lat = request.GET.get('lat', '')
    lon = request.GET.get('lon', '')
    start_date = request.GET.get('date', datetime.now().strftime('%Y-%m-%d'))
    start_time = request.GET.get('start_time', datetime.now().strftime('%H:%M:%S'))
    end_time = request.GET.get('end_time', time(5, 0, 0).strftime('%H:%M:%S'))
    if lat and lon:
        sessions_as_json = json.dumps(request_handler.get_sessions_by_date(date=start_date,
                                                                           start_time=start_time,
                                                                           end_time=end_time,
                                                                           coordinates=[float(lat), float(lon)]))
    elif search_term:
        sessions_as_json = json.dumps(request_handler.get_sessions_by_date(date=start_date,
                                                                           start_time=start_time,
                                                                           end_time=end_time,
                                                                           search_term=search_term))
    else:
        sessions_as_json = json.dumps({'error': 'Bad parameters'})
    return HttpResponse(sessions_as_json, content_type='json')


def search_movies(request):
    """ Search for movies based on genre, producer, cast, synopsis, age restriction
    """
    genre = request.GET.get('genre', '')
    producer = request.GET.get('producer', '')
    cast = request.GET.get('cast', '')
    synopsis = request.GET.get('synopsis', '')
    age = int(request.GET.get('age', '18'))
    if genre or producer or cast or synopsis or age:
        if cast:
            cast = cast.split(',')
        else:
            cast = []
        if synopsis:
            synopsis = synopsis.split(',')
        else:
            synopsis = []
        movies_as_json = json.dumps(request_handler.search_movies(genre=genre, producer=producer, cast=cast, synopsis=synopsis, age=age))
    else:
        movies_as_json = json.dumps({'error': 'It needs at least one paramater (Genre, Producer, Cast, Synopsis, Age)'})
    return HttpResponse(movies_as_json, content_type='json')


def upcoming_releases(request):
    """ Search for upcoming movies
    """
    movies_as_json = json.dumps(request_handler.upcoming_releases())
    return HttpResponse(movies_as_json, content_type='json')


def get_movie_details(request):
    """ get details of movie 
    """
    movie = request.GET.get('movie', '')
    if not movie:
        movies_as_json = json.dumps({'error': 'Movie parameter missing'})
    else:
        movies_as_json = json.dumps(request_handler.get_movie_details(movie=movie))
    return HttpResponse(movies_as_json, content_type='json')
