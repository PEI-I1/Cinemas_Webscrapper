from django.urls import path, include
from . import views

urlpatterns = [
    path('movies', views.list_movies),
    
    path('test1', views.test1),
    path('all_cinemas', views.all_cinemas),
    path('all_movies', views.all_movies),
    
    path('req1', views.req1),
    path('req2', views.req2),
    path('req3', views.req3),
    path('req4', views.req4), #TODO
    path('req5', views.req5),
    path('req6', views.req6),
    path('req7', views.req7),
    path('req8', views.req8),
    path('req9', views.req9),
    path('req10',views.req10),
    path('req11',views.req11),
    path('req12',views.req12), #TODO
    path('req13',views.req13), #TODO

]
