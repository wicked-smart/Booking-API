from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from rest_framework.decorators import api_view
from flight.serializers import *
from rest_framework.response import Response
from rest_framework import status
from .models import *
from django.contrib.auth import authenticate, logout, login
from django.views.decorators.csrf import csrf_exempt


from django.middleware.csrf import get_token

# Create your views here.

def index(request):
    return HttpResponse("Hello, World!!!!")


def test_index(request, foo):
    response_str= "You Just Enterd This Value := " + str(foo)
    return HttpResponse(response_str)


def blog(request, slug):
    response_str= "Your Slug is := " + slug
    return HttpResponse(response_str)

@api_view(['POST'])
def register(request):

    if request.method == 'POST':

        data = request.data

        serializer = RegisterUserSerializer(data=data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            #generate the csrf_token 
            csrf_token = get_token(request)

            response = Response(serializer.data, status=status.HTTP_201_CREATED)
            response['X-CSRFToken'] = csrf_token
            return response
        
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def loginn(request):

    if request.method == 'POST':

        print(request.user)
        if request.user.is_authenticated:
            return Response({"message": "you're already logged in!!!!"}, status=status.HTTP_200_OK)

        data = request.data

        serializer = LoginUserSerializer(data=data)

        if serializer.is_valid(raise_exception=True):
            username = serializer.validated_data.get("username")
            password = serializer.validated_data.get("password")

            user = authenticate(username=username, password=password)
            print(user)

            if user is not None:
                login(request, user)
                return Response({"message": "Succesfully logged-in!"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Invalid username and/or password!!!"}, status=status.HTTP_401_UNAUTHORIZED)

        else:
            return Response(serializers.errors, status=status.HTTP_404_NOT_FOUND)
     

@api_view(['POST'])
def logoutt(request):

    if request.user.is_authenticated:
        logout(request)
        return Response({"message": "you've been successfully logged out!!!"})
    
    

    return Response({"message": "you're already logged out!!!"})
    