from django.urls import path, include
from . import views

urlpatterns = [
    path('movies', views.list_movies),
    
    path('test1', views.test1),
    path('all_cinemas', views.all_cinemas),
    path('all_movies', views.all_movies),
    
    path('req37', views.req37),
    path('req38', views.req38),
    path('req39', views.req39),
    #path('req40', views.req40),
    #path('req41', views.req40),
    path('req42', views.req42),
    path('req43', views.req43),
    path('req44', views.req44),
    path('req45', views.req45),
    path('req46', views.req46),
    path('req47', views.req47),
    #path('req48', views.req48),
    #path('req49', views.req49),

]
