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

def getMovies():
    r = requests.get(settings.MOVIES_LINK)
    movies_objects = []
    if (r.status_code == 200):
        soup = BeautifulSoup(r.text, 'html5lib')
        movies_html = soup.find('ul', {'class': 'drop-list masterBorderColor'})
        movies = movies_html.find_all('a', {'class': 'list-item'})
        for movie in movies:
            m = getMovie(settings.NOS_CINEMAS_URL + movie['href'], False)
            movies_objects.append(m)

    else:
        print("Não foi possível obter a lista de filmes")

    return movies_objects

def getMovie(movie_link, debut):
    r = requests.get(movie_link)
    if (r.status_code == 200):
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
                 r'Duração (minutos)': 0}

        for detail in general_descriptions:
            prop, val = tuple(detail.get_text().strip().split(':', 1))
            if prop in props:
                props[prop] = re.sub(r'^\s+', '', val)

        synopsis = details.find('section', {'class': 'sinopse'}).find('div', {'class': 'ms-rtestate-field'}).get_text()
        synopsis = re.sub(r'\s+', ' ', synopsis)

        schedule_html = soup.find('section', {'class': 'schedule'}).find_all('section', {'class': 'table is-hidden display-none'})
        
        # Too heavy for testing every time
        if not debut: 
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
            'debut': debut,
            'sessions': schedule
        }

        return movie_object

    else:
        print("Não foi possível obter as informações do filme")

def getSchedule(schedule_html):

    sessions_objects = []
    
    for day_schedule in schedule_html:
        day = re.sub(r'normal ', '', day_schedule['data-id'])
        
        sessions_line = day_schedule.find_all('article', {'class': 'line'})
        for session_line in sessions_line:
            cinema = session_line.find('div', {'class': 'cinema'}).get_text().strip()
            sessions = session_line.find('div', {'class': 'hours'}).find_all('a')
            for session in sessions:
                hours = re.sub(r'\s+.*', '', session.get_text().strip())
                link = session['href']
                session_object = {
                        'cinema': cinema,
                        'date': day,
                        'hours': hours,
                        'purchase_link': link,
                }
                sessions_objects.append(session_object)
                
    return sessions_objects

def getNextDebuts():
    r = requests.get(settings.NOS_CINEMAS_URL)
    movies_objects = []
    if (r.status_code == 200):
        soup = BeautifulSoup(r.text, 'html5lib')
        script = soup.find('div', {'id': 'MSOZoneCell_WebPartWPQ1'}).find('script', {'type': 'text/javascript'}).get_text()
        moviesData = re.findall(r'moviesData = {(.*)};', script)[0]
        movies_json = json.loads('{' + moviesData + '}')
        for movie in movies_json['Estreias']:
            m = getMovie(settings.NOS_CINEMAS_URL + movie['movieLink'], True)
            movies_objects.append(m)

    else:
        print("Não foi possível obter a lista de próximas estreias")

    return movies_objects


def updateSessionsAvailability(date):
    print('Update started...')
    purchase_links = Session.objects \
                            .filter(start_date__gte=date) \
                            .values_list('purchase_link', flat=True)
    
    p = multiprocessing.Pool(processes=15)
    sessions_updated = p.map(getSessionAvailability, purchase_links)
    Session.objects.bulk_update(sessions_updated, ['availability']);
    print('Update completed!')


def getSessionAvailability(link):
    """ Get number of available seats for a given session
    :param: Link to purchase ticket for a session
    :return: number of available seats
    """
    r = requests.get(link)
    session = Session.objects.get(purchase_link=link)
    if (r.status_code == 200):
        soup = BeautifulSoup(r.text, 'html5lib')
        #available_seats = soup.find('tfoot').find('div', {'class': 'right'}).find('span', {'class': 'number'}).get_text()
        tmp = soup.find('tfoot')
        if tmp:
            tmp = tmp.find('div', {'class': 'right'})
            if tmp:
                tmp = tmp.find('span', {'class': 'number'})
                if tmp:
                    availability = int(tmp.get_text())
                    session.availability = availability
    return session

@task(bind=True)
def updateDatabase(self):
    today = datetime.today()
    time = today.strftime("%H:%M:%S")
    date = today.strftime("%Y-%m-%d")
    
    if today.weekday() == 3 and (time >= '05:00:00' and time < '06:00:00'):
        updateMovieSessions()
    updateSessionsAvailability(date)
        
                    
def updateMovieSessions():
    """ Fetch the latest session and movie info to update the database
    """
    print("Updating database")
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

    Session.objects.all().delete()
    Movie.objects.all().delete()
    Movie.objects.bulk_create(movies_array, ignore_conflicts=True)
    Session.objects.bulk_create(sessions_array, ignore_conflicts=True)
    print("Update complete")
