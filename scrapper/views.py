from django.shortcuts import render
from . import request_handler

# Create your views here.
def list_movies(request):
    request_handler.updateMovieSessions()

# Test function here.
def test(request):
    print("TESTE:--------------------------")
    print(request_handler.next_sessions_specific_movie(original_title="JOke",date="2019-10-18",time="00:25:00",location="Forum Coimbra"))