from django.contrib import admin

# Register your models here.
from .models import *

class SeatsAdmin(admin.ModelAdmin):
    list_display = ['flight', 'seat_no', 'seat_type', 'departure_date', 'passenger', 'is_booked']
    

    ordering = ['seat_no']  # Order seats by seat_no in ascending order

admin.site.register(Seats, SeatsAdmin)

admin.site.register(User)
admin.site.register(Week)
admin.site.register(Airport)
admin.site.register(Passenger)
admin.site.register(Booking)
admin.site.register(Flight)
admin.site.register(Layover)
