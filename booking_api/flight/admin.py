from django.contrib import admin

# Register your models here.
from .models import *


admin.site.register(User)
admin.site.register(Week)
admin.site.register(Airport)
admin.site.register(Passenger)
admin.site.register(Booking)
admin.site.register(Flight)
