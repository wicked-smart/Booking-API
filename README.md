
# Flight-Booking-API


## Quick Introduction
* A Flight Booking REST API that let users search and book flight tickets (one-way/round-trip) across 1000+ Domestic and Interntional airports and different seat classes (Economy/Buisness/First class ) in 3-step (search, book and make payments , receive ticket in PDFs). 


## Infrastructure setup
* The API runs on docker compose having separate container for web (django), db (postgres), redis(redis as broker and cache) , worker(celery) and ngrok(ngrok).

    ![containers](images/containers.drawio.png)

* docker compose build session

    ![compose build](images/demo.svg)





## Features and Notes
*  Users get their API Key after they sign-up/register succesfully
* Allow users to search flights using 11+ filters like departure date, return date, flight number, origin city, airlines, flight duration, price etc. with response customised as per journey type (one-way/round-trip).
* Users can book the  flight ticket with passenger data like departure date, flight (departing and/or returning ), seat class etc. and receive **booking_ref** in return
*  Make payments using the **booking_ref** , validate the returned hooks url and click on the response link to receive ticket PDF
* Received PDF ticket contains information of the booking date and time, flight , journey type, baggage information, passenger allocated seats, fare rules and charges and finally , boarding instruction
* For round trip flight, if the return journey airline is different than departing one, separate tickets are generated while, if having same airline case..single ticket is generated.
* All these PDFs generation tasks are offloaded to celery workers to process it asynchronously and at scale.
* Allow users to cancel ticket , calculate appropriate cancellation charges based on difference between departing and cancelling datetime , issue refunds and refund receipt pdf.
* Also, Cancellation logic is customised for separate and single airline. For case of same airline, user has to explicitely state DEPARTING or RETURNING cancellation refund or BOTH.
* After validating stripe returned url , the internal django endpoint handles the webhook events like PaymentIntent Created , Succeeded, refunded etc.
* This architecture of exposing internal Dajngo endpoint rather than having separate Flask one to handle webhooks, shaves off around 70% response time giving very snappy user experience.
*  Various utility scripts like for initialising the database with airports data, formating date time in human readable format.
* Once user completes payment, seat is allocated as per his/her preferance (Window/Aisle/Middle). Bulk booking is also allowed but not more than max 10 at a time , subject to availability
* Users are allowed to add coupons availing discounts, check-in baggage information etc. while booking tickets
* If two passengers have same First, Middle and Last names, internally a UUID is allocated to each one to mark them unique
* API has been deployed to Heroku, with the generated PDFs uploaded to AWS S3 as heroku itself have ephemeral file system.
* For Payments , their is stripe integration with registed webhook events like payments intent created, succeeded, refunded etc.



## Future Work

* Fix bugs and write various unit , performance and load tests 
* Optimise ORM queries/ use **select_related** and **prefetch_related** or maybe use **raw sql queries** to lower the overall response times 
* ‌Ability to add custom debit and credit cards as payment methods and do live payments
* Allow users to query on Stops and Layovers 
*  Also, Add feature to book **multi-city** flights
* Fix the very strange bug of **400 BAD REQUEST** on cancelling returning ticket of ROUND_TRIP flight (reason being refunds webhook event data containing same booking_ref for both DEPARTING and RETURNING journey type!)

## Live Demo

 [![Video]](https://github.com/wicked-smart/Flight-Booking-API/assets/46626672/d8caf614-9dae-467e-b777-e225344bf5af)



## Link to Documentation

## How to Run and Test Locally

For this project to run locally, you need to install [docker](https://docs.docker.com/engine/install/) and [docker-compose](https://docs.docker.com/compose/install/).

After installing , clone this repo
```
$ git clone https://github.com/wicked-smart/Flight-Booking-API.git
$ cd Flight-Booking-API/

```

Then, simplly run the docker compose service to build and spin docker compose service
```
$ docker-compose -f docker-compose.prod.yml up -d --build 
```

Your api is up and running on http://localhost:8000/v1/flight_api/ .

Now visit  http://localhost:4040, find ngrok UUID and paste it in your stripe test API webhook settngs with url **<uuid>/webhook**

You can verify if it's working properly by runining and then looking the logs
```
$ docker-compose -f docker-compose.prod.yml logs -f
```

You can spin down the docker compose service by runing
```
$ docker-compose -f docker-compose.prod.yml down -v
```

 Check documentation to understand all the endpoints and launch postman to test different API endpoints 


## Deploying on Heorku

Deploying to heroku using its container registry and not heroku.yml.

1. Login to heroku container 
```
$ heroku container:login -a APP_NAME
```
2. Rename Dockerfile to Dockerfile.web and Dcokerfile.celery to Dockerfile.worker , then recursively push to the registry

```
$ sudo heroku container:push --recursive -a APP_NAME
```
![docker build](images/demo_output.svg)

3. After it is succesfully built and pushed ,we release the web and worker containers to heroku using herokurelease command

```
$ sudo herou container:release web worker -a APP_NAME
```

4. Now, we will dump the fixtures into app's fixtures directory , update settings.py file to include remote db'd credentials and then load the data.

```
$ cd booking_api/
$ python3 manage.py dumpdata --indent 2 > flight/fixtures/db.json
$ python3 manage.py loaddata -v 3 flight/fixtures/db.json
```

![loaddata output](images/fixture.png)

