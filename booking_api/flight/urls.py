from django.urls import re_path, path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('health_test', views.health_test, name="health-test"),
    path('register', views.register, name="register"),
    path('login', views.loginn, name="login"),
    path('airports', views.airports, name="airports"),
    path('airport/<int:airport_id>', views.airport, name="airport"),
    path('book_flight/<int:flight_id>', views.book_flight, name="book_flight"),
    path('payments/<str:booking_ref>', views.payments, name="payments"),
    path('bookings/<str:booking_ref>', views.bookings, name="bookings"),
    path('update_booking', views.update_booking, name="update-booking"),
    path('flights', views.flights, name="flights"),
    path('flight_details/<int:flight_id>', views.flight_details, name="flight_details"),
    path('test_pdf/<str:booking_ref>', views.test_pdf, name="test-pdf"),
    path('logout', views.logoutt, name="logout")
]

urlpatterns += static(settings.STATIC_URL, document=settings.STATIC_ROOT)