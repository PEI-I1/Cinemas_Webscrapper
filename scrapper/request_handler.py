from .models import *
from .scrapper_utils import getMovies, getNextDebuts, distance
import time
from datetime import datetime, date, time, timedelta
from django.db.models import Q

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

    return closest_cinema.coordinates

def find_cinemas(search_term=""):
    cinemas = Cinema.objects.all()
    cinemas_response = []
    for cinema in cinemas:
        st = search_term.lower()
        if st in cinema.name.lower() or st in cinema.alt_name.lower() or st in cinema.city.lower():
            cinemas_response.append(cinema.coordinates)
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
    print(cinemas)
    movies = movies_of_cinemas(cinemas)
    return movies

def get_sessions_by_date(cinemas_coordinates, date):
    """ Get sessions taking placing in a cinema on a given date
    :param: cinema coordinates
    :param: date 
    """
    return Session.objects.filter(start_date=date, cinema__in=cinemas_coordinates)                     


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
    return cinemas

def get_sessions_by_duration(date, duration, search_term ="", coordinates = []):
    """ 
    :param: Duration limit
    """
    cinemas = get_matching_cinemas(search_term, coordinates)
    movies_ud = Movie.objects.filter(length__lte=duration).values_list('original_title', 'length')
    sessions = get_sessions_by_date(cinemas, date)
    res = {}
    for movie in movies_ud:
        raw_movie_sessions = sessions.filter(movie=movie[0]).values_list('start_date', 'start_time', 'purchase_link')
        movie_sessions = [{'Start date': str(raw_session[0]),
                           'Start time': str(raw_session[1]),
                           'Ticket link': raw_session[2]}
                          for raw_session in raw_movie_sessions]
        res[movie[0]] = {'length': movie[1], 'sessions': movie_sessions}

    return res
    

def next_sessions(search_term="", coordinates=[]):
    """ List upcoming sessions taking place near the user based on current date
    :param: coordinates in list like [41,7]
    """
    next_sessions = []
    cinemas = get_matching_cinemas(search_term, coordinates)
    
    now = datetime.today()
    current_time = now.strftime("%H:%M:%S")
    past_mid_night = current_time[0] == '0' and int(current_time[1]) < 5

    if past_mid_night: #in cinemas nos website past mid-night sessions are still in the previous day , so we need to subtract one day if its past mid-night
        take_one_day = timedelta(days = -1)
        now = now + take_one_day
    
    current_date = now.strftime("%Y-%m-%d")

    sessions = Session.objects.filter(cinema__in = cinemas, start_date = current_date, start_time__gte = current_time)
    # FIX: example 01h00 is smaller than 16h00
    
    res = {}
    for cinema in cinemas:
        sessions = list(set(Session.objects.filter(cinema=cinema[0]).values_list('movie', 'start_time', 'purchase_link', flat=True)))
        res[cinema[1]] = sessions
    return res
    
    """for session in sessions:

        session_is_past_midnight = str(session.start_time)[0]=='0' and int(str(session.start_time)[1])<5
        session_before_current_before =  not session_is_past_midnight and not past_mid_night and session.start_time > now.time() 
        session_after_current_before =  session_is_past_midnight and not past_mid_night and True
        session_before_current_after =  not session_is_past_midnight and past_mid_night and False 
        session_after_current_after =  session_is_past_midnight and past_mid_night and session.start_time > now.time() 

        if session_before_current_before or session_after_current_before or session_before_current_after or session_after_current_after:
            next_sessions_list.append(session)
    return next_sessions_list"""

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
    
    
def get_movies(genre="",producer="",cast="",synopsis="",age=18):
    """ List upcoming movies based on genre,producer,cast,synopsis and age
    :param: genre requested by the costumer
    :param: producer requested by the costumer
    :param: cast member or members requested by the costumer
    :param: synopsis/details of the movie given by the costumer
    :param: age limit requested by the costumer
    """
    movies = Movie.objects.filter(  genre__name__icontains=genre,
                                    producer__icontains=producer,
                                    cast__icontains=cast,
                                    synopsis__icontains=synopsis,
                                    age_rating_id__lte=age
                                )
    """
    #prints for testing 
    print("MOVIES-----------------------")
    for m in movies:
        print(m.original_title)
    """ 
    return movies
def upcoming_releases():
    """ List upcoming releases
    """
    movies = Movie.objects.filter( released=False)
    movies = list(dict.fromkeys(movies))
    return movies

def available_seats(session_id):
    """ Available seats of un specific session
    :param: id of session
    """
    session = Session.objects.get(pk=session_id)
    return session.availability

def movie_details(original_title):
    """ Movies details of un specific movie
    :param: original_title of movie (primarykey)
    """
    movie = Movie.objects.get(pk=original_title)
    return movie.synopsis

def next_sessions_specific_movie(original_title,date="",time="",location=""):
    """ List upcoming sessions taking by the given location,date and movie
    :param: original_title of movie (primarykey)
    :param: date given by costumer ("%yyyy-%mm-%dd")
    :param: time given by costumer ("hh:mm:ss")
    :param: location given by costumer (city or name of cinema)
    """
    sessions = Session.objects.filter(
                                        movie__original_title__icontains=original_title,
                                    )
    sessions = sessions.filter( Q(cinema__name__icontains=location) | Q(cinema__alt_name__icontains=location) | Q(cinema__city__icontains=location) )
    
    if (date!=""): 
        sessions= sessions.filter( start_date = date)
    
    if (time!=""):
        now = datetime.strptime(time,'%H:%M:%S')

        past_mid_night = str(time)[0]=='0' and int(str(time)[1])<5
        next_sessions_list = []
        for session in sessions:
            session_is_past_midnight = str(session.start_time)[0]=='0' and int(str(session.start_time)[1])<5
            session_before_current_before =  not session_is_past_midnight and not past_mid_night and session.start_time > now.time()
            session_after_current_before =  session_is_past_midnight and not past_mid_night and True
            session_before_current_after =  not session_is_past_midnight and past_mid_night and False 
            session_after_current_after =  session_is_past_midnight and past_mid_night and session.start_time > now.time()

            if session_before_current_before or session_after_current_before or session_before_current_after or session_after_current_after:
                next_sessions_list.append(session)
        sessions = next_sessions_list

    """
    #testing
    print("LEN=" + str(len(sessions)) )
    for s in sessions:
        print("-------")
        print(s.start_time)
        print(s.start_date)
        print("--------")
    """

    return sessions
