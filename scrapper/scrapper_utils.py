from django.conf import settings
import requests
import re
from bs4 import BeautifulSoup
import json
import math 

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
        #getMovie(settings.NOS_CINEMAS_URL + movies[0]['href'])

    else:
        print("Não foi possível obter a lista de filmes")

    return movies_objects

def getMovie(movie_link, debut):
    r = requests.get(movie_link)
    #print(movie_link)
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
        #print('----> ' + day)
        
        sessions_line = day_schedule.find_all('article', {'class': 'line'})
        for session_line in sessions_line:
            cinema = session_line.find('div', {'class': 'cinema'}).get_text().strip()
            room = session_line.find('div', {'class': 'room'}).get_text().strip()
            #print(cinema + ', ' + room)
            sessions = session_line.find('div', {'class': 'hours'}).find_all('a')
            for session in sessions:
                hours = re.sub(r'\s+.*', '', session.get_text().strip())
                link = session['href']

                session_object = {
                        'cinema': cinema,
                        'room': re.sub(r'Sala ', '', room),
                        'date': day,
                        'hours': hours,
                        'purchase_link': link,
                        'availability': 0 #available_seats
                }
                sessions_objects.append(session_object)                
                # getSessionAvailability(link) TODO: move me

    #for s in sessions_objects:
        #print(s)
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


#FIXME
def getSessionAvailability(link):
    """ Get number of available seats for a given session
    """
    r = requests.get(link)
    if (r.status_code == 200):
        soup = BeautifulSoup(r.text, 'html5lib')
        available_seats = soup.find('tfoot').find('div', {'class': 'right'}).find('span', {'class': 'number'}).get_text()
        print('\t' + hours + '  ' + link + '  ' + available_seats + ' lugares')
    else:
        print("Não foi possível obter o número de lugares disponíveis para a sessão")

def distance(p1X,p1Y,p2X,p2Y):
    """ Get distance between 2 localizations based on both coordinates 
    :param: X of first localization
    :param: Y of first localization
    :param: X of second localization
    :param: T of second localization
    """
    dist = math.sqrt( ((p1X-p2X)**2)+((p1Y-p2Y)**2) )
    return dist 
