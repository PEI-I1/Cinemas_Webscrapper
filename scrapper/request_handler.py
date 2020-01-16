from .models import *
from django.conf import settings
from django.db.models import Q
from datetime import datetime, date, time, timedelta
from .scrapper_utils import getMovies, getNextDebuts
from functools import reduce
import operator
from geopy.geocoders import Nominatim
from haversine import haversine, Unit
import re

PIVOT_TIME = time(5, 0, 0).strftime('%H:%M:%S')
geolocator = Nominatim()

def haversine_distance(c1, c2):
    ''' Calculate the distance between two points on a spherical surface
    :param: Point 1
    :param: Point 2
    '''
    location_1 = c1
    location_2 = c2
    return haversine(location_1, location_2, unit=Unit.KILOMETERS)


def closest_cinemas(coordinates=[]):
    ''' Find the cinemas that are closest to the given coordinates
    :param: users location
    '''
    cinemas = Cinema.objects.all()
    closest_cinemas = []
    min_dist = 100000
    closest = None

    for cinema in cinemas:
        cinema_coordinates = cinema.coordinates.strip().split(',', 1)
        distance = haversine_distance((coordinates[0],coordinates[1]),(float(cinema_coordinates[0]),float(cinema_coordinates[1])))
        if  distance < settings.MAX_DISTANCE:
            closest_cinemas.append((cinema.coordinates, cinema.name))
        if distance < min_dist and distance >= settings.MAX_DISTANCE:
            closest = (cinema.coordinates, cinema.name)
            min_dist = distance

    if not(closest_cinemas) and closest:
        closest_cinemas = [closest]

    return closest_cinemas


def find_cinemas(search_term=""):
    ''' Find cinemas that match the search term
    :param: string/term to look for
    '''
    cinemas = Cinema.objects.all()
    cinemas_response = []

    for cinema in cinemas:
        st = search_term.lower()
        if st in cinema.name.lower() or st in cinema.alt_name.lower() or st in cinema.city.lower():
            cinemas_response.append((cinema.coordinates, cinema.name))

    if not(cinemas_response):
        try:
            addr_raw = geolocator.geocode("Portugal, " + search_term)
            if addr_raw:
                coordinates = [addr_raw.latitude, addr_raw.longitude]
                cinemas_response = closest_cinemas(coordinates)
        except:
            pass

    return cinemas_response


def movies_of_cinemas(cinemas_coordinates):
    ''' Check for all the movies in a cinema
    :param: coordinates corresponding to the cinemas location
    '''
    cinemas = Cinema.objects \
                    .values_list('coordinates', 'name') \
                    .filter(coordinates__in=cinemas_coordinates)
    res = {}

    for cinema in cinemas:
        movies = list(set(Session.objects \
                          .filter(cinema=cinema[0]) \
                          .values_list('movie__title_pt',
                                       'movie__imdb_rating')))
        
        res[cinema[1]] = [{'Portuguese title': movie_info[0], 'IMDB Rating': movie_info[1]}
                          for movie_info in movies]
    return res


def get_movies_by_cinema(search_term='', coordinates=[]):
    ''' Get movies in exhibition in a certain cinema
    :param: query for cinema
    :param: cinema coordinates
    '''
    cinemas = get_matching_cinemas(search_term, coordinates)
    movies = movies_of_cinemas([cinema[0] for cinema in cinemas])
    return movies


def get_matching_cinemas(search_term="", coordinates = []):
    ''' Get all cinemas matching the search parameters
    :param: query for cinema
    :param: cinema coordinates
    :return: list of cinema's coordinates and names
    '''
    if search_term:
        cinemas = find_cinemas(search_term)
    else:
        cinemas = closest_cinemas(coordinates)
    return cinemas


def search_cinemas(search_term="", coordinates = []):
    ''' Get all cinemas matching the search parameters (API facing)
    :param: query for cinema
    :param: cinema coordinates
    :return: list of cinema's names
    '''
    cinemas_names = [name for (coordinates, name) in get_matching_cinemas(search_term, coordinates)]
    return {'cinemas': cinemas_names}

def get_sessions_by_date(date, start_time, end_time, search_term="", coordinates=[]):
    ''' Search for all sessions in a specific cinema after a given date-time
    :param: date of the sessions to search for
    :param: minimum start time for the sessions
    :param: query for the cinema
    :param: user location
    '''
    sessions = filter_sessions_by_datetime(date, start_time, end_time, search_term, coordinates).values_list('start_date',
                                                                                                             'start_time',
                                                                                                             'availability',                                                                                                             
                                                                                                             'purchase_link',
                                                                                                             'cinema__name',
                                                                                                             'movie')
    
    res = {}
    for session in sessions:
        session_object = {'Movie': session[-1],
                          'Start date': formatDate(str(session[0])),
                          'Start time': formatTime(str(session[1])),
                          'Availability': str(session[2]),
                          'Ticket link' : session[3]}
        res[session[-2]] = res.get(session[-2], []) + [session_object]

    for cinema in res:
        for session in res[cinema]:
            session['Start time'] = re.sub(r'0([0-9])(h[0-5][0-9])', r'5\g<1>\g<2>', session['Start time'])

    for cinema in res:
        res[cinema] = sorted(res[cinema], key=lambda x: x['Start date'] + x['Start time'])

    for cinema in res:
        for session in res[cinema]:
            session['Start time'] = re.sub(r'5([0-9]h[0-5][0-9])', r'0\g<1>', session['Start time'])
    
    return res
    

def filter_sessions_by_datetime(date, start_time, end_time=None, search_term="", coordinates=[]):
    ''' Filter all sessions taking place after a specific date and time
    in specific cinemas
    :param: date of the sessions to search for
    :param: minimum start time for the sessions
    :param: query for the cinema
    :param: user location
    '''
    cinemas = get_matching_cinemas(search_term, coordinates)
    

    if(start_time <= PIVOT_TIME and end_time <= PIVOT_TIME) or (start_time > PIVOT_TIME and end_time > PIVOT_TIME):
        sessions = Session.objects \
                      .filter(start_date=date,
                              cinema__in=[cinema[0] for cinema in cinemas])
        return sessions.filter(Q(start_time__gte=start_time) & Q(start_time__lte = end_time))

    elif(start_time <= PIVOT_TIME and end_time > PIVOT_TIME):
        prev_date = (datetime.strptime(date, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
        sessions = Session.objects \
                          .filter(cinema__in=[cinema[0] for cinema in cinemas])\
                          .filter((Q(start_date = date) & Q(start_time__lte = end_time)) |
                                  (Q(start_date = prev_date) & Q(start_time__gte = start_time) & Q(start_time__lte = PIVOT_TIME)))
        return sessions
        
    elif(start_time > PIVOT_TIME and end_time <= PIVOT_TIME):
        sessions = Session.objects \
                          .filter(start_date=date,
                                  cinema__in=[cinema[0] for cinema in cinemas])
        return sessions.filter(Q(start_time__gte=start_time) | Q(start_time__lte = end_time))


def get_sessions_by_duration(duration, date, start_time, end_time, search_term = "", coordinates = []):
    ''' Retrieve sessions for movies under the specified duration
    :param: movie duration limit
    :param: date of the sessions to search for
    :param: minimum start time for the sessions
    :param: query for the cinema
    :param: user location
    '''
    sessions = filter_sessions_by_datetime(date, start_time, end_time, search_term, coordinates)
    movies_ud = Movie.objects \
                     .filter(length__lte=duration) \
                     .values_list('original_title')
    sessions = sessions.filter(movie__in=movies_ud).values_list('start_date',
                                                                'start_time',
                                                                'availability',
                                                                'purchase_link',
                                                                'cinema__name',
                                                                'movie',
                                                                'movie__length')

    res = {}
    for session in sessions:
        session_object = {'Length (min)': session[-1],
                          'Movie': session[-2],
                          'Start date': formatDate(str(session[0])),
                          'Start time': formatTime(str(session[1])),
                          'Availability': str(session[2]),
                          'Ticket link' : session[3]}
        res[session[-3]] = res.get(session[-3], []) + [session_object]

    for cinema in res:
        for session in res[cinema]:
            session['Start time'] = re.sub(r'0([0-9])(h[0-5][0-9])', r'5\g<1>\g<2>', session['Start time'])

    for cinema in res:
        res[cinema] = sorted(res[cinema], key=lambda x: x['Start date'] + x['Start time'])

    for cinema in res:
        for session in res[cinema]:
            session['Start time'] = re.sub(r'5([0-9]h[0-5][0-9])', r'0\g<1>', session['Start time'])
    
    return res
    

def next_sessions(search_term="", coordinates=[]):
    ''' List upcoming sessions in a specific cinema
    :param: query for the cinema
    :param: user location
    '''
    now = datetime.today()
    current_time = now.strftime("%H:%M:%S")
    current_date = now.strftime("%Y-%m-%d")
    end_time = PIVOT_TIME
    sessions = filter_sessions_by_datetime(current_date, current_time, end_time, search_term, coordinates).values_list('movie',
                                                                                                                       'movie__trailer_url',
                                                                                                                       'start_date',
                                                                                                                       'start_time',
                                                                                                                       'availability',
                                                                                                                       'purchase_link',
                                                                                                                       'cinema__name')

    res = {}
    for session in sessions:
        session_object = {'Movie': session[0],
                          'Trailer': session[1],
                          'Start date': formatDate(str(session[2])),
                          'Start time': formatTime(str(session[3])),
                          'Availability': str(session[4]),
                          'Ticket link' : session[5]}
        res[session[-1]] = res.get(session[-1], []) + [session_object]

    for cinema in res:
        for session in res[cinema]:
            session['Start time'] = re.sub(r'0([0-9])(h[0-5][0-9])', r'5\g<1>\g<2>', session['Start time'])

    for cinema in res:
        res[cinema] = sorted(res[cinema], key=lambda x: x['Start date'] + x['Start time'])

    for cinema in res:
        for session in res[cinema]:
            session['Start time'] = re.sub(r'5([0-9]h[0-5][0-9])', r'0\g<1>', session['Start time'])
    
    return res


def movies_queryset_to_array(movies, full_description = False):
    ''' Convert a movie queryset to an array of values
    :param: movie queryset
    :param: indicates whether all the info about a movie should be retrieved
    '''
    if full_description:
        movies = movies.values_list('original_title', 'cast', 'genre__name', 'banner_url', 'trailer_url', 'producer',
                                    'imdb_rating', 'synopsis', 'length', 'released', 'title_pt', 'age_rating')
    else:
        movies = movies.values_list('original_title', 'cast', 'genre__name', 'banner_url', 'trailer_url', 'producer',
                                    'imdb_rating')
    
    res = []
    for movie in movies:
        movie_object = {
            'Original title': movie[0],
            'Cast': movie[1],
            'Genre': movie[2],
            'Banner': movie[3],
            'Trailer': movie[4],
            'Producer': movie[5],
            'IMDB Rating': movie[6]
        }
        if full_description:
            movie_object['Synopsis'] = movie[7]
            movie_object['Length (min)'] = movie[8]
            movie_object['Released'] = movie[9]
            movie_object['Portuguese title'] = movie[10]
            movie_object['Age rating'] = movie[11]
        res.append(movie_object)
    return res


def search_movies(genre, producer, cast, synopsis, age):
    ''' List upcoming movies based on genre,producer,cast,synopsis and age
    :param: genre requested by the costumer
    :param: producer requested by the costumer
    :param: cast member or members requested by the costumer
    :param: synopsis/details of the movie given by the costumer
    :param: age limit requested by the costumer
    '''
    movies = Movie.objects.filter(
        producer__icontains=producer,
        age_rating_id__lte=age
    )

    if cast != []:
        movies = movies.filter(reduce(operator.and_, (Q(cast__icontains=actor) for actor in cast)))
    
    if synopsis != []:
        movies = movies.filter(reduce(operator.and_, (Q(synopsis__icontains=term) for term in synopsis)))

    if genre:
        movies_aux = movies.filter(genre__name=genre)
        if not movies_aux:
            movies_aux = movies.filter(genre__name__icontains=genre)
        movies = movies_aux

    return movies_queryset_to_array(movies, full_description=True)


def upcoming_releases():
    ''' List upcoming releases
    '''
    movies = Movie.objects.filter(released=False)
    return movies_queryset_to_array(movies)


def get_movie_details(movie):
    ''' Retrieve the details of a movie
    :param: movie query
    '''
    movies = Movie.objects \
                  .filter(Q(original_title__icontains=movie) | Q(title_pt__icontains=movie)).values_list('original_title')
    return movies_queryset_to_array(movies, full_description=True)


def get_sessions_by_movie(date, start_time, end_time, movie, search_term="", coordinates=[]):
    ''' Get all sessions of a movie in a set of cinemas
    :param: date of the sessions to search for
    :param: minimum start time for the sessions
    :param: movie query
    :param: query for the cinema
    :param: user location
    '''
    movies_matched = Movie.objects \
                          .filter(Q(original_title__icontains=movie) | Q(title_pt__icontains=movie)).values_list('original_title')
    
    sessions = filter_sessions_by_datetime(date, start_time, end_time, search_term, coordinates) \
                .filter(movie__in=movies_matched) \
                .values_list('movie', 'start_date', 'start_time', 'availability', 'purchase_link', 'cinema__name')

    res = {}
    for session in sessions:
        session_object = {'Start date': formatDate(str(session[1])),
                          'Start time': formatTime(str(session[2])),
                          'Availability': str(session[3]),
                          'Ticket link' : session[4]}

        res[session[-1]] = res.get(session[-1], {})
        res[session[-1]][session[0]] = {'sessions': res[session[-1]].get(session[0], {'sessions':[]})['sessions'] + [session_object]}
    
    for cinema in res:
        for movie in res[cinema]:
            for session in res[cinema][movie]['sessions']:
                session['Start time'] = re.sub(r'0([0-9])(h[0-5][0-9])', r'5\g<1>\g<2>', session['Start time'])

    for cinema in res:
        for movie in res[cinema]:
            res[cinema][movie]['sessions'] = sorted(res[cinema][movie]['sessions'], key=lambda x: x['Start date'] + x['Start time'])

    for cinema in res:
        for movie in res[cinema]:
            for session in res[cinema][movie]['sessions']:
                session['Start time'] = re.sub(r'5([0-9]h[0-5][0-9])', r'0\g<1>', session['Start time'])

    return res


def formatDate(date):
    ''' Change format of date string: from 'Y-M-D' to 'D/M/Y'
    :param: date string
    '''
    return re.sub(r'([0-9]{4})-([0-9]{2})-([0-9]{2})', r'\g<3>/\g<2>/\g<1>', date)


def formatTime(time):
    ''' Change format of time string: from 'H:M:S' to 'HhM'
    :param: time string
    '''
    return re.sub(r'([012][0-9]):([0-5][0-9]):[0-5][0-9]', r'\g<1>h\g<2>', time)
