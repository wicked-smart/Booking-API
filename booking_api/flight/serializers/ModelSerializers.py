from flight.models import *
from rest_framework import serializers
from collections import OrderedDict
from enum import Enum
from rest_framework.exceptions import ValidationError
import re
from flight.utils import generate_hex_token
from datetime import datetime, timedelta
from django.db import transaction


LAYOVER_STOPS = (

    ('NON_STOP','NonStop'),
    ('ONE_STOP','OneStop'),
    ('TWO_OR_MORE','TwoOrMore')
)



FLIGHT_TIMINGS = (

    ('BEFORE_5_AM' , '12:00 AM to 5:00 AM'),
    ('AFTER_5_BEFORE_11_AM' , '5:00 AM - 11:00 AM'),
    ('AFTER_11_BEFORE_4_PM' , '11:00 AM - 4:00 PM'),
    ('AFTER_4_BEFORE_7_PM' , '4:00 PM - 7:00 PM'),
    ('AFTER_7_PM' , '7:00 PM - 12:00 AM')

)
    

SEAT_CLASS = (

    ('ECONOMY', 'Economy'),
    ('BUISNESS', 'Buisness'),
    ('FIRST_CLASS', 'FirstClass')
)

SORT_BY = (
    ('PRICE','Cheapest First' ),
    ('DEPARTURE_TIME', 'Deperture_time'),
    ('ARRIVAL_TIME', 'Arrival_time'),
    ('DURATION', 'Duration')
)

SEAT_TYPE = (
    ('WINDOW','Window' ),
    ('AISLE', 'Aisle'),
    ('MIDDLE', 'Middle')
)

CANCELLATION_TYPE  = (
    ('BOTH', 'Both'),
    ('DEPARTING', 'Departing'),
    ('RETURNING', 'Returning')
)

class AirportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airport
        fields = "__all__"
        extra_kwargs = {
            "city": {"required": True},
            "name": {"required": True},
            "code": {"required": True},
            "country": {"required": True}

        }
    
    
class FlightSerializer(serializers.ModelSerializer):
    origin = AirportSerializer()
    destination = AirportSerializer()

    # dynamically calculate seat fare 
    dynamic_fields = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        fields = ["id", "flight_no", "airline", "origin", "destination", "depart_time","arrival_time", "duration", "dynamic_fields"]



    # dynamic fields method
    def get_dynamic_fields(self, obj):

        request = self.context.get('request')
        query_params = request.query_params

        price = query_params.get('price')
        seat_class = query_params.get('seat_class')
        
        dynamic_data = {}

        if (price and seat_class) or (not price and seat_class) :
            if seat_class == 'ECONOMY':
                dynamic_data['economy_fare'] = obj.economy_fare

            elif seat_class == 'BUISNESS':
                dynamic_data['buisness_fare'] = obj.buisness_fare

            elif seat_class == 'FIRST_CLASS':
                dynamic_data['first_class_fare'] = obj.first_class_fare

        return dynamic_data

           
            

    #modify the results 
    def to_representation(self, instance):
        rep =  super().to_representation(instance)


        # Flatten the API Response 

        keys = list(rep.keys())

        origin  = rep.pop('origin')
        destination = rep.pop('destination')
        

        #code to maintain order of the origin `rep` function
        origin_idx = keys.index('origin')
        
        temp = OrderedDict()

        #flatten the API response
        keys.insert(origin_idx, 'origin_airport')
        keys.insert(origin_idx+1, 'origin_city')
        keys.insert(origin_idx+2, 'origin_code')

        keys.insert(origin_idx+3, 'destination_airport')
        keys.insert(origin_idx+4, 'destination_city')
        keys.insert(origin_idx+5, 'destination_code')

        temp_keys = {
            "origin_city": origin['city'],
            "origin_code": origin['code'],
            "origin_airport": destination['name'],
            "destination_city": destination['city'],
            "destination_code": destination['code'],
            "destination_airport": destination['name']
        }

        for k in keys:
            if k in list(rep.keys()):
                temp[k] = rep[k]
            elif k in temp_keys.keys():
                temp[k] = temp_keys[k]
                
        rep = temp

        #flatten dynamic fields
        dynamic_fields = rep.pop('dynamic_fields', {})  # Get the dynamic_fields data and remove it from the dictionary
        rep.update(dynamic_fields)

        request = self.context.get('request')
        flight_id = self.context.get('flight_id')


        if request and flight_id and request.method == 'GET' :
                #bagagge    information
            rep["check-in baggage"] = "15kg / person (1 piece only, not exceeding more than 32Kgs per baggage)"
            rep["hand baggage"]   = "1 hand-bag up to 7 kgs and 115 cms (L+W+H) per customer"
        

            # extra baggage charges information
            rep['extra_baggage_charges'] = {
                "at_airport charges": "Rs. 550 per extra kg",
                "pre-booking charges": {
                    "3 kg prepaid": "Rs. 1350",
                    "5 kg prepaid": "Rs. 2250",
                    "10 kg prepaid": "Rs. 4500",
                    "15 kg prepaid": "Rs. 6750",
                    "20 kg prepaid": "Rs. 9000",
                    "30 kg prepaid": "Rs. 13500",
                }
            }
                

        return rep


class FlightParamSerializer(serializers.Serializer):

    round_trip = serializers.BooleanField(default=False)
    return_date = serializers.DateField(input_formats=['%d-%m-%Y'])
    stops = serializers.ChoiceField(choices=LAYOVER_STOPS)
    flight_number = serializers.CharField(max_length=6)
    airlines = serializers.ListField(child=serializers.CharField(), required=False)
    origin = serializers.CharField(max_length=100, required=False)
    destination = serializers.CharField(max_length=100, required=False)
    duration = serializers.DurationField()
    seat_class = serializers.ChoiceField(choices=SEAT_CLASS)
    booking_date = serializers.DateField(input_formats=['%d-%m-%Y'])
    price = serializers.FloatField()
    departure_timing = serializers.ChoiceField(choices=FLIGHT_TIMINGS)
    layover_duration = serializers.DurationField()
    sort_by = serializers.ChoiceField(choices=SORT_BY) 

    #initilise with all the required=False
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in self.fields.keys():
            self.fields[field_name].required = False
    
    def validate(self, attrs):
        seat_class = attrs.get('seat_class')
        
        #check for return flight
        round_trip = attrs.get('round_trip')
        return_date = attrs.get('return_date')
        booking_date = attrs.get('booking_date')

        if round_trip and not return_date:
            raise ValidationError("For returning flights, return date is neccesary!!!")

        if booking_date and return_date:
            if booking_date > return_date:
                raise ValidationError("Return Date must be after booking date!!!")
            

        sort_by = attrs.get('sort_by')
        if sort_by and sort_by == 'PRICE':
            if not seat_class:
                raise ValidationError("seat_class  is must for ordering by price!!!")

        booking_date = attrs.get('booking_date')
        print("booking_date := ", booking_date)

        if booking_date:
            #booking_date = datetime.strptime(booking_date, '%d-%m-%Y').date()

            if booking_date < datetime.now().date():
                raise ValidationError("Booking date cannot be earlier than today!!")

        return attrs


class PassengerSerializer(serializers.ModelSerializer):
    seat_type = serializers.ChoiceField(choices=SEAT_TYPE, required=True)
    hand_baggage = serializers.FloatField(required=False)
    check_in_baggage = serializers.FloatField(required=False)

    class Meta:
        model = Passenger
        fields = ['first_name', 'last_name', 'gender', 'age', 'type', 'seat_type', 'hand_baggage', 'check_in_baggage']
        extra_kwargs = {
            "hand_baggage": {"required": False},
            "check_in_baggage": {"required": False}

        }


class FlightBookingSerializer(serializers.ModelSerializer):

    passengers = PassengerSerializer(many=True, required=True)
    flight_dep_date = serializers.CharField(required=False, max_length=12)
    return_flight_dep_date = serializers.CharField(required=False, max_length=12)
    trip_type = serializers.CharField(required=True, max_length=15) 

    #extra fields
    return_flight = serializers.IntegerField(required=False)
    return_flight_dep_date = serializers.CharField(required=False)
    cancellation_type = serializers.CharField(required=False, max_length=10)      

    class Meta:
        model = Booking
        fields = ['booking_ref', 'flight', 'payment_status', 'trip_type',  'booking_status', 'booked_at' ,'flight_dep_date', 'flight_arriv_date','cancellation_type' ,'return_flight', 'return_flight_dep_date', 'seat_class' , 'passengers', 'coupon_used','extra_baggage_booking_mode','extra_check_in_baggage', 'extra_baggage_price','coupon_code','coupon_discount' ,'total_fare', 'separate_ticket', 'other_booking_ref' ]
        extra_kwargs = {
            'seat_class': {'required': True},
            'flight_dep_date': {'required': True},
            'flight_arriv_date': {'required': False},
            'booking_ref': {'required': False} ,
            'flight': {'required': False} ,
            'total_fare': {'required': False},
            'extra_baggage_booking_mode': {'required': True},
            'extra_baggage_price': {'required': False ,'read_only': True},
            'extra_check_in_bagagge': {'required': False, 'read_only': True},
            'trip_type': {'required': True},
            'return_flight': {'required': False},
            'return_flight_dep_date': {'required': False},
            'separate_ticket': {'required': False},
            'other_booking_ref': {'required': False},
            'cancellation_type': {'required': False}

        }
    
    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs)

        request = self.context.get('request', None)
        if request and request.method == 'PUT':
            self.fields['seat_class'].allow_null = True
            self.fields['flight_dep_date'].allow_null = True
            self.fields['passengers'].allow_null = True
            self.fields['extra_baggage_booking_mode'].allow_null = True
    
    def validate(self, attrs):

        flight = self.context.get('flight')
        request = self.context.get('request')
        returning_flight = self.context.get('return_flight')


        if request and request.method == 'PUT':
            
            booking = self.context.get('booking')

            if not booking:
                raise ValidationError("Booking object Not passed to the Serializer !!!")

            booking_status = attrs.get("booking_status")
            if not booking_status or  booking_status != 'CANCELED':
                raise ValidationError("Invalid booking_status update  !!")
            
            if booking.trip_type == 'ROUND_TRIP' and booking.separate_ticket == "NO":
                ret_booking = Booking.objects.get(booking_ref=booking.other_booking_ref)
                cancellation_type = attrs.get("cancellation_type")
                if cancellation_type is None:
                        raise ValidationError("While cancelling for tickets from same airline, cancellation type is mandatory! ")
                if cancellation_type == "DEPARTING":
                    if booking.booking_status == 'CANCELED' or booking.booking_status == 'PENDING':
                        raise ValidationError('Departing booking_status not in valid state for this call!!!')
                elif cancellation_type == "RETURNING":
                    if ret_booking.booking_status == 'CANCELED' or ret_booking.booking_status == 'PENDING':
                        raise ValidationError('returning booking_status not in valid state for this call!!!')
                elif cancellation_type == "BOTH":
                    if booking.booking_status == 'CANCELED' or booking.booking_status == 'PENDING':
                        raise ValidationError('Departing booking_status not in valid state for this call!!!')
                    if ret_booking.booking_status == 'CANCELED' or ret_booking.booking_status == 'PENDING':
                        raise ValidationError('returning booking_status not in valid state for this call!!!')
            else:
                if booking.booking_status == 'CANCELED' or booking.booking_status == 'PENDING':
                    raise ValidationError("booking_status is in invalid state !!!")
                    
            return attrs

        date_str = attrs.get('flight_dep_date')
        date_obj = datetime.strptime(date_str, "%d-%m-%Y").date()

        if date_obj < datetime.today().date():
            raise ValidationError("Departure Date Cannot be Earlier than Current Day!")
        
        departure_time = flight.depart_time
        combined_datetime = datetime.combine(date_obj, departure_time)
        
        if combined_datetime < datetime.now():
            raise ValidationError("Departure DateTime Cannot be Earlier than Current DateTime!")

        # validate trip_type , returning_flight and returning_date
        trip_type = attrs.get('trip_type')
        return_flight = attrs.get('return_flight')
        returning_flight_dep_date = attrs.get('return_flight_dep_date')

        if trip_type is None:
            raise ValidationError("trip_type field is required!!")
        
        if trip_type and trip_type == 'ROUND_TRIP':
            if return_flight is None:
                raise ValidationError("For ROUND_TRIP returning_flight is required!")
            if returning_flight_dep_date is None:
                raise ValidationError("For ROUND_TRIP returning_flight_dep_date is required!")
            
            ret_date_obj = datetime.strptime(returning_flight_dep_date, "%d-%m-%Y").date()
            ret_departure_time = returning_flight.depart_time
            combined_ret_datetime = datetime.combine(ret_date_obj, ret_departure_time)

            if combined_ret_datetime <= combined_datetime:
                raise ValidationError("Returning Flight Departure must be STRICTLY after Departing Flight DateTime!!")

            #check for correct depature and arrival timings
            depart_combined_datetime = datetime.combine(date_obj, flight.arrival_time)
            ret_combined_datetime = datetime.combine(ret_date_obj, returning_flight.depart_time)
            if ret_combined_datetime <= depart_combined_datetime:
                raise ValidationError("Returning Flight must be deprting after departing flights arrival time!!")
        
            
        passengers = attrs.get('passengers')

        if len(passengers) > 20:
            raise ValidationError("No More Than 20 seats are allowed to be booked in one go!!!!")
        
        # validate for hand baggage
        for passenger in passengers:
            hand_baggage = passenger.get('hand_baggage')
            
            if hand_baggage:
                if hand_baggage > 7.0:
                    raise ValidationError("Hand Baggage Per customer cannot be more thaan 7 kgs !! ")
        

        


        if not flight:
            raise ValidationError("flight context is not passed in the serializer")

        #if not request:
        #    raise ValidationError("Request context is not passed in the serializer")
        

        date_pattern = re.compile(r"^(0[1-9]|[1-2][0-9]|3[0-1])([-./])(0[1-9]|1[0-2])\2\d{4}$")
        match  = date_pattern.match(date_str)

        if not match:
            raise ValidationError("Invalid Departure Date Format. Correct format is `dd[.-/]mm[./-]year ")

        if trip_type == 'ROUND_TRIP':
            match = date_pattern.match(returning_flight_dep_date)
            if not match:
                raise ValidationError("Invalid Departure Date Format. Correct format is `dd[.-/]mm[./-]year ")

        
        return attrs

    
    def get_passengers_seats(self, booking_ref, depart_obj, flight):
        try:

            booking = Booking.objects.filter(booking_ref=booking_ref).first()
            passengers  = booking.passengers.all()
            print("passengers from booking call := ", passengers)
            passengers_list = [] # new passengers list
            for passenger in passengers:
                
                foo = {
                    "first_name": passenger.first_name,
                    "last_name": passenger.last_name,
                    "gender": passenger.gender,
                    "age": passenger.age,
                    "age_category": passenger.type,
                    "hand_baggage": passenger.hand_baggage,
                    "check_in_baggage": passenger.check_in_baggage
                    
                }
                    
                seat = Seats.objects.filter(flight=flight, departure_date=depart_obj, passenger=passenger, is_booked=True).first()
                #print("seat:= ", seat)
                if not seat:
                    foo['seat'] = "NOT_ALLOCATED"
                else:
                    foo['seat'] = seat.seat_no
                    foo["seat_type"]= seat.seat_type 
                    
                passengers_list.append(foo)
            
            return passengers_list

                
        except Booking.DoesNotExist:
            return None
                    # get appropriate seats using booking_ref ....
        
    
    
    def to_representation(self, instance):

        request = self.context.get('request')
        flight = self.context.get('flight')
        ret_flight = self.context.get('return_flight')

        if isinstance(instance, tuple):
            booking, ret_booking = instance
            booking_data = super().to_representation(booking)
            ret_booking_data = super().to_representation(ret_booking)

            # insert flight timiings and passengers seats info , then return
            if flight.airline  == ret_flight.airline:

                booking_data.pop("separate_ticket")
                booking_data.pop("other_booking_ref")
                booking_data["flight_depart_time"] = flight.depart_time
                booking_data["flight_arrival_time"] = flight.arrival_time

                depart_date = booking_data["flight_dep_date"]
                dep_passengers = self.get_passengers_seats(booking_data["booking_ref"],  depart_date, flight)
                booking_data.pop("passengers")
                if dep_passengers is None:
                    booking_data["departure_error"] = "seats for departing passengers have not been allocated correctly!"
                else:
                    booking_data["passengers"] = dep_passengers
                
                # merge ret_booking info
                booking_data["return_flight"] = ret_booking_data.pop("flight")
                ret_depart_date = ret_booking_data.pop("flight_dep_date")
                booking_data["return_flight_dep_date"] = ret_depart_date
                booking_data["return_flight_arrival_date"] = ret_booking_data.pop("flight_arriv_date")
                booking_data["flight_depart_time"] = ret_flight.depart_time
                booking_data["flight_arrival_time"] = ret_flight.arrival_time
                booking_data["return_booking_status"] = ret_booking_data.pop("booking_status")
                booking_data["return_total_fare"] = ret_booking_data.pop("total_fare")

                #get return booking passengers
                ret_passengers = self.get_passengers_seats(ret_booking_data["booking_ref"],  ret_depart_date, ret_flight)
                if ret_passengers is None:
                    booking_data["return_error"] = "seats for returning passengers have not been allocated correctly!"
                else:
                    booking_data["return_passengers"] = ret_passengers

                return booking_data
            
            else:
                booking_data.pop("separate_ticket")
                booking_data.pop("other_booking_ref")
                booking_data["flight_depart_time"] = flight.depart_time
                booking_data["flight_arrival_time"] = flight.arrival_time

                #get passenegrs
                depart_date = booking_data["flight_dep_date"]
                dep_passengers = self.get_passengers_seats(booking_data["booking_ref"],  depart_date, flight)
                booking_data.pop("passengers")
                if dep_passengers is None:
                    booking_data["departure_error"] = "seats for departing passengers have not been allocated correctly!"
                else:
                    booking_data["passengers"] = dep_passengers

                #manage returning passengers
                ret_booking_data.pop("separate_ticket")
                ret_booking_data.pop("other_booking_ref")
                ret_booking_data["flight_depart_time"] = ret_flight.depart_time
                ret_booking_data["flight_arrival_time"] = ret_flight.arrival_time

                #get passenegrs
                depart_date = ret_booking_data["flight_dep_date"]
                dep_passengers = self.get_passengers_seats(ret_booking_data["booking_ref"],  depart_date, flight)
                ret_booking_data.pop("passengers")
                if dep_passengers is None:
                    ret_booking_data["departure_error"] = "seats for departing passengers have not been allocated correctly!"
                else:
                    ret_booking_data["passengers"] = dep_passengers
                
                return {"booking": booking_data, "return_booking": ret_booking_data}
                
        else:
            ret = super().to_representation(instance)

        print("representation := ", ret)

        #print("flight := ", flight)
        # GET /bookings/<str:booking_ref>   write to handdle this case

        if request and ( request.method == 'POST' or request.method == 'GET' ) :

            coupon_used = ret.get('coupon_used')

            if not coupon_used:
                ret.pop('coupon_code')
                ret.pop('coupon_discount')
            
            ret['flight_depart_time'] = flight.depart_time
            ret['flight_arrival_time'] = flight.arrival_time

            # attach allocated seat number to the passengers 
            departure_date  = ret.get('flight_dep_date')

            #print("departure-date := ", departure_date)
            depart_obj = datetime.strptime(departure_date, "%Y-%m-%d").date()
            booking_ref = ret.get('booking_ref')
            ret.pop("passengers")
            passengers = self.get_passengers_seats(booking_ref, depart_obj, flight)
            if passengers is None:
                ret['error'] = 'Booking ref does not exists!'
            else:
                ret['passengers'] = passengers

            #if trip_type == 'ROUND_TRIP' and single ticket scenario, insert returning times (depart and arrival), fetch passengers
            
        return ret 

    # seat allocation function 
    def allocate_seat(self, booking,  passenger, available_seats, preference):

        if preference == 'ANY':
            available_seats.sort(key=lambda seat: seat.seat_no)  # Sort seats by seat number
            
        for seat in available_seats:
            if not seat.is_booked and (seat.seat_type == preference or preference == 'ANY'):
                seat.is_booked = True
                #create new passenger
                new_passenger = Passenger.objects.create(**passenger)
                #print("new_passenger := " , new_passenger)
                new_passenger.unique_id = uuid.uuid4()
                new_passenger.seat_no = seat.seat_no
                new_passenger.save()

                # add passenger to the booking list 
                booking.passengers.add(new_passenger)

                #allot this new passenger this unbooked seat
                seat.passenger = new_passenger
                seat.save()
                return seat
        return None


    # get arrival date from departire date and corresponding flight
    def get_arrival_date(self, departure_date_str, flight):
        depart_datetime = datetime.strptime(departure_date_str, "%d-%m-%Y")

        depart_time = flight.depart_time
        arrival_time = flight.arrival_time
        arrival_timedelta = timedelta(hours=arrival_time.hour, minutes=arrival_time.minute, seconds=arrival_time.second)

        # Calculate the arrival_datetime by adding depart_timedelta to depart_datetime
        arrival_datetime = depart_datetime + arrival_timedelta

        # Extract the arrival date from arrival_datetime
        arrival_date = arrival_datetime.date()
        depart_date = depart_datetime.date()

        return depart_date, arrival_date


    #create seats
    def create_seats(self, flight, departure_date):

        for i in range(1, 31):
            for seat_col in range(ord('A'), ord('G')):
                
                seat_no = f"{i:02d}{chr(seat_col)}"

                if chr(seat_col) == 'A' or chr(seat_col) == 'F':
                    seat_type = 'WINDOW'
                elif chr(seat_col) == 'B' or chr(seat_col) == 'E':
                    seat_type = 'MIDDLE'
                elif chr(seat_col) == 'C' or chr(seat_col) == 'D':
                    seat_type = 'AISLE'
                
                Seats.objects.create(flight=flight, departure_date=departure_date, seat_no=seat_no, seat_type=seat_type)
                    
    
    def create(self, validated_data):
        
        
        flight = self.context.get('flight')
        request = self.context.get('request')
        
        seat_class = validated_data.get('seat_class')

       #check for returning trip type
        ret_flight = self.context.get('return_flight')
        trip_type = validated_data.get('trip_type')
        


        # Extract flight_dep_date and output arrival_dep_date 
        departure_date_string = validated_data.get('flight_dep_date')
        
        depart_date, arrival_date = self.get_arrival_date(departure_date_string, flight)

        if trip_type == 'ROUND_TRIP':

             # calculate return departure date and arrival  date
            ret_flight_dep_date_str = validated_data.get('return_flight_dep_date')
            ret_depart_date, ret_arrival_date = self.get_arrival_date(ret_flight_dep_date_str, ret_flight)


        if trip_type == 'ONE_WAY': 
        # Instantiate departing Booking object
            booking_ref = generate_hex_token()
            booking = Booking.objects.create(
                                            booking_ref=booking_ref,
                                            flight=flight,
                                            booked_by=request.user,
                                            flight_dep_date=depart_date,
                                            flight_arriv_date=arrival_date,
                                            seat_class=seat_class,
                                            )

        if trip_type == 'ROUND_TRIP':
            dep_booking_ref = generate_hex_token()
            dep_booking = Booking.objects.create(
                                        booking_ref=dep_booking_ref,
                                        flight=flight,
                                        booked_by=request.user,
                                        flight_dep_date=depart_date,
                                        flight_arriv_date=arrival_date,
                                        seat_class=seat_class,
                                        trip_type='ROUND_TRIP'
                                        )
                
        
            ret_booking_ref = generate_hex_token()
            ret_booking = Booking.objects.create(
                                booking_ref=ret_booking_ref,
                                flight=ret_flight,
                                booked_by=request.user,
                                flight_dep_date=ret_depart_date,
                                flight_arriv_date=ret_arrival_date,
                                seat_class=seat_class,
                                trip_type='ROUND_TRIP'

                )

            ret_booking.other_booking_ref = dep_booking_ref
            dep_booking.other_booking_ref = ret_booking_ref           

            if flight.airline != ret_flight.airline:
                dep_booking.separate_ticket = 'YES'
                ret_booking.separate_ticket = 'YES'

                dep_booking.other_booking_ref = ret_booking_ref
                ret_booking.other_booking_ref = dep_booking_ref
            else:
                dep_booking.separate_ticket = 'NO'
                ret_booking.separate_ticket = 'NO'

                


        #Add coupon code
        coupon_code = validated_data.get('coupon_code')
        if coupon_code:
            booking.coupon_used = True
            booking.coupon_code = coupon_code
            booking.coupon_discount= 750

            if trip_type == 'ROUND_TRIP':
                dep_booking.coupon_used = True
                dep_booking.coupon_code = coupon_code
                dep_booking.coupon_discount= 750

                ret_booking.coupon_used = True
                ret_booking.coupon_code = coupon_code
                ret_booking.coupon_discount= 750

        # SEAT ALLOTMENT LOGIC 
        seats = Seats.objects.filter(flight=flight, departure_date=depart_date, is_booked=False)
        if not seats.exists():
            #seats_to_create = []
            self.create_seats(flight, depart_date)


            # Use atomic transaction to speed up the bulk db creation
            #with transaction.atomic():
            #    Seats.objects.bulk_create(seats_to_create)

        if trip_type == 'ROUND_TRIP':
            ret_seats = Seats.objects.filter(flight=ret_flight, departure_date=ret_depart_date, is_booked=False)
            if not ret_seats.exists():
            #seats_to_create = []
               self.create_seats(ret_flight, ret_depart_date)

        # sort seats as per seat_type
        seats = list(seats)
        seats.sort(key=lambda seat: seat.seat_type)

        if trip_type == 'ROUND_TRIP':
            ret_seats = list(ret_seats)
            ret_seats.sort(key=lambda seat: seat.seat_type)


        # get passengers and sort by seat_type
        passengers = validated_data.get('passengers')

        no_of_passengers = len(passengers)
        #print("passengers := ", passengers)
        if len(seats) < len(passengers):
            raise ValidationError(f"Only {len(seats)} seats available!! not enough seats for booking all the passengers..")

        
        if trip_type == 'ROUND_TRIP':
            if len(ret_seats) < len(passengers):
              raise ValidationError(f"Only {len(ret_seats)} returning seats available!! not enough seats for booking all the passengers..")


        # sort passenegrs on seat_type basis
        passengers.sort(key=lambda passenger: passenger["seat_type"])

        #print("passengers after sort := ", passengers)
        #extra check_in cost calculaion

        extra_check_in_baggage = 0.0

        #adult and children count
        non_infants=0
        infants=0

        # book seats 
        for passenger in passengers:
            preference = passenger.get('seat_type')

            if passenger['type'] == "Adult" or passenger['type'] == 'Child':
                non_infants+=1
            elif passenger['type'] == 'Infant':
                infants+=1

            if passenger['check_in_baggage'] >= 15:
                extra_check_in_baggage += (passenger['check_in_baggage']-15.0) 
            #print("passenger after popping seat_type := ", passenger)
            
            if trip_type == 'ONE_WAY':
                booking = booking
            elif trip_type == 'ROUND_TRIP':
                booking = dep_booking

            allocated_seat = self.allocate_seat(booking, passenger, seats, preference)
            if not allocated_seat:
                allocated_seat = self.allocate_seat(booking, passenger, seats, 'ANY')  # Allocate any available seat
            
            #seat allocation for returning passegers
            if trip_type == 'ROUND_TRIP':
                 allocated_seat = self.allocate_seat(ret_booking, passenger, ret_seats, preference)
                 if not allocated_seat:
                    allocated_seat = self.allocate_seat(ret_booking, passenger, ret_seats, 'ANY')  # Allocate any available seat

                 ret_seats = Seats.objects.filter(flight=ret_flight, departure_date=ret_depart_date, is_booked=False)
                 ret_seats = list(ret_seats)
                 ret_seats.sort(key=lambda seat: seat.seat_type)

            # Update available seats after allocation
            seats = Seats.objects.filter(flight=flight, departure_date=depart_date, is_booked=False)
            seats = list(seats)
            seats.sort(key=lambda seat: seat.seat_type)

        #validate extra_check_in baggage
        if extra_check_in_baggage > 30:
            raise ValidationError("Extra check-in baggage can't be greater then 30 kgs")
    
        booking.extra_check_in_baggage = extra_check_in_baggage

        if trip_type == 'ROUND_TRIP' and flight.airline != ret_flight.airline:
            ret_booking.extra_check_in_baggage = extra_check_in_baggage
            dep_booking.extra_check_in_baggage = extra_check_in_baggage
        

        # Add total fare (base fare, GST, Discount coupon, Convenience Fee))
        if seat_class == 'ECONOMY':
            base_fare = flight.economy_fare
            gst = 0.05 * base_fare

        elif seat_class == 'BUISNESS':
            base_fare = flight.buisness_fare
            gst = 0.12 * base_fare 

        elif seat_class == 'FIRST_CLASS':
            base_fare = flight.first_class_fare
            gst = 0.12 * base_fare
        
        if trip_type == 'ROUND_TRIP':
            if seat_class == 'ECONOMY':
                ret_base_fare = ret_flight.economy_fare
                gst = 0.05 * ret_base_fare

            elif seat_class == 'BUISNESS':
                ret_base_fare = ret_flight.buisness_fare
                gst = 0.12 * ret_base_fare 

            elif seat_class == 'FIRST_CLASS':
                ret_base_fare = ret_flight.first_class_fare
                gst = 0.12 * ret_base_fare
        
        
        
        convenience_fee = 300


        if coupon_code:
            discount = 750.0
        else:
            discount = 0.0

        cute_charge = 50.00
        rcs_provision  = 50.00
        aviation_security_fee = 236.00
        passenger_service_fee = 91.00
        user_developement_fee = 61.00


        # extra baggage cost calculation
        extra_baggage_booking_mode = validated_data.get("extra_baggage_booking_mode")
        
        # add extra check in baggage booking mode INFO to the booking
        booking.extra_baggage_booking_mode = extra_baggage_booking_mode
        if trip_type == 'ROUND_TRIP' and flight.airline != ret_flight.airline:
            ret_booking.extra_baggage_booking_mode = extra_baggage_booking_mode
            dep_booking.extra_baggage_booking_mode = extra_baggage_booking_mode
        
        extra_check_in_baggage_price = 0.0

        if extra_baggage_booking_mode == 'AT_AIRPORT':
            extra_check_in_baggage_price = extra_check_in_baggage * 550

        elif extra_baggage_booking_mode == 'PRE_BOOKING':
            
            if extra_check_in_baggage <= 3:
                extra_check_in_baggage_price = 1350    
            
            elif extra_check_in_baggage > 3 and extra_check_in_baggage <= 5:
                extra_check_in_baggage_price = 2250    
            
            elif extra_check_in_baggage > 5 and  extra_check_in_baggage <= 10:
                extra_check_in_baggage_price = 4500    
            
            elif extra_check_in_baggage >10  and extra_check_in_baggage <= 15:
                extra_check_in_baggage_price = 6700    
            
            elif extra_check_in_baggage > 15 and extra_check_in_baggage <= 20:
                extra_check_in_baggage_price = 9000   

            elif extra_check_in_baggage > 20 and extra_check_in_baggage <= 30:
                extra_check_in_baggage_price = 13500     
        

        #print("total_fare from FlightBookingSerializer := ", no_of_passengers *(base_fare + gst) + convenience_fee - discount)
        booking.extra_baggage_price = extra_check_in_baggage_price
        if trip_type == 'ROUND_TRIP' and flight.airline != ret_flight.airline:
            ret_booking.extra_baggage_price = extra_check_in_baggage_price
            dep_booking.extra_baggage_price = extra_check_in_baggage_price

        total_fare = round(non_infants *(base_fare + gst) 
                                  + infants*(550+ 0.05*550)
                                  + convenience_fee
                                  + cute_charge
                                  + rcs_provision
                                  + aviation_security_fee
                                  + passenger_service_fee
                                  + user_developement_fee 
                                  + extra_check_in_baggage_price
                                  - discount)

        if trip_type == 'ROUND_TRIP':
            ret_total_fare = round(non_infants *(ret_base_fare + gst) 
                                  + infants*(550+ 0.05*550)
                                  + convenience_fee
                                  + cute_charge
                                  + rcs_provision
                                  + aviation_security_fee
                                  + passenger_service_fee
                                  + user_developement_fee 
                                  + extra_check_in_baggage_price
                                  - discount)

        if trip_type == 'ONE_WAY':
            booking.total_fare = total_fare
            booking.save()
            return booking

        if trip_type == 'ROUND_TRIP':

            dep_booking.total_fare = total_fare
            ret_booking.total_fare = ret_total_fare
            dep_booking.save()
            ret_booking.save()
            return dep_booking, ret_booking

            
                
    
    