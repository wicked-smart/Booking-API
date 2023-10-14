from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import timedelta
import uuid 

# Create your models here.


#various choice tuples

GENDER = (
    ('MALE', 'Male'),
    ('FEMALE', 'Female'),
    ('OTHER', 'Others')
)

SEAT_CLASS = (
    ("ECONOMY", "Economy"),
    ("BUISNESS", "Buisness"),
    ("FIRST_CLASS", "First_class")
)


TICKET_STATUS = (
    ("PENDING", "Pending"),
    ("CONFIRMED", "Confirmed"),
    ("CANCELED", "Canceled")
)

REFUND_STATUS = (
    ('NO_INITIALISED', 'Not Initialised'),
    ('CREATED', 'Created')   
)

PAYMENT_STATUS = (
    ('SUCCEDED', 'Succeded'),
    ('CANCELED', 'Canceled'),
    ('REFUNDED', 'Refunded'),
    ('FAILED', 'Failed'),
    ('PROCESSING', 'Processing'),
    ('NOT_ATTEMPTED', 'Not Attempted')
)

SEAT_TYPE = (
    		('WINDOW', 'Window'),
    		('AISLE', 'Aisle'),
    		('MIDDLE', 'Middle')
    	)

EXTRA_BAGGAGE_BOOKING_MODE = (
    ('PRE-BOOKING', 'Pre_booking'),
    ('AT_AIRPORT', 'At_Airport')
)

TRIP_TYPE = (
    ('ROUND_TRIP', 'Round Trip'),
    ('ONE_WAY', 'One Way')
)

SEPERATE_TICKET = (
    ('YES', "Yes"),
    ('NO', "No")
)



class User(AbstractUser):

    confirmation = models.CharField(max_length=128, default="test")
    mobile_no = models.CharField(max_length=14, default="+91-XXXXXXXXXX")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    
class Airport(models.Model):

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=3)
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=60)

    def __str__(self):
        return f"{self.city} ({self.code})"


class Week(models.Model):
    name = models.CharField(max_length=10)
    number = models.IntegerField()

    def __str__(self):
        return f"{self.name}"
    

class Flight(models.Model):

    airline = models.CharField(max_length=50)
    flight_no = models.CharField(max_length=6)
    flight_code = models.CharField(max_length=3, default='CO')
    origin = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="departures")
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="arrivals")
    departure_weekday = models.ManyToManyField(Week, related_name="flights_of_the_day")
    arrival_weekday = models.ManyToManyField(Week)
    seats_available = models.IntegerField(default=220)
    depart_time = models.TimeField(auto_now=False, auto_now_add=False)
    arrival_time = models.TimeField(auto_now=False, auto_now_add=False)
    is_nonstop = models.BooleanField(default=True)
    economy_fare = models.FloatField()
    buisness_fare = models.FloatField()
    first_class_fare = models.FloatField()
    duration = models.DurationField(default=timedelta(hours=1))


    def __str__(self):
        return f"{self.origin.code} to {self.destination.code} ({self.flight_no})"
    
    

    

class Passenger(models.Model):

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(choices=GENDER, max_length=10)
    age = models.IntegerField()
    type = models.CharField(max_length=10, blank=True)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False)
    seat_type = models.CharField(choices=SEAT_TYPE, default='WINDOW', max_length=15)
    seat_no = models.CharField(max_length=3, default='00A')
    hand_baggage = models.FloatField(default=0.0)
    check_in_baggage = models.FloatField(default=0.0)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.unique_id})"

    

class Booking(models.Model):

    booking_ref = models.CharField(max_length=6)
    payment_ref = models.CharField(max_length=50, blank=True, null=True)
    payment_status = models.CharField(choices=PAYMENT_STATUS, max_length=15, default="NOT_ATTEMPTED")
    refund_status = models.CharField(max_length=20, choices=REFUND_STATUS, default="NOT_INITIALISED")
    refund_receipt_url = models.URLField(max_length=500, blank=True, null=True, default=None)
    last_updated = models.DateTimeField(auto_now=True)
    booked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="booked_tickets")
    booked_at = models.DateTimeField(auto_now_add=True)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="bookings")
    flight_dep_date = models.DateField()
    flight_arriv_date = models.DateField()
    passengers = models.ManyToManyField(Passenger, related_name="ticket_bookings")
    seat_class = models.CharField(choices=SEAT_CLASS, max_length=15)
    booking_status = models.CharField(choices=TICKET_STATUS, max_length=15, default="PENDING")
    coupon_used = models.BooleanField(default=False)
    coupon_code = models.CharField(max_length=10, blank=True)
    coupon_discount = models.FloatField(default=0.0)
    total_fare = models.FloatField(default=0.0)
    extra_baggage_booking_mode = models.CharField(choices=EXTRA_BAGGAGE_BOOKING_MODE, blank=True, null=True)
    extra_baggage_price = models.FloatField(default=0.0)
    extra_check_in_baggage = models.FloatField(default=0.0)
    trip_type = models.CharField(choices=TRIP_TYPE, max_length=15, default='ONE WAY')
    separate_ticket = models.CharField(choices=SEPERATE_TICKET, max_length=3, null=True, blank=True)
    other_booking_ref=models.CharField(max_length=6, null=True, blank=True)
    # return_flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="Bookings", blank=True, null=True)
    # return_flight_dep_date = models.DateField(blank=True, null=True)
    # return_flight_arriv_date = models.DateField(blank=True, null=True)
    

    def __str__(self):
        return f"{self.booking_ref}"



class Layover(models.Model):

    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="layovers")
    city = models.CharField(max_length=20)
    duration = models.TimeField()
    airport_change = models.BooleanField(default=False)
    connecting_flight = models.ForeignKey(Flight, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.flight}"
    


    	
    	
class Seats(models.Model):
    
    id = models.BigAutoField(primary_key=True) 
    seat_type = models.CharField(max_length=10,choices=SEAT_TYPE, blank=True)
    seat_no = models.CharField(max_length=3, blank=True, null=True)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="seats")
    departure_date = models.DateField()
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE, related_name="seats", blank=True, null=True)
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.seat_no} ({self.seat_type})"
    
    class Meta:
        unique_together = ['flight', 'departure_date', 'seat_no']
        

