from django.shortcuts import render
from . import request_handler

# Create your views here.
def list_movies(request):
    request_handler.updateMovieSessions()
