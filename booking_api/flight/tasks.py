from celery import shared_task
from .models import *
import os
from django.template.loader import get_template
from django.template import Context
from .utils import *

@shared_task
def add(a,b):
    return a+b

@shared_task
def generate_reciept_pdf(booking_ref):
    booking = Booking.objects.get(booking_ref=booking_ref)

    receipt_url = booking.refund_receipt_url
    while receipt_url is None:
        receipt_url = booking.refund_receipt_url

    print("receipt url := ", receipt_url)

    pdf_options = {
                    'page-size': 'Letter',
                    'margin-top': '0.75in',
                    'margin-right': '0.75in',
                    'margin-bottom': '0.75in',
                    'margin-left': '0.75in'
                }
    
    pdf = pdfkit.from_url(receipt_url, False, pdf_options)
    pdf_filename = f"refund_receipt_{booking.booking_ref}.pdf"

    pdf_path = os.path.join(settings.MEDIA_ROOT, f"refunds/{pdf_filename}")
    with open(pdf_path, 'wb') as pdf_file:
        pdf_file.write(pdf)
    
    return pdf_filename

@shared_task
def generate_ticket_pdf(booking_ref):

    booking = Booking.objects.get(booking_ref=booking_ref)

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
    #print("rendered_template := ", rendered_template)

    #pdfkit using from string
    pdf = pdfkit.from_string(rendered_template, False, pdf_options)

    #save ticket in MEDIA_ROOT
    pdf_filename = f"booking_ticket_{booking.booking_ref}.pdf"

    pdf_path = os.path.join(settings.MEDIA_ROOT, f"tickets/{pdf_filename}")
    with open(pdf_path, 'wb') as pdf_file:
        pdf_file.write(pdf)
    
    #return pdf_filename