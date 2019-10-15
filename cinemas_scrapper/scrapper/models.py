from django.db import models

class Cinema(models.Model):
    """ Cinema
    """
    coordinates = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=32)
    cidade = models.CharField(max_length=32)


class Session(models.Model):
    """ Movie exhibition
    """
    start_date = models.DateField()
    start_time = models.TimeField()
    availability = models.IntegerField()
    technology = models.CharField(max_length=32)
    movie = models.ForeignKey(
        'Movie',
        on_delete=models.CASCADE,
    )

class Movie(models.Model):
    """ Movie
    """
    original_title = models.CharField(max_length=32, primary_key=True)
    title_pt = models.CharField(max_length=32)
    producer = models.CharField(max_length=32)
    cast = models.TextField()
    synopsis = models.TextField()
    length = models.IntegerField()
    trailer_url = models.CharField(max_length=128) #TODO: max length
    banner = models.BinaryField()
    released = models.BooleanField()
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
    name = models.CharField(max_length=32, primary_key=True)
