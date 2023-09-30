from .models import *
from tqdm import tqdm
from booking_api.settings import BASE_DIR
from datetime import datetime, timedelta
import random 
from random import randrange
import pdfkit
from booking_api import settings
import os
from django.template.loader import get_template
from django.template import Context




# get number of lines
def get_number_of_lines(csv_file):

    with open(csv_file) as f:
        for i, l in enumerate(f):
            pass 
    
    return i+1

# Create Week Days
def createWeekDays():
    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

    for i, day in enumerate(days):
        Week.objects.create(name=day,number=int(i))
    

# Add Airports
def addAirports():
    file = open(BASE_DIR / "Data/airports.csv")
    print("Adding airport data....")
    
    total = get_number_of_lines("Data/airports.csv")


    for i, line in tqdm(enumerate(file), desc="Adding airports :", total=total):
        if i == 0:
            continue

        data = line.split(",")

        name = data[1].strip()
        city = data[0].strip()
        code = data[2].strip()
        country = data[3].strip()

        try:
            Airport.objects.create(name=name, city=city, code=code, country=country)
        except:
            print("couldn't add ")
            continue

    print("Done")

def addDomesticFlights():

    file = open(BASE_DIR / "Data/domestic_flights.csv")
    print("file := ", file)
    print("Adding domestic flights...")

    total = get_number_of_lines("Data/domestic_flights.csv")
    for i, line in tqdm(enumerate(file), total=total):

        if i == 0:
            continue

        data = line.split(",")

        origin = data[1].strip()
        destination = data[2].strip()
        depart_time = datetime.strptime(data[3].strip(), "%H:%M:%S").time()
        arrival_time = datetime.strptime(data[6].strip(), "%H:%M:%S").time()
        depart_week = int(data[4].strip())
        arrive_week = int(data[7].strip())
        duration = timedelta(hours=int(data[5].strip()[:2]), minutes=int(data[5].strip()[3:5]))
        flight_no = data[8].strip()
        airline = data[10].strip()
        economy_fare = float(data[11].strip() if data[11].strip() else 0.0)
        buisness_fare = economy_fare + randrange(int(economy_fare/2), int(economy_fare))
        first_class_fare = economy_fare + randrange(int(economy_fare), int(economy_fare + economy_fare/2))

        try:
            try:
                origin = Airport.objects.get(code=origin)
            except Airport.DoesNotExist:
                print(f"Airport with origin code {origin} does not exists!")
                continue
            
            try:
                destination = Airport.objects.get(code=destination)
            except Airport.DoesNotExist:
                print(f"Airport with origin code {destination} does not exists!")
                continue

            depart_weekday = Week.objects.get(number=depart_week)
            arrival_weekday = Week.objects.get(number=arrive_week)


            #create a flight db
            flight = Flight.objects.create(
                                            origin=origin,
                                            destination=destination,
                                            airline=airline, 
                                            flight_no=flight_no, 
                                            depart_time=depart_time,
                                            arrival_time=arrival_time,
                                            economy_fare=economy_fare,
                                            buisness_fare=buisness_fare,
                                            first_class_fare=first_class_fare,
                                            duration=duration
                                        ) 
            
            flight.departure_weekday.add(depart_weekday)
            flight.arrival_weekday.add(arrival_weekday)
            flight.save()

        except Exception as e:
            print(e)
        
    print("Done")



def addInternationalflights():

    file = open(BASE_DIR / "Data/international_flights.csv")
    print("Adding International Flights.....")
    total = get_number_of_lines("Data/international_flights.csv")

    for i, line in tqdm(enumerate(file), total=total):

        if i == 0:
            continue

        data = line.split(',')

        origin = data[1].strip()
        destination = data[2].strip()
        depart_time = datetime.strptime(data[3].strip(), "%H:%M:%S").time()
        arrival_time = datetime.strptime(data[6].strip(), "%H:%M:%S").time()
        depart_week = int(data[4].strip())
        arrive_week = int(data[7].strip())
        duration = timedelta(hours=int(data[5].strip()[:2]), minutes=int(data[5].strip()[3:5]))
        flight_no = data[8].strip()
        airline = data[10].strip()
        economy_fare = float(data[11].strip() if data[11].strip() else 0.0)
        buisness_fare = economy_fare + randrange(int(economy_fare/2), int(economy_fare))
        first_class_fare = buisness_fare + randrange(int(economy_fare/2), int(economy_fare))

        try:
            try:
                origin = Airport.objects.get(code=origin)
            except Airport.DoesNotExist:
                print(f"Airport with origin code {origin} does not exists!")
                continue
            
            try:
                destination = Airport.objects.get(code=destination)
            except Airport.DoesNotExist:
                print(f"Airport with origin code {destination} does not exists!")
                continue
            


            depart_weekday = Week.objects.get(number=depart_week)
            arrival_weekday = Week.objects.get(number=arrive_week)


            #create a flight db
            flight = Flight.objects.create(
                                            origin=origin,
                                            destination=destination,
                                            airline=airline, 
                                            flight_no=flight_no, 
                                            depart_time=depart_time,
                                            arrival_time=arrival_time,
                                            economy_fare=economy_fare,
                                            buisness_fare=buisness_fare,
                                            first_class_fare=first_class_fare,
                                            duration=duration
                                        ) 
            
            flight.departure_weekday.add(depart_weekday)
            flight.arrival_weekday.add(arrival_weekday)
            flight.save()

        except Exception as e:
            print(e)
        


    print("Done")
    



#generate random 6-digit  hex token
def generate_hex_token():
    token = ''.join(random.choice('0123456789ABCDEF')  for _ in range(6))
    return token 



# format duration from TimeDelta to 'Xh XXmins' format
def format_duration(duration):
        hours, seconds = divmod(duration.total_seconds(), 3600)
        minutes, seconds = divmod(seconds, 60)

        formatted_duration = ""
        
        if hours > 0:
            formatted_duration += f"{int(hours)}h "
        
        if minutes > 0:
            formatted_duration += f"{int(minutes)} mins"

        if not formatted_duration:
            formatted_duration = "0 mins"

        return formatted_duration

# utility function to generate receipt PDF FileName
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
    
    return pdf_filename