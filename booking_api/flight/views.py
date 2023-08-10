from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from rest_framework.decorators import api_view, permission_classes
from flight.serializers.AuthSerializers import *
from flight.serializers.ModelSerializers import *
from rest_framework.response import Response
from rest_framework import status
from .models import *
from django.contrib.auth import authenticate, logout, login
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .pagination import CustomPageNumberPagination
from django.views.decorators.cache import cache_page

from .utils import *
from django.middleware.csrf import get_token

# Create your views here.
@api_view(["GET"])
@permission_classes([IsAdminUser])
def initialise(request):
    
    try:
        if len(Week.objects.all()) == 0:
            createWeekDays()
        
        if  len(Airport.objects.all()) == 0:
            print("Adding airports...")
            addAirports()
        
        if len(Flight.objects.all()) == 0:
            addDomesticFlights()
        
        return Response({"message": "Succesfully Initialised Databases!!"})

    except:
        return Response({"message": "Couldn't initilise properly!!!"}, status=status.HTTP_400_BAD_REQUEST)


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
     

# airports endpoint
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@cache_page(60* 15)
def airports(request):

    if request.method == "GET":
        
        airports = Airport.objects.all()

        #pagination 
        paginator = CustomPageNumberPagination()
        paginated_airports = paginator.paginate_queryset(airports, request)

        serializer = AirportSerializer(paginated_airports, many=True)
        return paginator.get_paginated_response(serializer.data)


    
  




@api_view(['POST'])
def logoutt(request):

    if request.user.is_authenticated:
        logout(request)
        return Response({"message": "you've been successfully logged out!!!"})
    
    

    return Response({"message": "you're already logged out!!!"})
    
