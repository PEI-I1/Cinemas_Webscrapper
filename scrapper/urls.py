from django.urls import path, include
from . import views

urlpatterns = [
    path('movies', views.update_DB),
    path('cinemas/search', views.get_matching_cinemas),
    path('movies/by_cinema', views.get_movies_by_cinema),
    path('sessions/by_duration', views.get_sessions_by_duration),
    path('sessions/next_sessions', views.next_sessions),
    path('sessions/by_movie', views.get_sessions_by_movie),
    path('sessions/by_date', views.get_sessions_by_date),
    path('movies/search', views.search_movies),
    path('movies/releases',views.upcoming_releases),
    path('movies/details',views.get_movie_details),
]
