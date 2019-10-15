import requests
import re
from bs4 import BeautifulSoup
import json

nos_cinemas_url = 'http://cinemas.nos.pt'
movies_link = nos_cinemas_url + '/pages/cartaz.aspx'

def getMovies():

    r = requests.get(movies_link)
    if (r.status_code == 200):
        soup = BeautifulSoup(r.text, 'html5lib')
        movies_html = soup.find('ul', {'class': 'drop-list masterBorderColor'})
        movies = movies_html.find_all('a', {'class': 'list-item'})
        #for movie in movies:
        #    getMovie(nos_cinemas_url + movie['href'])
        getMovie(nos_cinemas_url + movies[0]['href'])

    else:
        print("Não foi possível obter a lista de filmes")

def getMovie(movie_link):

    r = requests.get(movie_link)
    #print(movie_link)
    if (r.status_code == 200):
        soup = BeautifulSoup(r.text, 'html5lib')
        details = soup.find('section', {'class': 'details container--fixed'})

        banner = nos_cinemas_url + details.find('article', {'class': 'details--left'}).find('img')['src']
        
        trailer = details.find('a', {'class': 'masterTextColor trailerButton', 'target': '_blank'})
        if trailer:
            trailer = trailer['href']
        
        movie_header = details.find('div', {'class': 'info'})
        title = movie_header.find('h1').get_text().strip()
        age = movie_header.find('h2', {'class': 'subheadline'}).get_text().strip()

        general_descriptions = details.find('section', {'class': 'description'}).find_all('p')
        d = []
        for detail in [0, 2, 3, 4, 8]:
            text = general_descriptions[detail].get_text().strip()
            t = re.sub(r'[^:]*:\s', '', text)
            d.append(t)
        genre = d[0]
        original_title = d[1]
        producer = d[2]
        actors = d[3]
        duration = d[4]

        synopsis = details.find('section', {'class': 'sinopse'}).find('div', {'class': 'ms-rtestate-field'}).get_text()
        synopsis = re.sub(r'\s+', ' ', synopsis)

        schedule_html = soup.find('section', {'class': 'schedule'}).find_all('section', {'class': 'table is-hidden display-none'})
        schedule = getSchedule(schedule_html)

        movie_object = {
            'title': title,
            'original_title': original_title,
            'genre': genre,
            'producer': producer,
            'actors': actors,
            'duration': duration,
            'synopsis': synopsis,
            'trailer_url': trailer,
            'banner_url': banner
        }

        print(movie_object)

    else:
        print("Não foi possível obter as informações do filme")

def getSchedule(schedule_html):

    sessions_objects = []
    
    for day_schedule in schedule_html:
        day = re.sub(r'normal ', '', day_schedule['data-id'])
        print('----> ' + day)
        
        sessions_line = day_schedule.find_all('article', {'class': 'line'})
        for session_line in sessions_line:
            cinema = session_line.find('div', {'class': 'cinema'}).get_text().strip()
            room = session_line.find('div', {'class': 'room'}).get_text().strip()
            print(cinema + ', ' + room)
            sessions = session_line.find('div', {'class': 'hours'}).find_all('a')
            for session in sessions:
                hours = re.sub(r'\s+.*', '', session.get_text().strip())
                link = session['href']

                r = requests.get(link)
                if (r.status_code == 200):
                    soup = BeautifulSoup(r.text, 'html5lib')
                    available_seats = soup.find('tfoot').find('div', {'class': 'right'}).find('span', {'class': 'number'}).get_text()
                    print('\t' + hours + '  ' + link + '  ' + available_seats + ' lugares')

                    session_object = {
                        'cinema': cinema,
                        'room': re.sub(r'[^\d]', '', room),
                        'date': day,
                        'hours': hours,
                        'purchase_link': link,
                        'availability': available_seats
                    }

                    sessions_objects.append(session_object)
                
                else:
                    print("Não foi possível obter o número de lugares disponíveis para a sessão")

    for s in sessions_objects:
        print(s)


getMovies()