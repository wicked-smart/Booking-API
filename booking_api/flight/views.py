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
from datetime import datetime, time

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
@api_view(['GET'])
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


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def airport(request, airport_id):

    try:
        airport = Airport.objects.get(id=airport_id)  
    except Airport.DoesNotExist:
        return Response({'message': "Airport Does Not Exists!"}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':

        serializer = AirportSerializer(airport)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'DELETE':

        airport.delete()
        return Response({'message': 'successfully deleted!'}, status=status.HTTP_200_OK)


#Flights Endpoint
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@cache_page(60* 10)
def flights(request):

    if request.method == 'GET':
 

        paginator = CustomPageNumberPagination()
        print("request := ", request)

        params = request.query_params
        print("query params := ", params)

        if len(params) > 0:

            queryParamSerializer = FlightParamSerializer(data=params)

            if queryParamSerializer.is_valid():

                #get all the filters
                flight_number = queryParamSerializer.validated_data.get('flight_number')
                origin_city = queryParamSerializer.validated_data.get('origin')
                destination_city = queryParamSerializer.validated_data.get('destination')
                stops = queryParamSerializer.validated_data.get('stops')
                airlines = queryParamSerializer.validated_data.get('airlines')
                duration = queryParamSerializer.validated_data.get('duration')
                seat_class = queryParamSerializer.validated_data.get('seat_class')
                booking_date = queryParamSerializer.validated_data.get('booking_date')
                price = queryParamSerializer.validated_data.get('price')
                departure_timing = queryParamSerializer.validated_data.get('departure_timing')
                layover_duration = queryParamSerializer.validated_data.get('layover_duration')
                sort_by = queryParamSerializer.validated_data.get('sort_by')

                filters = {}

                if origin_city and destination_city:

                    try:
                        origin = Airport.objects.filter(city__iexact=origin_city)
                        
                        if not origin.exists():
                            raise Airport.DoesNotExist
                        
                        filters['origin'] = origin[0]

                    except Airport.DoesNotExist:
                        message = f" {origin_city} city airport does not exists yet in our db...we're still updating our data.."
                        return Response({'message': message}, status=status.HTTP_404_NOT_FOUND)

                    try:
                        destination = Airport.objects.filter(city__iexact=destination_city)

                        if not destination.exists():
                            raise Airport.DoesNotExist
                        
                        filters['destination'] = destination[0]

                    except Airport.DoesNotExist:
                        message = f" {destination_city} city airport does not exists yet in our db...we're still updating our data.."
                        return Response({'message': message}, status=status.HTTP_404_NOT_FOUND)
                

                else:
                    return Response({'message': 'Both origin and destination fields are important! '}, status=status.HTTP_400_BAD_REQUEST)



                #filters

               
                if flight_number:
                    filters['flight_no'] = flight_number

                if stops:
                    if stops == 'NON_STOP':
                        filters['is_nonstop'] = True
                    else:
                        filters['is_nonstop'] = False
                
                if airlines:
                    airline_string = airlines[0]
                    airlines = airline_string.split(', ')
                    filters['airline__in'] = airlines
                
                if duration:
                    filters['duration__lte'] = duration

                if booking_date:
                    #convert to week day and add filters['depart_weekday'] = wekk_number 
            
                    week_number = booking_date.weekday()

                    week = Week.objects.get(number=week_number)
                    filters['departure_weekday'] = week 
    
                    
                
                if seat_class and price:

                    if seat_class == 'ECONOMY':
                        filters['economy_fare__lte'] = price

                    elif seat_class == 'BUISNESS':
                        filters['buisness_fare__lte'] = price
                    
                    elif  seat_class == 'FIRST_CLASS':
                        filters['first_class_fare__lte'] = price

                elif (price and not seat_class) or (seat_class and not price):
                    return Response({'message': 'seat_class and Price is both mandatory query fields!!!'}, status=status.HTTP_400_BAD_REQUEST)




                if departure_timing:

                    if departure_timing == 'BEFORE_5_AM':
                        time1 =   time(hour=12, minute=0, second=0)
                        time2 =  time(hour=5, minute=0, second=0)
                    
                    elif departure_timing == 'AFTER_5_BEFORE_11_AM':
                        time1 =   time(hour=5, minute=0, second=0)
                        time2 =  time(hour=11, minute=0, second=0)

                    elif departure_timing == 'AFTER_11_BEFORE_4_PM':
                        time1 =   time(hour=11, minute=0, second=0)
                        time2 =  time(hour=16, minute=0, second=0)
                    
                    elif departure_timing == 'AFTER_4_BEFORE_7_PM':
                        time1 =   time(hour=16, minute=0, second=0)
                        time2 =  time(hour=19, minute=0, second=0)

                    
                    elif departure_timing == 'AFTER_7_PM':
                        time1 =   time(hour=19, minute=0, second=0)
                        time2 =  time(hour=23, minute=59, second=0)
                    
                    filters['depart_time__gte'] = time1
                    filters['depart_time__lte'] = time2

                    
                if layover_duration:
                    pass 
            
                
                        

                print("filter:= ", filters)
                flights = Flight.objects.filter(**filters)

                if sort_by:

                    if sort_by == 'PRICE':
                        if seat_class == 'ECONOMY':
                            flights = flights.order_by('economy_fare')
                        elif seat_class == 'BUISNESS':
                            flights = flights.order_by('buisness_fare')
                        elif seat_class == 'FIRST_CLASS':
                            flights = flights.order_by('first_class_fare')
                    
                    elif sort_by == 'ARRIVAL_TIME':
                        flights = flights.order_by('arrival_time')
                    
                    elif sort_by == 'DEPARTURE_TIME':
                        flights = flights.order_by('depart_time')
                    
                    elif sort_by == 'DURATION':
                        flights = flights.order_by('duration')



                if flights.exists():
                    paginated_flights = paginator.paginate_queryset(flights, request)

                else:
                    return Response({'message': {'Oops! None of flights match your query!!!'}}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(queryParamSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            #return the response
            serializer = FlightSerializer(paginated_flights, many=True, context={'request': request})
            print("serializer Meta fields:= ", FlightSerializer.Meta.fields)
            return paginator.get_paginated_response(serializer.data)
        
        else:
            flights = Flight.objects.all()
            paginated_flights = paginator.paginate_queryset(flights, request)
            serializer = FlightSerializer(paginated_flights, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)


#book flight
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def book_flight(request, flight_id):

    try:
        flight = Flight.objects.get(pk=flight_id)
    except Flight.DoesNotExist:
        return Response({'message': 'Flight Does not exists!'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'POST':

        data = request.data
        serializer = FlightBookingSerializer(data=data, context={'request': request, 'flight': flight})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def logoutt(request):

    if request.user.is_authenticated:
        logout(request)
        return Response({"message": "you've been successfully logged out!!!"})
    
    

    return Response({"message": "you're already logged out!!!"})
    
