from .models import *
from django.conf import settings
from django.db.models import Q
from datetime import datetime, date, time, timedelta
from .scrapper_utils import getMovies, getNextDebuts
from functools import reduce
import operator
from celery import shared_task, task
#import math
from haversine import haversine, Unit

# MID DAY
MID_DAY_S = time(12, 0, 0).strftime('%H:%M:%S')

@task(bind=True)
def updateMovieSessions(self):
    """ Fetch the latest session and movie info to update the database
    """
    print("Updating database")
    movie_dump = getMovies()
    debuts_dump = getNextDebuts()

    for debut in debuts_dump:
        movie_dump.append(debut)

    for movie in movie_dump:
        
        age_rating = AgeRating.objects.all().filter(age = movie['age'])
        if len(age_rating) == 0:
            age_rating = AgeRating(age = movie['age'])
            age_rating.save()
            print('NOVA IDADE ADICIONADA')
        else:
            age_rating = age_rating[0]
        
        genre = Genre.objects.all().filter(name = movie['genre'])
        if len(genre) == 0:
            genre = Genre(name = movie['genre'])
            genre.save()
            print('NOVO GÉNERO ADICIONADO')
        else:
            genre = genre[0]

        movie_entry = Movie(
            original_title = movie['original_title'],
            title_pt = movie['title'],
            producer = movie['producer'],
            cast = movie['actors'],
            synopsis = movie['synopsis'],
            length = movie['duration'],
            trailer_url = movie['trailer_url'],
            banner_url = movie['banner_url'],
            released = not movie['debut'],
            age_rating = age_rating,
            genre = genre
        )
        
        movie_entry.save()

        for session in movie['sessions']:

            cinema = Cinema.objects.all().filter(name = session['cinema'])
            if len(cinema) > 0:
                cinema = cinema[0]
            else:
                cinema = Cinema.objects.all().filter(alt_name = session['cinema'])[0]

            session_entry = Session(
                start_date = datetime.strptime(session['date'], '%Y-%m-%d'),
                start_time = datetime.strptime(session['hours'], '%Hh%M'),
                room = session['room'],
                purchase_link = session['purchase_link'],
                movie = movie_entry,
                cinema = cinema
            )

            session_entry.save()

    print("Update complete")
            
'''
def haversine_distance(c1, c2):
    """ Calculate the distance between two points on a spherical surface
    :param: Point 1
    :param: Point 2
    """
    r = 6371e3 #Earth's radius (km)
    hav1 = math.sin((c2[0] - c1[0])/2)**2
    hav2 = math.sin((c2[1] - c1[1])/2)**2
    h = math.sqrt(hav1 + math.cos(c1[0])*math.cos(c2[0])*hav2)

    return 2*r*math.asin(h)
'''


def haversine_distance(c1, c2):
    """ Calculate the distance between two points on a spherical surface
    :param: Point 1
    :param: Point 2
    """
    location_1 = c1
    location_2 = c2
    return haversine(location_1, location_2, unit=Unit.KILOMETERS)


def closest_cinemas(coordinates=[]):
    """ Find the cinemas that are closest to the given coordinates
    :param: users location
    """
    cinemas = Cinema.objects.all()
    closest_cinemas = []
    for cinema in cinemas:
        cinema_coordinates = cinema.coordinates.strip().split(',', 1)
        distance = haversine_distance((coordinates[0],coordinates[1]),(float(cinema_coordinates[0]),float(cinema_coordinates[1])))
        if  distance < settings.MAX_DISTANCE:
            closest_cinemas.append((cinema.coordinates, cinema.name))
    return closest_cinemas


def find_cinemas(search_term=""):
    """ Find cinemas that match the search term
    :param: string/term to look for
    """
    cinemas = Cinema.objects.all()
    cinemas_response = []
    for cinema in cinemas:
        st = search_term.lower()
        if st in cinema.name.lower() or st in cinema.alt_name.lower() or st in cinema.city.lower():
            cinemas_response.append((cinema.coordinates, cinema.name))
    return cinemas_response


def movies_of_cinemas(cinemas_coordinates):
    """ Check for all the movies in a cinema
    :param: coordinates corresponding to the cinemas location
    """
    cinemas = Cinema.objects \
                    .values_list('coordinates', 'name') \
                    .filter(coordinates__in=cinemas_coordinates)
    res = {}

    for cinema in cinemas:
        movie_titles = list(set(Session.objects \
                                       .filter(cinema=cinema[0]) \
                                       .values_list('movie', flat=True)))
        res[cinema[1]] = movie_titles
    return res


def get_movies_by_cinema(search_term="", coordinates=[]):
    """ Get movies in exhibition in a certain cinema
    :param: query for cinema
    :param: cinema coordinates
    """
    cinemas = get_matching_cinemas(search_term, coordinates)
    movies = movies_of_cinemas([cinema[0] for cinema in cinemas])
    return movies


def get_matching_cinemas(search_term="", coordinates = []):
    """ Get all cinemas matching the search parameters
    :param: query for cinema
    :param: cinema coordinates
    :return: list of cinema's coordinates and names
    """
    if search_term:
        cinemas = find_cinemas(search_term)
    else:
        cinemas = closest_cinemas(coordinates)
    return cinemas


def search_cinemas(search_term="", coordinates = []):
    """ Get all cinemas matching the search parameters (API facing)
    :param: query for cinema
    :param: cinema coordinates
    :return: list of cinema's names
    """
    cinemas_names = [name for (coordinates, name) in get_matching_cinemas(search_term, coordinates)]
    return {'cinemas': cinemas_names}

def get_sessions_by_date(date, start_time, end_time, search_term="", coordinates=[]):
    """ Search for all sessions in a specific cinema after a given date-time
    :param: date of the sessions to search for
    :param: minimum start time for the sessions
    :param: query for the cinema
    :param: user location
    """
    sessions = filter_sessions_by_datetime(date, start_time, end_time, search_term, coordinates).values_list('start_date',
                                                                                                              'start_time',
                                                                                                              'purchase_link',
                                                                                                              'cinema__name',
                                                                                                              'movie')
    res = {}
    for session in sessions:
        session_object = {'Start date': str(session[0]),
                          'Start time': str(session[1]),
                          'Ticket link': session[2]}
        res[session[-2]] = res.get(session[-2], {})
        res[session[-2]][session[-1]] = {'sessions': res[session[-2]].get(session[-1], {'sessions':[]})['sessions'] + [session_object]}
    return res
    

def filter_sessions_by_datetime(date, start_time, end_time, search_term="", coordinates=[]):
    """ Filter all sessions taking place after a specific date and time
    in specific cinemas
    :param: date of the sessions to search for
    :param: minimum start time for the sessions
    :param: query for the cinema
    :param: user location
    """
    cinemas = get_matching_cinemas(search_term, coordinates)
    sessions = Session.objects \
                      .filter(start_date=date,
                              cinema__in=[cinema[0] for cinema in cinemas])

    if((start_time <= MID_DAY_S and end_time <= MID_DAY_S) or
       (start_time > MID_DAY_S and start_time < "24:00:00" and end_time > MID_DAY_S and end_time < "24:00:00")):
        return sessions.filter(Q(start_time__gte=start_time) & Q(start_time__lte = end_time))
    elif(start_time < "24:00:00"):
        return sessions.filter(Q(start_time__gte=start_time) | Q(start_time__lte = end_time))


def get_sessions_by_duration(duration, date, time, search_term = "", coordinates = []):
    """ Retrieve sessions for movies under the specified duration
    :param: movie duration limit
    :param: date of the sessions to search for
    :param: minimum start time for the sessions
    :param: query for the cinema
    :param: user location
    """
    sessions = filter_sessions_by_datetime(date, time, MID_DAY_S, search_term, coordinates)
    movies_ud = Movie.objects \
                     .filter(length__lte=duration) \
                     .values_list('original_title')
    sessions = sessions.filter(movie__in=movies_ud).values_list('start_date',
                                                                'start_time',
                                                                'purchase_link',
                                                                'cinema__name',
                                                                'movie',
                                                                'movie__length')
    res = {}
    for session in sessions:
        session_object = {'Start date': str(session[0]),
                          'Start time': str(session[1]),
                          'Ticket link': session[2]}
        res[session[-3]] = res.get(session[-3], {})
        res[session[-3]][session[-2]] = {'Length (min)': session[-1], 'sessions': res[session[-3]].get(session[-2], {'sessions':[]})['sessions'] + [session_object]}
    return res
    

def next_sessions(search_term="", coordinates=[]):
    """ List upcoming sessions in a specific cinema
    :param: query for the cinema
    :param: user location
    """
    now = datetime.today()
    current_time = now.strftime("%H:%M:%S")

    if current_time < '05:00:00': #account for sessions past mid-night
        take_one_day = timedelta(days = -1)
        now = now + take_one_day
    
    current_date = now.strftime("%Y-%m-%d")

    sessions = filter_sessions_by_datetime(current_date, current_time, MID_DAY_S, search_term, coordinates).values_list('movie',
                                                                                                                        'start_date',
                                                                                                                        'start_time',
                                                                                                                        'purchase_link',
                                                                                                                        'cinema__name')

    res = {}
    for session in sessions:
        session_object = {'Start date': str(session[1]),
                          'Start time': str(session[2]),
                          'Ticket link' : session[3]}
        res[session[-1]] = res.get(session[-1], {})
        res[session[-1]][session[0]] = {'sessions': res[session[-1]].get(session[0], {'sessions':[]})['sessions'] + [session_object]}
    return res


def movies_queryset_to_array(movies, full_description = False):
    """ Convert a movie queryset to an array of values
    :param: movie queryset
    :param: indicates whether all the info about a movie should be retrieved
    """
    if full_description:
        movies = movies.values_list('original_title', 'cast', 'genre__name', 'banner_url', 'producer',
                                    'synopsis', 'length', 'trailer_url', 'released', 'title_pt', 'age_rating')
    else:
        movies = movies.values_list('original_title', 'cast', 'genre__name', 'banner_url')
    
    res = []
    for movie in movies:
        movie_object = {
            'Original title': movie[0],
            'Cast': movie[1],
            'Genre': movie[2],
            'Banner': movie[3]
        }
        if full_description:
            movie_object['Producer'] = movie[4]
            movie_object['Synopsis'] = movie[5]
            movie_object['Length (min)'] = movie[6]
            movie_object['Trailer'] = movie[7]
            movie_object['Released'] = movie[8]
            movie_object['Portuguese title'] = movie[9]
            movie_object['Age rating'] = movie[10]
        res.append(movie_object)
    return res


def search_movies(genre, producer, cast, synopsis, age):
    """ List upcoming movies based on genre,producer,cast,synopsis and age
    :param: genre requested by the costumer
    :param: producer requested by the costumer
    :param: cast member or members requested by the costumer
    :param: synopsis/details of the movie given by the costumer
    :param: age limit requested by the costumer
    """
    movies = Movie.objects.filter(
        genre__name__icontains=genre,
        producer__icontains=producer,
        age_rating_id__lte=age
    )

    if cast != []:
        movies = movies.filter(reduce(operator.and_, (Q(cast__icontains=actor) for actor in cast)))
    
    if synopsis != []:
        movies = movies.filter(reduce(operator.and_, (Q(synopsis__icontains=term) for term in synopsis)))

    return movies_queryset_to_array(movies, full_description=True)


def upcoming_releases():
    """ List upcoming releases
    """
    movies = Movie.objects.filter(released=False)
    return movies_queryset_to_array(movies)


def get_movie_details(movie):
    """ Retrieve the details of a movie
    :param: movie query
    """
    movies = Movie.objects \
                  .filter(Q(original_title__icontains=movie) | Q(title_pt__icontains=movie)).values_list('original_title')
    return movies_queryset_to_array(movies, full_description=True)


def get_sessions_by_movie(date, time, movie, search_term="", coordinates=[]):
    """ Get all sessions of a movie in a set of cinemas
    :param: date of the sessions to search for
    :param: minimum start time for the sessions
    :param: movie query
    :param: query for the cinema
    :param: user location
    """
    movies_matched = Movie.objects \
                          .filter(Q(original_title__icontains=movie) | Q(title_pt__icontains=movie)).values_list('original_title')
    
    sessions = filter_sessions_by_datetime(date, time, MID_DAY_S, search_term, coordinates) \
                .filter(movie__in=movies_matched) \
                .values_list('movie', 'start_date', 'start_time', 'purchase_link', 'cinema__name')

    res = {}
    for session in sessions:
        session_object = {'Start date': str(session[1]),
                          'Start time': str(session[2]),
                          'Ticket link' : session[3]}
        res[session[-1]] = res.get(session[-1], {})
        res[session[-1]][session[0]] = {'sessions': res[session[-1]].get(session[0], {'sessions':[]})['sessions'] + [session_object]}
    
    return res
