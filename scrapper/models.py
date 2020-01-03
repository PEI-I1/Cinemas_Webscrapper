from django.db import models

class Cinema(models.Model):
    """ Cinema
    """
    coordinates = models.CharField(max_length=32, primary_key=True)
    alt_name = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    city = models.CharField(max_length=32)


class Session(models.Model):
    """ Movie exhibition
    """
    purchase_link = models.CharField(max_length=256, primary_key=True)
    start_date = models.DateField()
    start_time = models.TimeField()
    availability = models.IntegerField(default=0)
    movie = models.ForeignKey(
        'Movie',
        on_delete=models.CASCADE,
    )
    cinema = models.ForeignKey(
    	'Cinema',
    	on_delete=models.CASCADE)

class Movie(models.Model):
    """ Movie
    """
    original_title = models.CharField(max_length=32, primary_key=True)
    title_pt = models.CharField(max_length=32)
    producer = models.CharField(max_length=32)
    cast = models.TextField()
    synopsis = models.TextField()
    length = models.IntegerField()
    trailer_url = models.CharField(max_length=128)
    banner_url = models.CharField(max_length=128)
    released = models.BooleanField()
    imdb_rating = models.FloatField()
    age_rating = models.ForeignKey(
        'AgeRating',
        on_delete=models.CASCADE
    )
    genre = models.ForeignKey(
        'Genre',
        on_delete=models.CASCADE
    )
       

class AgeRating(models.Model):
    """ Age restriction 
    """
    age = models.IntegerField(primary_key=True)

class Genre(models.Model):
    """ Movie genre
    """
    name = models.CharField(max_length=32)
