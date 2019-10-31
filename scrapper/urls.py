from django.urls import path, include
from . import views

urlpatterns = [
    path('movies', views.list_movies),
    path('test1',views.test1),
    path('test2',views.test2),
    path('test3',views.test3),
    path('test4',views.test4),
    path('req37',views.req37),
    path('req38',views.req38),
    path('req39',views.req39),
]
