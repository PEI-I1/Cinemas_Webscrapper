from django.urls import path, include
from . import views

urlpatterns = [
    path('movies', views.update_DB),
    
    path('movies/by_cinema', views.get_movies_by_cinema),
    path('sessions/by_duration', views.get_sessions_by_duration),
    path('req3', views.req3),
    path('req4', views.req4),
    path('req5', views.req5),
    path('req6', views.req6),
    path('req7', views.req7),
    path('req8', views.req8),
    path('req9', views.req9),
    path('req10',views.req10),
    path('req11',views.req11),
    path('req13',views.req13),
]

# 1  - O utilizador deve poder consultar os filmes em exibicao num determinado cinema.
# 2  - O utilizador deve poder consultar sessões de filmes com uma determinada duração.
# 3  - O utilizador deve poder consultar as proximas sessões num determinado cinema.
# 4  - O utilizador deve poder consultar as próximas sessões de um determinado filme.
# 5  - O utilizador deve poder consultar as sessões numa determinada data.
# 6  - O utilizador deve poder consultar filmes de determinado género.
# 7  - O utilizador deve poder consultar filmes de determinado realizador.
# 8  - O utilizador deve poder consultar filmes com base no elenco.
# 9  - O utilizador deve poder consultar filmes de acordo com a sua sinopse.
# 10 - O utilizador deve poder consultar filmes com base em restrições de idade.
# 11 - O utilizador deve poder consultar as próximas estreias.
# 12 - O utilizador deve ser capaz de consultar os lugares livres por sessão.
# 13 - O utilizador deve ser capaz de consultar os detalhes de um determinado filme.
