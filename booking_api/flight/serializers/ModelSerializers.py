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

        if price and seat_class:
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

    #journey_type = serializers.ChoiceField
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
        sort_by = attrs.get('sort_by')

        if sort_by and sort_by == 'PRICE':
            if not seat_class:
                raise ValidationError("seat_class  is must for ordering by price!!!")


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
    flight_dep_date = serializers.CharField(required=True, max_length=12)

            

    class Meta:
        model = Booking
        fields = ['booking_ref', 'flight', 'payment_status', 'booking_status', 'booked_at' ,'flight_dep_date', 'flight_arriv_date', 'seat_class' , 'passengers', 'coupon_used','extra_baggage_booking_mode','extra_check_in_baggage', 'extra_baggage_price','coupon_code','coupon_discount' ,'total_fare' ]
        extra_kwargs = {
            'seat_class': {'required': True},
            'flight_dep_date': {'required': True},
            'flight_arriv_date': {'required': False},
            'booking_ref': {'required': False} ,
            'flight': {'required': False} ,
            'total_fare': {'required': False},
            'extra_baggage_booking_mode': {'required': True},
            'extra_baggage_price': {'required': False ,'read_only': True},
            'extra_check_in_bagagge': {'required': False, 'read_only': True}
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

        if request and request.method == 'PUT':
            
            booking = self.context.get('booking')

            if not booking:
                raise ValidationError("Booking object Not passed to the Serializer !!!")

            if attrs['booking_status'] != 'CANCELED':
                raise ValidationError("Not Allowed !!")
            
            if booking.booking_status == 'CANCELED' or booking.booking_status == 'PENDING':
                raise ValidationError("Not a Valid Call !!!")
            
            return attrs

        date_str = attrs['flight_dep_date']
        date_obj = datetime.strptime(date_str, "%d-%m-%Y")

        passengers = attrs.get('passengers')

        if len(passengers) > 20:
            raise ValidationError("No More Than 20 seats are allowed to be booked in one go!!!!")
        
        # validate for hand baggage
        for passenger in passengers:
            hand_baggage = passenger.get('hand_baggage')
            
            if hand_baggage:
                if hand_baggage > 7.0:
                    raise ValidationError("Hand Baggage Per customer cannot be more thaan 7 kgs !! ")
        

        if date_obj < datetime.today():
            raise ValidationError("Invalid Departure date!")


        if not flight:
            raise ValidationError("flight context is not passed in the serializer")

        #if not request:
        #    raise ValidationError("Request context is not passed in the serializer")
        

        date_pattern = re.compile(r"^(0[1-9]|[1-2][0-9]|3[0-1])([-./])(0[1-9]|1[0-2])\2\d{4}$")
        match  = date_pattern.match(date_str)

        if not match:
            raise ValidationError("Invalid Departure Date Format. Correct format is `dd[.-/]mm[./-]year ")

        
        return attrs

    
    def to_representation(self, instance):
        ret = super().to_representation(instance)

        #print("reprentation := ", ret)
        request = self.context.get('request')
        flight = self.context.get('flight')

        print("flight := ", flight)

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
            try:

                booking = Booking.objects.filter(booking_ref=booking_ref).first()
                passengers  = booking.passengers.all()
                print("passengers from booking call := ", passengers)

                ret.pop('passengers') # pop the passengers

                print("ret after popping passengers := ", ret)
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
                    print("seat:= ", seat)
                    if not seat:
                        foo['seat'] = "NOT_ALLOCATED"
                    else:
                        foo['seat'] = seat.seat_no
                        foo["seat_type"]= seat.seat_type 
                        
                    passengers_list.append(foo)
                
                ret['passengers'] = passengers_list

                
            except Booking.DoesNotExist:
                raise ValidationError(f"Booking with {booking_ref} does not exists!!!")
                # get appropriate seats using booking_ref ....
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
                new_passenger.save()

                # add passenger to the booking list 
                booking.passengers.add(new_passenger)

                #allot this new passenger this unbooked seat
                seat.passenger = new_passenger
                seat.save()
                return seat
        return None
    
    def create(self, validated_data):
        
        booking_ref = generate_hex_token()
        flight = self.context.get('flight')
        request = self.context.get('request')
        seat_class = validated_data.get('seat_class')

       

        # Extract flight_dep_date and output arrival_dep_date 
        departure_date_string = validated_data.get('flight_dep_date')
        depart_datetime = datetime.strptime(departure_date_string, "%d-%m-%Y")

        depart_time = flight.depart_time
        arrival_time = flight.arrival_time

        # Calculate the timedelta for depart_time and arrival_time
        depart_timedelta = timedelta(hours=depart_time.hour, minutes=depart_time.minute, seconds=depart_time.second)
        arrival_timedelta = timedelta(hours=arrival_time.hour, minutes=arrival_time.minute, seconds=arrival_time.second)

        # Calculate the arrival_datetime by adding depart_timedelta to depart_datetime
        arrival_datetime = depart_datetime + arrival_timedelta

        # Extract the arrival date from arrival_datetime
        arrival_date_obj = arrival_datetime.date()
        depart_date = depart_datetime.date()



        # Instantiate Booking object
        booking = Booking.objects.create(
                                         booking_ref=booking_ref,
                                         flight=flight,
                                         booked_by=request.user,
                                         flight_dep_date=depart_date,
                                         flight_arriv_date=arrival_date_obj,
                                         seat_class=seat_class,
                                        )

        

        #Add coupon code
        coupon_code = validated_data.get('coupon_code')
        if coupon_code:
            booking.coupon_used = True
            booking.coupon_code = coupon_code
            booking.coupon_discount= 750

        # SEAT ALLOTMENT LOGIC 
        seats = Seats.objects.filter(flight=flight, departure_date=depart_date, is_booked=False)
        
        if not seats.exists():
            seats_to_create = []
            for i in range(1, 31):
                for seat_col in range(ord('A'), ord('G')):
                   
                    seat_no = f"{i:02d}{chr(seat_col)}"

                    if chr(seat_col) == 'A' or chr(seat_col) == 'F':
                        seat_type = 'WINDOW'
                    elif chr(seat_col) == 'B' or chr(seat_col) == 'E':
                        seat_type = 'MIDDLE'
                    elif chr(seat_col) == 'C' or chr(seat_col) == 'D':
                        seat_type = 'AISLE'
                    
                    Seats.objects.create(flight=flight, departure_date=depart_date, seat_no=seat_no, seat_type=seat_type)
                     
            # Use atomic transaction to speed up the bulk db creation
            #with transaction.atomic():
            #    Seats.objects.bulk_create(seats_to_create)
    

        # sort seats as per seat_type
        seats = list(seats)
        seats.sort(key=lambda seat: seat.seat_type)

        # get passengers and sort by seat_type
        passengers = validated_data.get('passengers')

        no_of_passengers = len(passengers)
        #print("passengers := ", passengers)
        if len(seats) < len(passengers):
            raise ValidationError(f"Only {len(seats)} seats available!! not enough seats for booking all the passengers..")

        # sort passenegrs on seat_type basis
        passengers.sort(key=lambda passenger: passenger["seat_type"])

        #print("passengers after sort := ", passengers)
        #extra check_in cost calculaion

        extra_check_in_baggage = 0.0

        # book seats 
        for passenger in passengers:
            preference = passenger.get('seat_type')

            if passenger['check_in_baggage'] >= 15:
                extra_check_in_baggage += (passenger['check_in_baggage']-15.0) 
            #print("passenger after popping seat_type := ", passenger)
            

            allocated_seat = self.allocate_seat(booking, passenger, seats, preference)
            
            if not allocated_seat:
                allocated_seat = self.allocate_seat(booking, passenger, seats, 'ANY')  # Allocate any available seat
            
            # Update available seats after allocation
            seats = Seats.objects.filter(flight=flight, departure_date=depart_date, is_booked=False)
            seats = list(seats)
            seats.sort(key=lambda seat: seat.seat_type)

        #validate extra_check_in baggage
        if extra_check_in_baggage > 30:
            raise ValidationError("Extra check-in baggage can't be greater then 30 kgs")
    
        booking.extra_check_in_baggage = extra_check_in_baggage

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

        booking.total_fare = round(no_of_passengers *(base_fare + gst) 
                                  + convenience_fee
                                  + cute_charge
                                  + rcs_provision
                                  + aviation_security_fee
                                  + passenger_service_fee
                                  + user_developement_fee 
                                  + extra_check_in_baggage_price
                                  - discount)

        #save booking object
        booking.save()

        return booking