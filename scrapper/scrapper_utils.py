from django.conf import settings
from django.db.models import Q
import requests
import re
from bs4 import BeautifulSoup
import json
import math
from celery import shared_task, task
from .models import *
from datetime import datetime
import billiard as multiprocessing
from functools import partial

def getMovies():
    ''' Fetch information pertaining to all released movies
    '''
    r = requests.get(settings.MOVIES_LINK)
    movies_objects = []
    if (r.status_code == 200):
        try:
            soup = BeautifulSoup(r.text, 'html5lib')
            movies_html = soup.find('ul', {'class': 'drop-list masterBorderColor'})
            movies = [settings.NOS_CINEMAS_URL + movie['href']
                  for movie in movies_html.find_all('a', {'class': 'list-item'})]
            # partially apply getMovie
            getMoviePart = partial(getMovie, released=True)
        
            with multiprocessing.Pool(15) as proc_pool:
                movies_objects = proc_pool.map(getMoviePart, movies)
        except Exception as e:
            print(f"[getMovies] Error while parsing HTML {str(e)}")
            raise Exception(f"[getMovies] {str(e)}")

    else:
        print("[getMovies] Não foi possível obter a lista de filmes")
        raise Exception(f"GET {settings.MOVIES_LINK} returned unexpected response code: {r.status_code}")

    return list(filter(lambda x: x != None, movies_objects))

def getMovie(movie_link, released):
    ''' Get all information related to a movie
    :param: movie link
    :param: boolean indicating if the movie has been released
    '''
    r = requests.get(movie_link)
    if (r.status_code == 200):
        try:
            soup = BeautifulSoup(r.text, 'html5lib')
            details = soup.find('section', {'class': 'details container--fixed'})

            banner = settings.NOS_CINEMAS_URL + details.find('article', {'class': 'details--left'}).find('img')['src']
        
            trailer = details.find('a', {'class': 'masterTextColor trailerButton', 'target': '_blank'})
            if trailer:
                trailer = trailer['href'].strip()
            else:
                trailer = ''
        
            movie_header = details.find('div', {'class': 'info'})
            title = movie_header.find('h1').get_text().strip()
            age = re.sub(r'M', '', movie_header.find('h2', {'class': 'subheadline'}).get_text().strip())
            if age.isdigit():
                age = int(age)
            else:
                age = 18

            general_descriptions = details.find('section', {'class': 'description'}).find_all('p')
            d = []

            props = {r'Género': '',
                     r'Título Original': '',
                     r'Realizador' : '',
                     r'Actores' : '',
                     r'Ano' : '',
                     r'Duração (minutos)': 0}

            for detail in general_descriptions:
                prop, val = tuple(detail.get_text().strip().split(':', 1))
                if prop in props:
                    props[prop] = re.sub(r'^\s+', '', val)

            synopsis = details.find('section', {'class': 'sinopse'}).find('div', {'class': 'ms-rtestate-field'}).get_text()
            synopsis = re.sub(r'\s+', ' ', synopsis)

            schedule_html = soup.find('section', {'class': 'schedule'}).find_all('section', {'class': 'table is-hidden display-none'})

            imdb_rating = getIMDBRating(props[r'Título Original'], props[r'Ano'])
            # Too heavy for testing every time
            if released: 
                schedule = getSchedule(schedule_html)
            else:
                schedule = []

            movie_object = {
                'title': title,
                'original_title': props[r'Título Original'],
                'genre': props[r'Género'],
                'age': age,
                'producer': props[r'Realizador'],
                'actors': props[r'Actores'],
                'duration': int(props[r'Duração (minutos)']),
                'synopsis': synopsis,
                'trailer_url': trailer,
                'banner_url': banner,
                'released': released,
                'sessions': schedule,
                'imdb_rating': imdb_rating
            }
            
            return movie_object

        except Exception as e:
            print(f"[getMovie] Missing information when fetching movie info ({str(e)})")
            return None

    else:
        print("[getMovie] Invalid movie link")
        return None

def getIMDBRating(title, year):
    ''' Fetch IMDB rating using the original title
    :param: movie title
    :param: year of production
    :return: IMDB rating if available
    '''
    info_url = settings.OMDB_API_URL.format(settings.OMDB_API_KEY, title, year)
    r = requests.get(info_url)
    if r.status_code == 200:
        rating = r.json().get('imdbRating', 'N/A')
    else:
        rating = 'N/A'
    return rating


def getSchedule(schedule_html):
    ''' Get session information for a specific movie
    :param: HTML from which to extract session info
    '''
    sessions_objects = []
    
    for day_schedule in schedule_html:
        day = re.sub(r'normal ', '', day_schedule['data-id'])
        sessions_line = day_schedule.find_all('article', {'class': 'line'})
        for session_line in sessions_line:
            cinema_raw = session_line.find('div', {'class': 'cinema'})
            if cinema_raw:
                cinema = cinema_raw.get_text().strip()
                sessions_raw = session_line.find('div', {'class': 'hours'})
                if sessions_raw:
                    sessions = sessions_raw.find_all('a')
                    for session in sessions:
                        try:
                            hours = re.sub(r'\s+.*', '', session.get_text().strip())                        
                            link = session['href']
                            session_object = {
                                'cinema': cinema,
                                'date': day,
                                'hours': hours,
                                'purchase_link': link,
                            }
                            sessions_objects.append(session_object)
                        except Exception as e:
                            print(f"[getSchedule] Error when fetching session {str(e)}")
    return sessions_objects


def getNextDebuts():
    ''' Get information about new releases
    '''
    r = requests.get(settings.NOS_CINEMAS_URL)
    movies_objects = []
    if (r.status_code == 200):
        try:
            soup = BeautifulSoup(r.text, 'html5lib')
            script_div = soup.find('div', {'id': 'MSOZoneCell_WebPartWPQ4'})
            if script_div:
                script = script_div.find('script', {'type': 'text/javascript'})
                if script:
                    moviesData = re.findall(r'moviesData = {(.*)};', script.get_text())
                    if moviesData and len(moviesData) > 0:
                        movies_json = json.loads('{' + moviesData[0] + '}')
                        for movie in movies_json['Estreias']:
                            m = getMovie(settings.NOS_CINEMAS_URL + movie['movieLink'], False)
                            movies_objects.append(m)
        except Exception as e:
            raise Exception(f"[getNextDebuts] Error while parsing HTML: {str(e)}")
    else:
        print("[getNextDebuts] Não foi possível obter a lista de próximas estreias")
        raise Exception(f"GET {settings.NOS_CINEMAS_URL} returned unexpected response code: {r.status_code}")

    return movies_objects


def updateSessionsAvailability(date):
    ''' Fetch availability for sessions after the given date
    :param: lower limit for session date
    '''
    print('[updateSessionsAvailability] Updating session information...')
    sessions = Session.objects \
                            .filter(start_date__gte=date) \
                            .all()
    
    p = multiprocessing.Pool(processes=15)
    sessions_updated = p.map(getSessionAvailability, sessions)
    Session.objects.bulk_update(sessions_updated, ['availability'])
    print('[updateSessionsAvailability] Sessions updated!')


def getSessionAvailability(session):
    """ Get number of available seats for a given session
    :param: Link to purchase ticket for a session
    :return: number of available seats
    """
    r = requests.get(session.purchase_link)
    if (r.status_code == 200):
        try:
            soup = BeautifulSoup(r.text, 'html5lib')
            tmp = soup.find('tfoot')
            if tmp:
                tmp = tmp.find('div', {'class': 'right'})
                if tmp:
                    tmp = tmp.find('span', {'class': 'number'})
                    if tmp:
                        availability = int(tmp.get_text())
                        session.availability = availability
        except Exception as e:
            print(f"[getSessoinAvailability] Error while parsing HTML {str(e)}")
    return session


@task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 5})
def updateDatabase(self):
    ''' Periodic database update
    '''
    today = datetime.today()
    time = today.strftime("%H:%M:%S")
    date = today.strftime("%Y-%m-%d")
    
    if today.weekday() == 3 and (time >= '05:00:00' and time < '06:00:00'):
        updateMovieSessions()
    updateSessionsAvailability(date)

    
def updateDatabaseStartup():
    ''' Startup update
    '''
    try:
        updateMovieSessions()
        today = datetime.today()
        date = today.strftime("%Y-%m-%d")
        updateSessionsAvailability(date)
    except Exception as e:
        print(f"[updateDatabaseStartup] Error while updating movie info ({str(e)})")
    
                    
def updateMovieSessions():
    """ Fetch the latest session and movie info to update the database
    """
    print("[updateMovieSessions] Updating database")
    movie_dump = getMovies()
    debuts_dump = getNextDebuts()

    for debut in debuts_dump:
        movie_dump.append(debut)

    movies_array = []
    sessions_array = []

    for movie in movie_dump:
        
        age_rating = AgeRating.objects.all().filter(age = movie['age'])
        if len(age_rating) == 0:
            age_rating = AgeRating(age = movie['age'])
            age_rating.save()
            print('[updateMovieSessions] NOVA IDADE ADICIONADA')
        else:
            age_rating = age_rating[0]
        
        genre = Genre.objects.all().filter(name = movie['genre'])
        if len(genre) == 0:
            genre = Genre(name = movie['genre'])
            genre.save()
            print('[updateMovieSessions] NOVO GÉNERO ADICIONADO')
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
            released = movie['released'],
            imdb_rating = movie['imdb_rating'],
            age_rating = age_rating,
            genre = genre
        )
        
        movies_array.append(movie_entry)

        for session in movie['sessions']:

            cinema = Cinema.objects.all().filter(name = session['cinema'])
            if len(cinema) > 0:
                cinema = cinema[0]
            else:
                cinema = Cinema.objects.all().filter(alt_name = session['cinema'])[0]

            session_entry = Session(
                start_date = datetime.strptime(session['date'], '%Y-%m-%d'),
                start_time = datetime.strptime(session['hours'], '%Hh%M'),
                purchase_link = session['purchase_link'],
                movie = movie_entry,
                cinema = cinema,
                availability = 0
            )

            sessions_array.append(session_entry)
    try:
        Session.objects.all().delete()
        Movie.objects.all().delete()
        Movie.objects.bulk_create(movies_array, ignore_conflicts=True)
        Session.objects.bulk_create(sessions_array)
        print("[updateMovieSessions] Update complete")
    except Exception as e:
        raise Exception(f"[updateMovieSessions] Database update raised: {str(e)}")

