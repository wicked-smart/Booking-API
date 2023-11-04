from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, JsonResponse
from rest_framework.decorators import api_view, permission_classes
from flight.serializers.AuthSerializers import *
from flight.serializers.ModelSerializers import *
from rest_framework.response import Response
from rest_framework import status
from .models import *
import time as timemodule
from django.contrib.auth import authenticate, logout, login
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .pagination import *
from django.views.decorators.cache import cache_page
from datetime import datetime, time
import os
from dotenv import load_dotenv
import stripe
from django.urls import reverse

from .utils import *
from booking_api.settings import BASE_DIR
from django.middleware.csrf import get_token
import pdfkit 
from django.template.loader import get_template
from django.template import Context
from .tasks import *
from celery.result import AsyncResult
import json
import boto3
from io import BytesIO
import requests



#load .env file
load_dotenv(BASE_DIR / '.env')

#load stripe api keys
stripe_test_api_key = os.getenv('STRIPE_TEST_API_KEY')
stripe.api_key = stripe_test_api_key

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

@api_view(['GET'])
def health_test(request):
    return Response({"message": "Health Test Working....."})


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
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
     

# airports endpoint
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@cache_page(60* 15)
def airports(request):

    if request.method == "GET":
        
        airports = Airport.objects.all()

        #pagination 
        paginator = CombinedPagination()
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
 

        paginator = CombinedPagination()
        print("request := ", request)

        params = request.query_params
        print("query params := ", params)

        if len(params) > 0:

            queryParamSerializer = FlightParamSerializer(data=params)

            if queryParamSerializer.is_valid():

                #get all the filters
                round_trip = queryParamSerializer.validated_data.get('round_trip')
                return_date = queryParamSerializer.validated_data.get('return_date')
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
                
                elif not origin_city and not destination_city:
                    pass 
                    
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

                    filters['departure_weekday__number'] = week_number 
    
                    
                
                if seat_class and not price:

                    if seat_class == 'ECONOMY':
                        filters['economy_fare__lte'] = 7000

                    elif seat_class == 'BUISNESS':
                        filters['buisness_fare__lte'] = 10000
                    
                    elif  seat_class == 'FIRST_CLASS':
                        filters['first_class_fare__lte'] = 13000

                if price and not seat_class:
                        return Response("seat class must be their with price filter..", status=status.HTTP_400_BAD_REQUEST)
                
                elif price and seat_class:

                    if seat_class == 'ECONOMY':
                            filters['economy_fare__lte'] = price

                    elif seat_class == 'BUISNESS':
                            filters['buisness_fare__lte'] = price
                
                    elif  seat_class == 'FIRST_CLASS':
                            filters['first_class_fare__lte'] = price
                


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
            
                    
                        

                print("departing filter:= ", filters)
                #paginator = FlightCombinedPagination()
                flights = Flight.objects.filter(**filters)
                print("departing flights := ", flights)

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
                    #paginated_flights = paginator.paginate_queryset(flights, request)
                    departing_flight_serializer = FlightSerializer(flights, many=True, context={'request': request})
                else:
                    paginated_flights = None
                    departing_flight_serializer = None

                #check for return type and prepare the return filters
                if round_trip is True:

                    week_number = return_date.weekday()
                    week = Week.objects.get(number=week_number)
                    
                    filters['departure_weekday__number'] = week_number 

                    #pop unwanted fields
                    #filters.pop('booking_date')
                    destination = filters.pop('origin')
                    origin = filters.pop('destination')

                    # push new filter
                    filters['origin'] = origin
                    filters['destination'] = destination

                    print("returning_filters := ", filters)
                    

                #retrieve returning flights
                #paginator = FlightCombinedPagination()
                returning_flights = Flight.objects.filter(**filters)

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
            
                if returning_flights.exists():
                    #paginated_returning_flights = paginator.paginate_queryset(returning_flights, request)
                    returning_flight_serializer = FlightSerializer(returning_flights, many=True, context={'request': request})
                else:
                    paginated_returning_flights = None
                    returning_flight_serializer = None


                if departing_flight_serializer is None and returning_flight_serializer is None:
                    return Response({'message': {'Oops! None of flights match your query!!!'}}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(queryParamSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            #return the response
            
            if round_trip is True:
                
                data = {
                    #"count": (len(paginated_flights) if paginated_flights else 0) + (len(paginated_returning_flights) if paginated_returning_flights else 0),
                    "departing_flights": departing_flight_serializer.data if departing_flight_serializer is not None else None,
                    "returning_flights": returning_flight_serializer.data if returning_flight_serializer is not None else None
                }
            else:
                data = departing_flight_serializer.data
            #print("serializer Meta fields:= ", FlightSerializer.Meta.fields)
            
            
            return Response(data, status=status.HTTP_200_OK)
        
        else:
            flights = Flight.objects.all()
            paginated_flights = paginator.paginate_queryset(flights, request)
            serializer = FlightSerializer(paginated_flights, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)


# flight GET, PUT , DELETE
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def flight_details(request, flight_id):

    try:
        flight = Flight.objects.get(id=flight_id)
    
    except Flight.DoesNotExist:
        return Response({'message': f"Flight with id {flight_id} Does not exists!!"})
    
    if request.method == 'GET':
        serializer = FlightSerializer(flight, context={'request': request, 'flight_id': flight_id})
        return Response(serializer.data, status=status.HTTP_200_OK)
    

#book flight
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def book_flight(request, flight_id):

    try:
        flight = Flight.objects.get(pk=flight_id)
        
    except Flight.DoesNotExist:
        return Response({'message': 'Flight Does not exists!'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'POST':

        data = request.data
        serializer = None
        #find tripe type and serialize according to it
        trip_type = data.get("trip_type")
        if trip_type is None:
            return Response({"message": "trip_type missing !!"}, status=status.HTTP_400_BAD_REQUEST)
        if trip_type == 'ONE_WAY':
            serializer = FlightBookingSerializer(data=data, context={'request': request, 'flight': flight})
        if trip_type == 'ROUND_TRIP':
            returning_flight = data.get('return_flight')
            if returning_flight is None:
                return Response({"message": "returning flight is neccesary in round trip flight!!"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                return_flight = Flight.objects.get(pk=returning_flight)
                ret_serializer = FlightBookingSerializer(
                    data=data, 
                    context={'request': request, 'flight': flight, 'return_flight':return_flight}
                    )
            except Flight.DoesNotExist:
                return Response({'message': 'Returning Flight Does not exists!'}, status=status.HTTP_404_NOT_FOUND)
            
        if serializer and serializer.is_valid():
            booking = serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif serializer is None:
            #seperate tickets
            if trip_type == 'ROUND_TRIP':
                if ret_serializer.is_valid():
                        booking,ret_booking = ret_serializer.save()
                        return Response(ret_serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(ret_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#download refunds receipts and tickets
@api_view(['GET'])
def download_pdf(request, booking_ref, pdf_type, pdf_filename):
    # Retrieve the PDF filename from booking_ref
    #pdf_filename = generate_reciept_pdf(booking_ref)

    booking = Booking.objects.get(booking_ref=booking_ref)

    # # Generate the full path to the PDF
    # if pdf_type == "refund":
    #     pdf_path = os.path.join(settings.MEDIA_ROOT, f"refunds/{pdf_filename}")

    # elif pdf_type == "ticket":
        
        #pdf_path = os.path.join(settings.MEDIA_ROOT, f"tickets/{pdf_filename}")

    # Serve the PDF for download
    if pdf_type == "ticket":
        if booking.payment_status == 'SUCCEDED' and booking.booking_status == 'CONFIRMED':

            #generate pdf , get the filename, read the file and return as response
            #generate_ticket_pdf.delay(booking_ref)
            response = generate_ticket_pdf.apply_async(args=[booking_ref])
            if response is None:
                return Response({"message": "error uploading to s3"}, status=status.HTTP_400_BAD_REQUEST)
            url = response.get()
            print(url)

            try:
                # Use requests to download the PDF file from the pre-signed URL
                response = requests.get(url)

                if response.status_code == 200:
                    # Set the content type to PDF and a desired filename
                    content_type = "application/pdf"
                    filename = "downloaded.pdf"  # You can set a default filename

                    # Set the content type and disposition for the response
                    response = HttpResponse(content=response.content, content_type=content_type)
                    response["Content-Disposition"] = f'attachment; filename="{filename}"'

                    return response
                else:
                    return Response({"messsage": "Failed to download the PDF file from the pre-signed URL."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            except Exception as e:
                return HttpResponse({"messsage": f"Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            
            # try:
            #     with open(pdf_path, 'rb') as pdf_file:
            #         print("pdf is being read..from views.py !!!!")
            #         response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            #         response['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'
            #         return response
            # except FileNotFoundError:
            #     print("pdf exists := ", os.path.exists(pdf_path))
            #     response_message = "The PDF is not available yet. Please check back later."
            #     return Response({"message": response_message}, status=status.HTTP_202_ACCEPTED)
        
    
        else:        
            return Response({"message": "Please complete your payment to get the ticket's PDF!"}, status=status.HTTP_404_NOT_FOUND)

    elif pdf_type == 'refund':
        if booking.booking_status == 'CANCELED' and booking.payment_status == 'REFUNDED' and booking.refund_status == 'CREATED':
            response = generate_reciept_pdf.apply_async(args=[booking_ref])
            if response is None:
                return Response({"message": "error uploading  receipt to s3"}, status=status.HTTP_400_BAD_REQUEST)
            url = response.get()
            print(url)

            try:
                # Use requests to download the PDF file from the pre-signed URL
                response = requests.get(url)

                if response.status_code == 200:
                    # Set the content type to PDF and a desired filename
                    content_type = "application/pdf"
                    filename = "downloaded.pdf"  # You can set a default filename

                    # Set the content type and disposition for the response
                    response = HttpResponse(content=response.content, content_type=content_type)
                    response["Content-Disposition"] = f'attachment; filename="{filename}"'

                    return response
                else:
                    return Response({"messsage": "Failed to download the PDF file from the pre-signed URL."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            except Exception as e:
                return HttpResponse({"messsage": f"Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            
        else:
            response_message = "The  receipt PDF is not available yet.Please check back later."
            return Response({"message": response_message}, status=status.HTTP_202_ACCEPTED)

#find cancellation charge
def get_cancellation_charge(booking):
        #calculate cancellation charge on the basis of time delta between current and booking datetimes
        departure_date = booking.flight_dep_date
        departure_time = booking.flight.depart_time

        departure_datetime = datetime.combine(departure_date, departure_time)
        
        diff =  departure_datetime - datetime.now()
        diff_in_hrs = round(diff.total_seconds() / 3600, 2)

        if diff_in_hrs <= 2:
            return None
        
        elif diff_in_hrs > 2 and diff_in_hrs <= 72:
            cancellation_charge = 3500

        elif diff_in_hrs > 72 and diff_in_hrs <= 168:
            cancellation_charge = 3000
        
        elif diff_in_hrs > 168:
            cancellation_charge = 0
        
        return cancellation_charge


# GET, PUT any particular booking using booking_ref
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def bookings(request, booking_ref):

    try:
        booking = Booking.objects.get(booking_ref=booking_ref)
    
    except Booking.DoesNotExist:
        return Response({'message': 'Booking Does Not Exsis!'})
    
    if request.method == 'GET':
        if booking.trip_type == 'ONE_WAY':
            serializer = FlightBookingSerializer(booking, context={'request': request, 'flight': booking.flight})
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif booking.trip_type == 'ROUND_TRIP':
            try:
                ret_booking = Booking.objects.get(booking_ref=booking.other_booking_ref)
                serializer = FlightBookingSerializer(booking, 
                                                     context={'request': request, 
                                                              'booking': booking, 
                                                              'ret_booking': ret_booking,
                                                              'flight': booking.flight, 
                                                              'ret_flight': ret_booking.flight}
                                                            )
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Booking.DoesNotExist:
                return Response({"message": "return booking does not exits !"}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PUT':
        data = request.data 
        serializer = FlightBookingSerializer(booking, data=data,  partial=True, context={'request': request, 'booking': booking})

        print("booking := ", booking)
        if serializer.is_valid():
            
            if booking.trip_type == 'ONE_WAY' or (booking.trip_type == 'ROUND_TRIP' and  booking.separate_ticket == "YES"):
                #cancel the ticket
                booking.booking_status= 'CANCELED'

                try:
                        total_fare = booking.total_fare
                        if total_fare == 0.0:
                            return Response({"message": "Total Fare can't be equal to zero!!!"})
                        
                        cancellation_charge = 0

                        #calculate cancellation charge on the basis of time delta between current and booking datetimes
                        cancellation_charge = get_cancellation_charge(booking)
                        if cancellation_charge == None:
                            return Response({"message": "tickets cannot be cancelled less than 2 hours before departure time!!"})

                        amount = round(total_fare - cancellation_charge) * 100 #
                        print("booking_ref being passed to refund stripe := ", booking_ref)
                        stripe.Refund.create(
                            payment_intent=booking.payment_ref,
                            amount = amount,  # partially refundable
                            metadata={
                                "booking_ref": booking_ref
                            }
                        )

                            
                        pdf_url = reverse('download_pdf', args=[booking_ref, "refund", f"refund_receipt_{booking_ref}.pdf"])
                        print("pdf_url := ", pdf_url)
                        return Response({"message": f"PDF is being generated. You can download it <a href='{pdf_url}'>here</a> once it's ready."}, status=status.HTTP_200_OK)
                    

                        #return Response({"message": "Refund is yet not complete yet..check out later!!!"}, status=status.HTTP_404_NOT_FOUND)
                        
                except stripe.error.StripeError as e:
                    return Response({'message': f"{str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            elif booking.trip_type == 'ROUND_TRIP' and  booking.separate_ticket == "NO":
                cancellation_type = data.get("cancellation_type") 
                if cancellation_type is None:
                    return Response({"message": "For same airline round trip tickets, cancellation_type field  must have either BOTH, DEPARTING or RETURNING  clearly mentioned !!"}, status=status.HTTP_400_BAD_REQUEST)

                if cancellation_type == 'DEPARTING':
                    #booking.booking_status= 'CANCELED'

                    try:
                        total_fare = booking.total_fare
                        if total_fare == 0.0:
                            return Response({"message": "Total Fare can't be equal to zero!!!"})
                        
                        cancellation_charge = 0

                        #calculate cancellation charge on the basis of time delta between current and booking datetimes
                        cancellation_charge = get_cancellation_charge(booking)
                        if cancellation_charge == None:
                            return Response({"message": "tickets cannot be cancelled less than 2 hours before departure time!!"})

                        amount = round(total_fare - cancellation_charge) * 100
                        stripe.Refund.create(
                            payment_intent=booking.payment_ref,
                            amount = amount,  # partially refundable
                            metadata={
                                "booking_ref": booking_ref
                            }
                        )

                            
                        pdf_url = reverse('download_pdf', args=[booking_ref, "refund", f"refund_receipt_{booking_ref}.pdf"])
                        print("pdf_url := ", pdf_url)
                        return Response({"message": f"PDF is being generated. You can download it <a href='{pdf_url}'>here</a> once it's ready."}, status=status.HTTP_200_OK)
                    

                            #return Response({"message": "Refund is yet not complete yet..check out later!!!"}, status=status.HTTP_404_NOT_FOUND)
                            
                    except stripe.error.StripeError as e:
                        return Response({'message': f"{str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
                elif cancellation_type == 'RETURNING':
                    
                    try:
                        print("ret booking ref:= ", booking.other_booking_ref)
                        ret_booking = Booking.objects.get(booking_ref=booking.other_booking_ref)
                        print("other ret_booking ref := ", ret_booking.other_booking_ref)
                        print("ret_booking ref:= ", ret_booking)
                        #ret_booking.booking_status = "CANCELED"

                        total_fare = ret_booking.total_fare
                        print("total_fare := ", total_fare)
                        if total_fare == 0.0:
                            return Response({"message": "Total Fare can't be equal to zero!!!"})
                        
                        cancellation_charge = 0

                        #calculate cancellation charge on the basis of time delta between current and booking datetimes
                        cancellation_charge = get_cancellation_charge(ret_booking)
                        if cancellation_charge == None:
                            return Response({"message": "tickets cannot be cancelled less than 2 hours before departure time!!"})

                        amount = round(total_fare - cancellation_charge) * 100
                        stripe.Refund.create(
                            payment_intent=ret_booking.payment_ref,
                            amount = amount,  # partially refundable
                            metadata={
                                "booking_ref": ret_booking.booking_ref
                            }
                        )

                            
                        pdf_url = reverse('download_pdf', args=[ret_booking.booking_ref, "refund", f"refund_receipt_{ret_booking.booking_ref}.pdf"])
                        print("pdf_url := ", pdf_url)
                        return Response({"message": f"PDF is being generated. You can download it <a href='{pdf_url}'>here</a> once it's ready."}, status=status.HTTP_200_OK)
                    

                    except stripe.error.StripeError as e:
                        return Response({'message': f"{str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

                
                elif cancellation_type == 'BOTH':
                    try:
                        ret_booking_ref = booking.other_booking_ref
                        ret_booking = Booking.objects.get(booking_ref=ret_booking_ref)

                        if booking.booking_status != "CONFIRMED" and ret_booking.booking_status != "CONFIRMED":
                            return Response({"message": "For BOTH cancellation type, departing and returning both must be confirmed!!!"})
                        
                        #departing booking cancellation
                        total_fare = booking.total_fare
                        if total_fare == 0.0:
                            return Response({"message": "Total Fare can't be equal to zero!!!"})
                        
                        cancellation_charge = 0

                        #calculate cancellation charge on the basis of time delta between current and booking datetimes
                        cancellation_charge = get_cancellation_charge(booking)
                        if cancellation_charge == None:
                            return Response({"message": "tickets cannot be cancelled less than 2 hours before departure time!!"})

                        amount = round(total_fare - cancellation_charge) * 100
                        stripe.Refund.create(
                            payment_intent=booking.payment_ref,
                            amount = amount,  # partially refundable
                            metadata={
                                "booking_ref": booking_ref
                            }
                        )

                            
                        dep_pdf_url = reverse('download_pdf', args=[booking_ref, "refund", f"refund_receipt_{booking_ref}.pdf"])

                        #returning booking cancellation
                        total_fare = ret_booking.total_fare
                        if total_fare == 0.0:
                            return Response({"message": "Total Fare can't be equal to zero!!!"})
                        
                        cancellation_charge = 0

                        #calculate cancellation charge on the basis of time delta between current and booking datetimes
                        cancellation_charge = get_cancellation_charge(ret_booking)
                        if cancellation_charge == None:
                            return Response({"message": "tickets cannot be cancelled less than 2 hours before departure time!!"})

                        amount = round(total_fare - cancellation_charge) * 100
                        stripe.Refund.create(
                            payment_intent=ret_booking.payment_ref,
                            amount = amount,  # partially refundable
                            metadata={
                                "booking_ref": ret_booking.booking_ref
                            }
                        )

                            
                        ret_pdf_url = reverse('download_pdf', args=[ret_booking.booking_ref, "refund", f"refund_receipt_{ret_booking.booking_ref}.pdf"])
                       # print("pdf_url := ", pdf_url)
                        return Response({"message": f"PDF is being generated. You can download departing refund receipt <a href='{dep_pdf_url}'>here</a> and returning refund receipt <a href='{dep_pdf_url}'>here</a>  once it's ready."}, status=status.HTTP_200_OK)
                    

                    except stripe.error.StripeError as e:
                        return Response({'message': f"{str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            


        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        '''
            max_poll_attempts = 10  # Adjust as needed
            poll_interval = 5  # Adjust as needed (seconds)
            current_attempt = 0
            
            while current_attempt < max_poll_attempts:
                booking.refresh_from_db()  # Refresh the booking object from the database
                if booking.booking_status == 'CANCELED' and booking.refund_status == 'CREATED':
                    #make sets is_booked=False
                    passengers = booking.passengers.all()

                    #make the seats available
                    for passenger in passengers:
                        seats = Seats.objects.filter(flight=booking.flight, departure_date=booking.flight_dep_date,passenger=passenger, is_booked=True).first()
                        seats.is_booked= False
                        seats.passenger = None
                        seats.save()

                    # create reciept pdf and send back as response
                    refund_task = generate_reciept_pdf.delay(booking_ref)
                    receipts_pdf_filename = f"refund_receipt_{booking_ref}.pdf"

                    print("Inside bookings PUT call")


                    # Return a response to acknowledge the request and provide a link to download the PDF
                    pdf_url = reverse('download_pdf', args=[booking_ref, "refund", receipts_pdf_filename])
                    print("pdf_url := ", pdf_url)
                    return HttpResponse({"message": f"PDF is being generated with task id {refund_task.id}. You can download it <a href='{pdf_url}'>here</a> once it's ready."}, status=status.HTTP_200_OK)
                    
                
                # Sleep for a while before the next polling attempt
                timemodule.sleep(poll_interval)
                current_attempt += 1
    
    
            
            
            if not (booking.booking_status == 'CANCELED' and booking.refund_status == 'CREATED'):

                return Response({'message': "Could not process refund , Try again !!"}, status=status.HTTP_400_BAD_REQUEST)
        '''
    

    

# payments endpoint
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def payments(request, booking_ref):
    try:
            booking = Booking.objects.get(booking_ref=booking_ref)
    except Booking.DoesNotExist:
            return Response("{'message': 'Booking does not exists!'}", status=status.HTTP_404_NOT_FOUND)
         
    
    if request.method == 'POST':

        
        if not stripe_test_api_key:
            return Response("{'message': 'Test API key not loaded from .env'}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if booking.booking_status != 'PENDING':
            return Response({'message': 'Booking status needs to be in PENDING state for payment to go through!!!'})
        
        # total fare 
        trip_type = booking.trip_type
        ret_booking = None 

        if trip_type == 'ONE_WAY':
            total_fare = round(booking.total_fare)
        elif trip_type == 'ROUND_TRIP':
            ret_booking_ref = booking.other_booking_ref
            try:
                ret_booking = Booking.objects.get(booking_ref=ret_booking_ref)
                total_fare = round(booking.total_fare) + round(ret_booking.total_fare)
            except Booking.DoesNotExist:
                return Response({"message": "returning booking of this ref does not exists!"}, status=status.HTTP_400_BAD_REQUEST)

        if total_fare == 0.0:
            return Response({'message': 'amount must be greater than zero!!!'},status=status.HTTP_400_BAD_REQUEST)

        
        # create stripe PaymentIntent Object, confirm the order with passing booking ref as meta data
        paymentIntent = stripe.PaymentIntent.create(
            amount= total_fare * 100,
            currency='inr',
            automatic_payment_methods={
                "enabled": True,
                "allow_redirects": "never"
            },
            payment_method_options={'card':
                        {
                        'request_three_d_secure': 'any'
                        }
                    },
            metadata = {
                "booking_ref": booking.booking_ref
            }

        )
        


        # retrieve payment_intent_id
        payment_intent_id = paymentIntent["id"]

        #confirm the paymentIntent
        confirm = stripe.PaymentIntent.confirm(
            payment_intent_id,
            payment_method= "pm_card_visa"
        )

        #generate Ticket PDF
        ticket_pdf_filename = f"booking_ticket_{booking.booking_ref}.pdf"

        if trip_type == 'ROUND_TRIP' and (booking.flight.airline != ret_booking.flight.airline):
            ret_ticket_pdf_filename = f"booking_ticket_{ret_booking.booking_ref}.pdf"



        pdf_url = reverse('download_pdf', args=[booking_ref, "ticket", ticket_pdf_filename])
        print("pdf_url := ", pdf_url)

        if trip_type == 'ROUND_TRIP' and (booking.flight.airline != ret_booking.flight.airline):
            ret_pdf_url = reverse('download_pdf', args=[ret_booking.booking_ref, "ticket", ret_ticket_pdf_filename])
            

        # prepare the response 
        response_return = {
            "payemnt_intent_id": payment_intent_id,
            "ticket_pdf_url": f"Your Ticket will be availalbe <a href='{pdf_url}'>here</a> once you have succesfully completed next_action of authenticating url !!",
            "next_action": "Click on the hok url with this response and ping GET endpoint for payment confirmation ",
            "url": confirm["next_action"]
        }

        if trip_type == 'ROUND_TRIP' and (booking.flight.airline != ret_booking.flight.airline):
            response_return = {
                "payemnt_intent_id": payment_intent_id,
                "ticket_pdf_url": f"Your Ticket will be availalbe <a href='{pdf_url}'>here</a> once you have succesfully completed next_action of authenticating url !!",
                "return_ticket_pdf_url": f"Your return ticket will be availalbe <a href='{ret_pdf_url}'>here</a> once you have succesfully completed next_action of authenticating url !!",
                "next_action": "Click on the hook url with this response and ping GET endpoint for payment confirmation ",
                "url": confirm["next_action"]
           }
        else:

            response_return = {
                "payemnt_intent_id": payment_intent_id,
                "ticket_pdf_url": f"Your Ticket will be availalbe <a href='{pdf_url}'>here</a> once you have succesfully completed next_action of authenticating url !!",
                "next_action": "Click on the hook url with this response and ping GET endpoint for payment confirmation ",
                "url": confirm["next_action"]
        }


        return Response(response_return, status=status.HTTP_200_OK)

# handling stripe webhook events
@api_view(['POST'])
def stripe_webhook(request):

    if request.method == 'POST':

        print("headers := ",request.headers)

        event = None
        payload = request.body

        try:
             event = json.loads(payload)
        #print('Received event:', event)
        except:
             print('⚠️  Webhook error while parsing basic request.' + str(e))
             return JsonResponse({"message": "couldn't process the load "})
    
        # Replace with your Stripe webhook secret
        endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

        
        if endpoint_secret:
            try:
                # Verify the event using the endpoint secret
                event = stripe.Webhook.construct_event(
                    payload, request.headers.get('Stripe-Signature'), endpoint_secret
                )
            except stripe.error.SignatureVerificationError as e:
                print('⚠️  Webhook signature verification failed.' + str(e))
                print(request.headers.get('stripe-signature'))
                return JsonResponse({"message": f"Webhook signature verification failed! with endpoint_secret {endpoint_secret}"}, status=400)

        # Handle the event
        if event and event["type"] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']  # contains a stripe.PaymentIntent
            print('Payment for {} succeeded'.format(payment_intent['amount']))
            

            if 'metadata' in payment_intent:

                booking_ref = payment_intent['metadata'].get('booking_ref')
                print("booking_ref := ", booking_ref)
                try:
                    booking = Booking.objects.get(booking_ref=booking_ref)
                except Booking.DoesNotExist:
                    return Response({"message": "booking ref is invalid!"}, status=status.HTTP_404_NOT_FOUND)


                if booking.booking_status != 'PENDING':
                    return Response({"message": "booking status must be in PENDING state!"}, status=status.HTTP_404_NOT_FOUND)

                trip_type = booking.trip_type
                ret_booking = None

                if trip_type == 'ROUND_TRIP':
                    ret_booking_ref = booking.other_booking_ref
                    try:
                         ret_booking = Booking.objects.get(booking_ref=ret_booking_ref)
                    except Booking.DoesNotExist:
                         return Response({"message": "booking ref is invalid!"}, status=status.HTTP_404_NOT_FOUND)


                    if booking.booking_status != 'PENDING' and ret_booking.booking_status != 'PENDING':
                        return Response({"message": "booking status must be in PENDING state!"}, status=status.HTTP_404_NOT_FOUND)


                payment_status = payment_intent.get("status")
                payment_id = payment_intent.get("id")

                if payment_status == "succeeded":
                    booking.booking_status = 'CONFIRMED'
                    booking.payment_status = 'SUCCEDED'
                else:
                    return Response({"message": "payment status is not `succeeded`"}, status=status.HTTP_400_BAD_REQUEST)
                
                if trip_type == 'ROUND_TRIP':
                    if payment_status == "succeeded":
                        ret_booking.booking_status = 'CONFIRMED'
                        ret_booking.payment_status = 'SUCCEDED'
                    else:
                      return Response({"message": "payment status is not `succeeded`"}, status=status.HTTP_400_BAD_REQUEST)
                

                if payment_id is not None:
                    booking.payment_ref = payment_id
                
                booking.save()

                if trip_type == 'ROUND_TRIP':
                    if payment_id is not None:
                        ret_booking.payment_ref = payment_id
                    ret_booking.save()


                return Response({'message': 'booking successfully updated!'}, status=status.HTTP_200_OK)
            
            else:
                print('⚠️  Metadata attribute not found in payment_intent object')
                return JsonResponse({"message": 'Metadata attribute not found in payment_intent object'}, status=400)       

        elif event["type"] == 'payment_intent.created':
            return JsonResponse({'message': 'payemnt intent created succesfully!'}, status=200)
            # Handle the attached payment method event here

        elif event["type"] == 'charge.refunded':
            refund_object = event['data']['object']
            print("Event charge.refund succeeded....")

            if 'metadata' in refund_object:
                booking_ref = refund_object['metadata'].get('booking_ref')
                receipt_url = refund_object['receipt_url']

                print("today's booking ref received := ",booking_ref)

                try:
                    booking = Booking.objects.get(booking_ref=booking_ref)
                except Booking.DoesNotExist:
                    return Response({"message": "booking ref is invalid!"}, status=status.HTTP_404_NOT_FOUND)

                print("today's booking status := ", booking.booking_status) ##

                if booking.booking_status != 'CONFIRMED':
                    return Response({"message": "Testing refund  eligible for refund!! "}, status=status.HTTP_400_BAD_REQUEST)


                refund_status = refund_object.get("status")
                #payment_id = data.get("payment_id")

                if refund_status is not None and refund_status == "succeeded":
                    booking.refund_status = 'CREATED'
                    booking.payment_status = 'REFUNDED'

                if receipt_url is not None:
                    booking.refund_receipt_url = receipt_url

                booking.booking_status = 'CANCELED'

                booking.save()

                #generate_reciept_pdf.delay(booking_ref)

                return Response({'message': 'Refund successfully created!'}, status=status.HTTP_200_OK)

                    

        else:
            # Unexpected event type
            return JsonResponse({'error': 'Unhandled event type'}, status=400)


@api_view(['POST'])
def logoutt(request):

    if request.user.is_authenticated:
        logout(request)
        return Response({"message": "you've been successfully logged out!!!"})
    
    

    return Response({"message": "you're already logged out!!!"})
   


'''
@api_view(['POST'])
def update_booking(request):
    data = request.data

    if data["event"] == "payment":

        if 'webhook_secret' in data and data["webhook_secret"] == os.environ.get('WEBHOOK_SECRET'):

            booking_ref = data.get("booking_ref")

            try:
                booking = Booking.objects.get(booking_ref=booking_ref)
            except Booking.DoesNotExist:
                return Response({"message": "booking ref is invalid!"}, status=status.HTTP_404_NOT_FOUND)


            if booking.booking_status != 'PENDING':
                return Response({"message": "PENDING Not Allowed!"}, status=status.HTTP_404_NOT_FOUND)


            payment_status = data.get("payment_status")
            payment_id = data.get("payment_id")

            if payment_status is not None:
                booking.booking_status = 'CONFIRMED'
                booking.payment_status = 'SUCCEDED'

            if payment_id is not None:
                booking.payment_ref = payment_id

            booking.save()

            return Response({'message': 'booking successfully updated!'}, status=status.HTTP_200_OK)

        else:
            return Response({'message': 'Internal Route..Not Alllowed!'}, status=status.HTTP_404_NOT_FOUND)

    elif data["event"] == "refund":


        if 'webhook_secret' in data and data["webhook_secret"] == os.environ.get('WEBHOOK_SECRET'):

            booking_ref = data.get("booking_ref")
            receipt_url = data.get("receipt_url")

            try:
                booking = Booking.objects.get(booking_ref=booking_ref)
            except Booking.DoesNotExist:
                return Response({"message": "booking ref is invalid!"}, status=status.HTTP_404_NOT_FOUND)


            if booking.booking_status != 'CONFIRMED':
                return Response({"message": "Not eligible for refund!! "}, status=status.HTTP_404_NOT_FOUND)


            refund_status = data.get("refund_status")
            #payment_id = data.get("payment_id")

            if refund_status is not None:
                booking.refund_status = refund_status
                booking.payment_status = 'REFUNDED'

            if receipt_url is not None:
                booking.refund_receipt_url = receipt_url

            booking.booking_status = 'CANCELED'

            booking.save()

            return Response({'message': 'Refund successfully created!'}, status=status.HTTP_200_OK)

        else:
            return Response({'message': 'Missing secret, request not Alllowed!'}, status=status.HTTP_404_NOT_FOUND)

 

 pdf generation endpoint 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_pdf(request, booking_ref):

    try:
        booking = Booking.objects.get(booking_ref=booking_ref)
    
    except Booking.DoesNotExist:
        return Response({'message': f"Booking with reference {booking_ref} does not exists! "}, status=status.HTTP_400_BAD_REQUEST)
    
    pdf_options = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
    }

    #url = "https://pay.stripe.com/receipts/payment/CAcaFwoVYWNjdF8xTlRQWWhTQmx3TnB1eEIyKPqpvKcGMgYIwlewUVQ6LBYz3XfSXJTk9fkJqr4qqp10M8sWYFHE66zDcvHG5zPO6bhJcfxywawR6FGQ"
    # Generate the PDF from the URL
    #pdf_content = pdfkit.from_url(url, False, options=pdf_options)

    template = get_template('flight/ticket.html')

    #context 

    duration = format_duration(booking.flight.duration)
    #print("duration := ", duration)

    #passengers age group count
    passengers = booking.passengers.all()

    adults=0
    children=0
    infants=0

    for passenger in passengers:
        if passenger.type == 'Adult':
            adults+=1
        elif passenger.type == 'Child':
            children+=1
        elif passenger.type == 'Infant':
            infants+=1
    
    age_group_count = {
        'adults': adults,
        'children': children,
        'infants': infants
    }

    # calculating ticket price
    seat_class = booking.seat_class

    if seat_class == 'ECONOMY':
        ticket_price = booking.flight.economy_fare
    elif seat_class == 'BUISNESS':
        ticket_price = booking.flight.buisness_fare
    elif seat_class == 'FIRST_CLASS':
        ticket_price = booking.flight.first_class_fare
    
    #total baggage information
    total_hand_baggage=0.0
    total_check_in_baggage=0.0
    for passenger in passengers:
        total_hand_baggage += passenger.hand_baggage
        total_check_in_baggage += passenger.check_in_baggage

    context = {
        'booking': booking,
        "duration": duration,
        "age_group_count": age_group_count,
        "ticket_price": ticket_price,
        "total_hand_baggae": total_hand_baggage,
        "total_check_in_baggage": total_check_in_baggage
        }

    rendered_template = template.render(context)
    print("rendered_template := ", rendered_template)

    #pdfkit using from string
    pdf = pdfkit.from_string(rendered_template, False, pdf_options)

    #create a HttpResponse with PDF content
    response = HttpResponse(pdf, content_type="application/pdf")
    response['Content-Disposition'] = 'attachment; filename="generated_pdf.pdf"'

    return response


@api_view(['GET'])
def testing_celery(request):

    pass




'''

@api_view(['GET'])
def test_pdf_gen(request):
    pdf_options = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
    }

    template = get_template('flight/index.html')
    rendered_template = template.render()
    pdf = pdfkit.from_string(rendered_template, False, pdf_options)
    pdf_filename = "test_pdf.pdf"
    pdf_buffer = BytesIO(pdf)

    s3 = boto3.client('s3', region_name='ap-south-1')


    s3_bucket_name = 'flight-booking-bucket'
    s3_key = "test_file.pdf"

    print("time before requets := ", datetime.now())
    s3.upload_fileobj(pdf_buffer, s3_bucket_name, s3_key)

    presigned_url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': s3_bucket_name, 'Key': s3_key},
        ExpiresIn=3600
    )

    try:
        # Use requests to download the PDF file from the pre-signed URL
        response = requests.get(presigned_url)

        if response.status_code == 200:
            # Set the content type to PDF and a desired filename
            content_type = "application/pdf"
            filename = "downloaded.pdf"  # You can set a default filename

            # Set the content type and disposition for the response
            response = HttpResponse(content=response.content, content_type=content_type)
            response["Content-Disposition"] = f'attachment; filename="{filename}"'

            return response
        else:
            return HttpResponse("Failed to download the PDF file from the pre-signed URL.", status=500)

    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)

    

    


