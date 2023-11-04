## API Docs

BASE_URL := **https://flight-booking-rest-api-355b8ab4795a.herokuapp.com/v1/flight_api/**

endpoints := 
* **/login**
    - allowed methods = *POST*

    * **POST**
        - {{BASE-URL}}/login
        - body parameters 
            * username (**required**) 
                - type: string
                - description: usernameid of the user
                - max length: 150

            * password (**required**)
                - type: string
                - description: password 
                - max length: 128
            
            sample request body: 
            ```
            {
                "username": "admin",
                "password": "123"
            }
            ```

        - responses
            * 200 (**succesfully logged in**)
                - returns csrfToken and sessionId which needs to passed with every endpoint.

            sample response body: 
            ```
            {
                "message": "succesfully logged in",
                "fooo": "bar"
            }
            ```

            * 400 (**Bad Request**)
                - returns appropriate field error message 
            * 401 (**Unauthorized**)
                - returns appropriate error message
            * 500 (**Error internally from app side**)
                - returns the raised exception message

* **/register**
    Allowed Methods :- **POST**

    - **POST**
        - {{BASE_URL}}/register
        - body parameters
            * first_name (**required**)
                - type: string
                - description: First name of the user
                - max length: 150
            
            * last_name (**required**)
                - type: string
                - description: Last name of the user
                - max length: 150
            
            * mobile_no (**required**)
                - type: string
                - description: Mobile number of the user
                - max length: 14
                - example: "+91-8909675432"
            
            * email (**required**)
                - type: string
                - description: Email of the user
                - max length: 150
            
            * username (**required**)
                - type: string
                - description: username of the user
                - max length: 150
            
            * password (**required**)
                - type: string
                - description: password of the user
                - max length: 150
            
            * confirmation (**required**)
                - type: string
                - description: Confirmation 
                - max length: 150

            Sample Body :
            ```
            {
                "first_name": "rakesh",
                "last_name": "mariya",
                "mobile_no": "+91-243589072",
                "email": "kumar88777@gmail.com",
                "username": "rakesh",
                "password": "9999",
                "confirmation": "9999"
            }
            ```
        
        - responses
            * 201 (**succesfully created new user**)
                - returns info of newly registered user

            Sample response body: 
            ```
            {
                "id": 4,
                "first_name": "rakesh",
                "last_name": "mariya",
                "mobile_no": "+91-243589072",
                "email": "kumar88777@gmail.com",
                "username": "rakesh"
            }
            ```

            * 400 (**Bad Request**)
                - returns appropriate field error messages
                sample error response:
                ```
                {
                    "first_name": [
                        "This field is required."
                    ],
                    "last_name": [
                        "This field is required."
                    ],
                    "mobile_no": [
                        "This field is required."
                    ],
                    "password": [
                        "This field is required."
                    ],
                    "confirmation": [
                        "This field is required."
                    ]
                }
                ```

            * 401 (**Unauthorized**)
                - returns appropriate error message
            * 500 (**Error internally from app side**)
                - returns the raised exception message



* **/logout**
    - Allowed Method: **POST**

    
    * **POST**
    - {{BASE_URL}}/logout


    * Responses
        - 200 (**logged out successfully**)
            * message of succesfull logout
        - 400 (**Bad Request**)
            * Bad request message



* **/flights**
    - Allowed Methods: **GET**

    - GET
        - {{BASE_URL}}/flights
        - Header Params
            * X-CSRFToken
                - type: string
                - description: csrf token value returned after logging in 
                - example: 3CwkDICL51KCKCF3QbIflWlXvDiMN55S

        - Query Parameters.
            * round_trip
                - type: boolean
                - description: state whether journey is round_trip type

            * origin
                - type: string
                - description: city of origin
                - max length: 50
            
            * destination
                - type: string 
                - description: destination city
                - max length: 50
            
            * flight_number
                - type: string 
                - description: Flight Number of the flight
                - max length: 6
            
            * booking_date
                - type: string 
                - description: Flight Booking Date (date in indian format)
                - exmaple: '12-11-2023'
            
            * return_date
                - type: string 
                - description: Flight return date (Date in Indian format)
                - example: '18-09-2023'
            
            * seat_class
                - type: string
                - desciption: seat class of the seat (One of the following value ECONOMY, BUISNESS, PREMIUM_ECONOMY )
                - max length: 10
            
            * airlines
                - type: string
                - description: Name of the Airline
                - max length: 50
                - example: Spice Jet, Indigo etc.

            * departure_timing
                - type: string 
                - description: Departure Time of the Flight
            
            * price
                - type: float
                - desciption: Minimum price of the ticket
            


            - Responses
                * 200 (**successful request**)
                    - if no query params specified, returns paginated data of all the flights in the database
                    sample response 
                    ```
                    {               
                    "count": 1607,
                    "next": "http://flight-booking-rest-api-355b8ab4795a.herokuapp.com/v1/flight_api/flights?page=2",
                    "previous": null,
                    "result": [
                        {
                            "id": 1,
                            "flight_no": "G8334",
                            "airline": "Go First",
                            "origin_airport": "Chhatrapati Shivaji International Airport",
                            "origin_city": "Delhi",
                            "origin_code": "DEL",
                            "destination_airport": "Chhatrapati Shivaji International Airport",
                            "destination_city": "Mumbai",
                            "destination_code": "BOM",
                            "depart_time": "08:00:00",
                            "arrival_time": "10:10:00",
                            "duration": "02:10:00"
                        },
                        {
                            "id": 2,
                            "flight_no": "G8338",
                            "airline": "Go First",
                            "origin_airport": "Chhatrapati Shivaji International Airport",
                            "origin_city": "Delhi",
                            "origin_code": "DEL",
                            "destination_airport": "Chhatrapati Shivaji International Airport",
                            "destination_city": "Mumbai",
                            "destination_code": "BOM",
                            "depart_time": "10:55:00",
                            "arrival_time": "13:10:00",
                            "duration": "02:15:00"
                        }]
                    }
                    ```
                    -   If query params is present, returns appropriate flight list (both departing and returning), but without pagination
                    ```
                    {
                        "departing_flights": [
                            {
                                "id": 598,
                                "flight_no": "SG8702",
                                "airline": "SpiceJet",
                                "origin_airport": "Indira Gandhi International Airport",
                                "origin_city": "Mumbai",
                                "origin_code": "BOM",
                                "destination_airport": "Indira Gandhi International Airport",
                                "destination_city": "Delhi",
                                "destination_code": "DEL",
                                "depart_time": "16:00:00",
                                "arrival_time": "18:20:00",
                                "duration": "02:20:00"
                            },
                            
                            {
                                "id": 609,
                                "flight_no": "SG712",
                                "airline": "SpiceJet",
                                "origin_airport": "Indira Gandhi International Airport",
                                "origin_city": "Mumbai",
                                "origin_code": "BOM",
                                "destination_airport": "Indira Gandhi International Airport",
                                "destination_city": "Delhi",
                                "destination_code": "DEL",
                                "depart_time": "00:35:00",
                                "arrival_time": "03:00:00",
                                "duration": "02:25:00"
                            }
                        ],
                        "returning_flights": [
                            {
                                "id": 7,
                                "flight_no": "SG8169",
                                "airline": "SpiceJet",
                                "origin_airport": "Chhatrapati Shivaji International Airport",
                                "origin_city": "Delhi",
                                "origin_code": "DEL",
                                "destination_airport": "Chhatrapati Shivaji International Airport",
                                "destination_city": "Mumbai",
                                "destination_code": "BOM",
                                "depart_time": "19:45:00",
                                "arrival_time": "22:00:00",
                                "duration": "02:15:00"
                            }
                            
                        ]
                    }
                    ```
                * 400 (**Bad Request**)
                    - Apropriate error messages for the request
                    Sample Response:
                    ```
                    {
                        "message": "seat class must be their with price filter.."
                    }
                    ```
                * 500 (**Internal Server Error**)
        

* **/book/:flight_id**
    - Allowed Methods: POST

    - {{BASE_URL}}/book_flight/:flight_id

    - **POST**

        - Path Parameter
            - flight_id
                * type: integer
                * description: id of the flight retrieved from **/flights** call  

        - Header Parameters
            - X-CSRFToken
                - type: string
                - description: csrf token value returned after logging in 
                - example: 3CwkDICL51KCKCF3QbIflWlXvDiMN55S

        - Body Parameters 
                - seat_class (**required**)
                    - type: string
                    - description: Seat Class of the Passengers. Must be ECONOMY, BUISNESS or FIRST_CLASS
                    - example: ECONOMY

                - trip_type   (**required**)
                    - type: string
                    - description: Trip Type of the journey, must be ONE_WAY or ROUND_TRIP
                
                - flight_dep_date (**required**)
                    - type: string
                    - description: Flight Departure Date, in indian format ('dd-mm-yyyy')
                    - example: '12-11-2023'
                
                - return_flight
                    - type: integer
                    - description: ID of the return flight, required for ROUND_TRIP journeys
                    - example: 23
                
                - return_flight_dep_date (**required**)
                    - type: string
                    - description: Return Flight Departure date, in indian format ('dd-mm-yyyy')
                    - example: '12-11-2023'
                
                - extra_baggage_booking_mode (**required**)
                    - type: string
                    - Description: Whether extra baggage has been pre-booked or at airport. Must be one of the      values PRE-BOOKING or AT-AIRPORT
                    - example: PRE-BOOKING
                

            



