from django.db import models
from django.contrib.auth.models import AbstractUser
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
    ("CONFIRMAED", "Confirmed"),
    ("CANCELED", "Canceled")
)

REFUND_STATUS = (
    ('NO_INITIALISED', 'Not Initialised'),
    ('CREATED', 'Created')   
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
        return f"{self.name} {self.code}"


class Week(models.Model):
    name = models.CharField(max_length=10)
    week_number = models.IntegerField()

    def __str__(self):
        return f"{self.name}"
    

class Flight(models.Model):

    airline = models.CharField(max_length=50)
    flight_no = models.CharField(max_length=6)
    origin = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="departures")
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="arrivals")
    departure_weekday = models.ManyToManyField(Week, related_name="flights_of_the_day")
    arrival_weekday = models.ManyToManyField(Week)
    depart_time = models.TimeField(auto_now=False, auto_now_add=False)
    arrival_time = models.TimeField(auto_now=False, auto_now_add=False)
    is_nonstop = models.BooleanField(default=False)
    economy_fare = models.FloatField()
    buisness_fare = models.FloatField()
    first_class_fare = models.FloatField()


    def __str__(self):
        return f"{self.origin.code} to {self.destination.code} ({self.flight_number})"
    

class Passenger(models.Model):

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    gender = models.CharField(choices=GENDER, max_length=10)
    age = models.IntegerField()



class Booking(models.Model):

    booking_ref = models.CharField(max_length=6)
    payment_ref = models.CharField(max_length=50, blank=True, null=True)
    refund_status = models.CharField(max_length=20, choices=REFUND_STATUS, default="NOT_INITIALISED")
    last_updated = models.DateTimeField(auto_now=True)
    booked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="booked_tickets")
    booked_at = models.DateTimeField(auto_now=True)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="bookings")
    flight_dep_date = models.DateField()
    flight_arriv_date = models.DateField()
    mobile_no = models.CharField(max_length=12)
    passengers = models.ManyToManyField(Passenger, related_name="ticket_bookings")
    seat_class = models.CharField(choices=SEAT_CLASS, max_length=15)
    status = models.CharField(choices=TICKET_STATUS, max_length=15, default="PENDING")
    flight_fare = models.FloatField()
    coupon_used = models.CharField(max_length=10, blank=True)
    coupon_discount = models.FloatField()
    

    def __str__(self):
        return f"{self.booking_ref}"



class Layover(models.Model):

    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="layovers")
    city = models.CharField(max_length=20)
    duration = models.TimeField()
    next_flight = models.ForeignKey(Flight, on_delete=models.CASCADE)