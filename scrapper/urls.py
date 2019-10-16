from django.urls import path, include
from . import views

urlpatterns = [
    path('movies', views.list_movies)
]
