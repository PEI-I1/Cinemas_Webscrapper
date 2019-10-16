from .models import *
from .scrapper_utils import getMovies, getNextDebuts
from datetime import datetime

def updateMovieSessions():
    """ Periodic task to fetch the latest session and movie info
    """
    movie_dump = getMovies()

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
            released = movie['debut'],
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

def next_sessions(coordinates):
    """ List upcoming movie sessions taking place near the user
    :param: coordinates user coordinates
    """
    time = time.now()
