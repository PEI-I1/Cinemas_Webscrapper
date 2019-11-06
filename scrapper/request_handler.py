from .models import *
from .scrapper_utils import getMovies, getNextDebuts, distance
import time
from datetime import datetime, date, time, timedelta
from django.db.models import Q
from functools import reduce
import operator

MID_DAY_S = time(12, 0, 0).strftime('%H:%M:%S')

def updateMovieSessions():
    """ Periodic task to fetch the latest session and movie info
    """
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
                availability = session['availability'],
                technology = 'normal',
                room = session['room'],
                purchase_link = session['purchase_link'],
                movie = movie_entry,
                cinema = cinema
            )

            session_entry.save()


def closest_cinema(coordinates=[]):
    cinemas = Cinema.objects.all()
    minDist = -1
    closest_cinema = {}
    for cinema in cinemas:
        cinemaCoord = cinema.coordinates.strip().split(',', 1)
        
        dist = distance(coordinates[0],coordinates[1],float(cinemaCoord[0]),float(cinemaCoord[1]))
        if  dist < minDist or minDist==-1 :
            minDist=dist
            closest_cinema = cinema

    return closest_cinema.coordinates,closest_cinema.name

def find_cinemas(search_term=""):
    cinemas = Cinema.objects.all()
    cinemas_response = []
    for cinema in cinemas:
        st = search_term.lower()
        if st in cinema.name.lower() or st in cinema.alt_name.lower() or st in cinema.city.lower():
            cinemas_response.append((cinema.coordinates, cinema.name))
    return cinemas_response

def movies_of_cinemas(cinemas_coordinates):
    cinemas = Cinema.objects \
                    .values_list('coordinates', 'name') \
                    .filter(coordinates__in=cinemas_coordinates)
    res = {}

    for cinema in cinemas:
        movie_titles = list(set(Session.objects.filter(cinema=cinema[0]).values_list('movie', flat=True)))
        res[cinema[1]] = movie_titles
    return res

def get_movies_by_cinema(search_term="", coordinates=[]):
    cinemas = get_matching_cinemas(search_term, coordinates)
    movies = movies_of_cinemas([cinema[0] for cinema in cinemas])
    return movies


def get_matching_cinemas(search_term="", coordinates = []):
    """ Return the coordinates of all the matching cinemas
    :param:
    :param:
    :return: list of cinema coordinates
    """
    if search_term:
        cinemas = find_cinemas(search_term)
    else:
        cinemas = [closest_cinema(coordinates)]
    print(cinemas)
    return cinemas


def get_sessions_by_date(search_term="", coordinates=[], date = datetime.now().strftime('%Y-%m-%d'), time = time(12, 0, 0).strftime('%H:%M:%S')):
    sessions = filter_sessions_by_datetime(search_term, coordinates, date, time).values_list('start_date', 'start_time', 'purchase_link', 'availability', 'cinema__name', 'movie')
    res = {}
    for session in sessions:
        session_object = {'Start date': str(session[0]),
                          'Start time': str(session[1]),
                          'Ticket link': session[2],
                          'Availability': session[3]}
        res[session[-2]] = res.get(session[-2], {})
        res[session[-2]][session[-1]] = {'sessions': res[session[-2]].get(session[-1], {'sessions':[]})['sessions'] + [session_object]}
    return res
    

def filter_sessions_by_datetime(search_term="", coordinates=[], date = datetime.now().strftime('%Y-%m-%d'), time = time(12, 0, 0).strftime('%H:%M:%S')):
    """ TODO
    """
    cinemas = get_matching_cinemas(search_term, coordinates)
    sessions = Session.objects.filter(start_date=date,
                                  cinema__in=[cinema[0] for cinema in cinemas])
    return sessions.filter(Q(start_time__gte=time) | Q(start_time__lte = MID_DAY_S))

def get_sessions_by_duration(duration, search_term = "", coordinates = [], date = datetime.now().strftime('%Y-%m-%d'), time = time(12, 0, 0).strftime('%H:%M:%S')):
    """ TODO
    """
    sessions = filter_sessions_by_datetime(search_term, coordinates, date, time)
    movies_ud = Movie.objects.filter(length__lte=duration).values_list('original_title')
    sessions = sessions.filter(movie__in=movies_ud).values_list('start_date', 'start_time', 'purchase_link', 'availability', 'cinema__name', 'movie', 'movie__length')
    res = {}
    for session in sessions:
        session_object = {'Start date': str(session[0]),
                          'Start time': str(session[1]),
                          'Ticket link': session[2],
                          'Availability': session[3]}
        res[session[-3]] = res.get(session[-3], {})
        res[session[-3]][session[-2]] = {'Length (min)': session[-1], 'sessions': res[session[-3]].get(session[-2], {'sessions':[]})['sessions'] + [session_object]}
    return res
    

def next_sessions(search_term="", coordinates=[]):
    """ List upcoming sessions taking place near the user based on current date
    :param: coordinates in list like [41,7]
    """
    now = datetime.today()
    current_time = now.strftime("%H:%M:%S")

    if current_time < '05:00:00': #account for sessions past mid-night
        take_one_day = timedelta(days = -1)
        now = now + take_one_day
    
    current_date = now.strftime("%Y-%m-%d")

    sessions = filter_sessions_by_datetime(search_term, coordinates, date=current_date, time=current_time).values_list('movie', 'start_date', 'start_time', 'purchase_link', 'availability', 'cinema__name')

    res = {}
    for session in sessions:
        session_object = {'Start date': str(session[1]),
                          'Start time': str(session[2]),
                          'Ticket link' : session[3],
                          'Availability': session[4]}
        res[session[-1]] = res.get(session[-1], {})
        res[session[-1]][session[0]] = {'sessions': res[session[-1]].get(session[0], {'sessions':[]})['sessions'] + [session_object]}
    return res

def next_movies(coordinates=[]):
    """ List upcoming movies taking place near the user based on current date
    :param: coordinates in list like [41,7]
    """
    next_movies_list=[]
    next_sessions_list = next_sessions(coordinates)
    for session in next_sessions_list:
        next_movies_list.append(session.movie)
    next_movies_list = list(dict.fromkeys(next_movies_list))
    return next_movies_list

    
def next_movies_by_duration(duration,coordinates=[]):
    """ List upcoming movies with less duration than given 
    :param: duration given by costumer in minutes
    :param: coordinates in list like [41,7]
    """ 
    next_movies_list = next_movies(coordinates)
    movies_results = []
    for movie in next_movies_list:
        if movie.length<=duration :
            movies_results.append(movie)
    movies_results = list(dict.fromkeys(movies_results))
    return movies_results

def movies_queryset_to_array(movies, full_description = False):
    if full_description:
        movies = movies.values_list('original_title', 'cast', 'genre__name', 'banner_url', 'producer', 'synopsis', 'length', 'trailer_url', 'released', 'title_pt', 'age_rating')
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

def search_movies(genre="", producer="", cast=[], synopsis=[], age=18):
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

    return movies_queryset_to_array(movies)

def upcoming_releases():
    """ List upcoming releases
    """
    movies = Movie.objects.filter(released=False)
    return movies_queryset_to_array(movies)

def get_movie_details(movie=""):
    """ TODO
    """
    movies = Movie.objects.filter(Q(original_title__icontains=movie) | Q(title_pt__icontains=movie)).values_list('original_title')
    return movies_queryset_to_array(movies, full_description=True)

def get_sessions_by_movie(movie="", search_term="", coordinates=[], date = datetime.now().strftime('%Y-%m-%d'), time = time(12, 0, 0).strftime('%H:%M:%S')):
    """ TODO
    """

    movies_matched = Movie.objects.filter(Q(original_title__icontains=movie) | Q(title_pt__icontains=movie)).values_list('original_title')
    
    sessions = filter_sessions_by_datetime(search_term, coordinates, date, time) \
                .filter(movie__in=movies_matched) \
                .values_list('movie', 'start_date', 'start_time', 'purchase_link', 'availability', 'cinema__name')

    res = {}
    for session in sessions:
        session_object = {'Start date': str(session[1]),
                          'Start time': str(session[2]),
                          'Ticket link' : session[3],
                          'Availability': session[4]}
        res[session[-1]] = res.get(session[-1], {})
        res[session[-1]][session[0]] = {'sessions': res[session[-1]].get(session[0], {'sessions':[]})['sessions'] + [session_object]}
    
    return res
