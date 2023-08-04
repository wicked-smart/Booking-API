from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def index(request):
    return HttpResponse("Hello, World!!!!")


def test_index(request, foo):
    response_str= "You Just Enterd This Value := " + str(foo)
    return HttpResponse(response_str)


def blog(request, slug):
    response_str= "Your Slug is := " + slug
    return HttpResponse(response_str)
