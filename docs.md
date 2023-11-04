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
                - returns this message of user does not have proper permission for this request
            
            * 403 (**Forbidden**)
                    - returns this error if user is not authenticated  or missing some csrf token in the request header
                    - sample error message 
                    ```
                    {
                        "detail": "CSRF Failed: CSRF token from the 'X-Csrftoken' HTTP header incorrect."
                    }
                    ```
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
        
        *  401 (**Unauthorized**)
                - returns this message of user does not have proper permission for this request

        * 403 (**Forbidden**)
            - returns this error if user is not authenticated  or missing some csrf token in the request header
            - sample error message 
            ```
            {
                "detail": "CSRF Failed: CSRF token from the 'X-Csrftoken' HTTP header incorrect."
            }
            ```
        



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
                - desciption: seat class of the seat (One of the following value **ECONOMY**, **BUISNESS**, **PREMIUM_ECONOMY** )
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
                
                 *  401 (**Unauthorized**)
                     - returns this message if user does not have proper permission for this request

                 * 403 (**Forbidden**)
                     - returns this error if user is not authenticated  or missing some csrf token in the request header
                     - sample error message 
                     ```
                     {
                        "detail": "CSRF Failed: CSRF token from the 'X-Csrftoken' HTTP header incorrect."
                     }
                     ```
                * 500 (**Internal Server Error**)
                    - appropriate internal server error message
        

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

            *  seat_class (**required**)
                - type: string
                - description: Seat Class of the Passengers. Must be **ECONOMY**, **BUISNESS** or **FIRST_CLASS**
                - example: ECONOMY

            * trip_type   (**required**)
                - type: string
                - description: Trip Type of the journey, must be **ONE_WAY** or **ROUND_TRIP**
            
            *  flight_dep_date (**required**)
                - type: string
                - description: Flight Departure Date, in indian format (**'dd-mm-yyyy'**)
                - example: '12-11-2023'
            
            *  return_flight
                - type: integer
                - description: ID of the return flight, required for **ROUND_TRIP** journeys
                - example: 23
            
            *  return_flight_dep_date (**required**)
                - type: string
                - description: Return Flight Departure date, in indian format (**'dd-mm-yyyy'**)
                - example: '12-11-2023'
            
            *  extra_baggage_booking_mode (**required**)
                - type: string
                - Description: Whether extra baggage has been pre-booked or at airport. Must be one of the      values **PRE-BOOKING** or **AT-AIRPORT**
                - example: **PRE-BOOKING**
            
            * passengers (**required**)
                - type: array of objects
                - Description: Passengers for the flight
                - object: 
                    * first_name (**required**)
                        - type: string 
                        - description: First Name of the passenger
                        - max length: 100
                        - example: "Ravi"

                    * last_name (**required**)
                        - type: string
                        - desription: Last Name of the passengers
                        - max length: 100
                        - example: "kumar"
                    
                    * gender (**required**)
                        - type: string
                        - deacription: Gender of the Passenger, Must be either **MALE**, **FEMALE** or **OTHERS**
                        - max length: 10
                        - example: FEMALE
                    
                    * age (**required**)
                        - type: integer
                        - description: Age of the passenger
                        - example: 21
                    
                    * type (**required**)
                        - type: string
                        - description: Age class of the passeneger, can be either Adult, child, infant, old etc.
                        - example: Infant

                    *  seat_type (**required**)
                        - type: string
                        - description: Seat preference of the passenger , Must be either **AISLE**, **WINDOW** or **MIDDLE**
                        - example: WINDOW
                    
                    * hand_baggage (**required**)
                        - type: float
                        - desciption: Hand Baggage weight to be carried with the Passenger (in Kgs)
                        - example: 6.5 
                    
                    * check_in_baggage (**required**)
                        - type: float
                        - description: Check in baggage weight to be checked in on the flight (in kgs)
                        - example: 12.6
                
                - Example:

                    ```
                    
                    {
                        "first_name": "Saul",
                        "last_name": "Goodman",
                        "gender": "MALE",
                        "age": 38,
                        "type": "Adult",
                        "seat_type": "WINDOW",
                        "hand_baggage": 6.5,
                        "check_in_baggage": 16.0
                     }

                    ```
            - Sample Booking object
            ```
            
            {
                "seat_class": "ECONOMY",
                "flight_dep_date": "02-11-2023",
                "extra_baggage_booking_mode": "AT_AIRPORT",
                "trip_type": "ROUND_TRIP",
                "return_flight": 23,
                "return_flight_dep_date": "12-11-2023",
                "passengers": [
                    {
                        "first_name": "Saul",
                        "last_name": "Goodman",
                        "gender": "MALE",
                        "age": 38,
                        "type": "Adult",
                        "seat_type": "WINDOW",
                        "hand_baggage": 6.5,
                        "check_in_baggage": 16.0
                    },

                    {
                        "first_name": "Ashwin",
                        "last_name": "Fukra",
                        "gender": "MALE",
                        "age": 32,
                        "type": "Adult",
                        "seat_type": "AISLE",
                        "check_in_baggage": 14.0
                    },
                    {
                        "first_name": "Roushan",
                        "last_name": "Kumar",
                        "gender": "MALE",
                        "age": 28,
                        "type": "Adult",
                        "seat_type": "WINDOW",
                        "check_in_baggage": 14.0
                    }
                ]
            }


            ```


        - Response

            * 200 (**succesfully booked**)
                - if trip_type is ONE_WAY , response will contain on about ticket booked for departing or returning flight 

                Sample Response for ONE_WAY
                ```
                {
                    "booking_ref": "BBDF77",
                    "flight": 598,
                    "payment_status": "NOT_ATTEMPTED",
                    "trip_type": "ONE WAY",
                    "booking_status": "PENDING",
                    "booked_at": "2023-11-04T09:04:34.001227+05:30",
                    "flight_dep_date": "2023-11-05",
                    "flight_arriv_date": "2023-11-05",
                    "seat_class": "ECONOMY",
                    "coupon_used": false,
                    "extra_baggage_booking_mode": "AT_AIRPORT",
                    "extra_check_in_baggage": 1.0,
                    "extra_baggage_price": 550.0,
                    "total_fare": 17935.0,
                    "separate_ticket": null,
                    "other_booking_ref": null,
                    "flight_depart_time": "16:00:00",
                    "flight_arrival_time": "18:20:00",
                    "passengers": [
                        {
                            "first_name": "Ashwin",
                            "last_name": "chowbe",
                            "gender": "MALE",
                            "age": 32,
                            "age_category": "Adult",
                            "hand_baggage": 0.0,
                            "check_in_baggage": 14.0,
                            "seat": "01C",
                            "seat_type": "AISLE"
                        },
                        {
                            "first_name": "Abhishek",
                            "last_name": "kumar",
                            "gender": "MALE",
                            "age": 38,
                            "age_category": "Adult",
                            "hand_baggage": 6.5,
                            "check_in_baggage": 16.0,
                            "seat": "01A",
                            "seat_type": "WINDOW"
                        },
                        {
                            "first_name": "Roushan",
                            "last_name": "Kumar",
                            "gender": "MALE",
                            "age": 28,
                            "age_category": "Adult",
                            "hand_baggage": 0.0,
                            "check_in_baggage": 14.0,
                            "seat": "01F",
                            "seat_type": "WINDOW"
                        }
                    ]
                }
                ```

                - If journey is round trip and both departing and returning airlines are different , response will contain separate tickt info for both airlines

                Sample Response for this case:
                ```
                {
                    "booking": {
                        "booking_ref": "452F47",
                        "flight": 598,
                        "payment_status": "NOT_ATTEMPTED",
                        "trip_type": "ROUND_TRIP",
                        "booking_status": "PENDING",
                        "booked_at": "2023-11-04T09:11:23.065038+05:30",
                        "flight_dep_date": "2023-11-05",
                        "flight_arriv_date": "2023-11-05",
                        "seat_class": "ECONOMY",
                        "coupon_used": false,
                        "extra_baggage_booking_mode": "AT_AIRPORT",
                        "extra_check_in_baggage": 1.0,
                        "extra_baggage_price": 550.0,
                        "coupon_code": "",
                        "coupon_discount": 0.0,
                        "total_fare": 17903.0,
                        "flight_depart_time": "16:00:00",
                        "flight_arrival_time": "18:20:00",
                        "passengers": [
                            {
                                "first_name": "Ashwin",
                                "last_name": "chowbe",
                                "gender": "MALE",
                                "age": 32,
                                "age_category": "Adult",
                                "hand_baggage": 0.0,
                                "check_in_baggage": 14.0,
                                "seat": "01D",
                                "seat_type": "AISLE"
                            },
                            {
                                "first_name": "Abhishek",
                                "last_name": "kumar",
                                "gender": "MALE",
                                "age": 38,
                                "age_category": "Adult",
                                "hand_baggage": 6.5,
                                "check_in_baggage": 16.0,
                                "seat": "02A",
                                "seat_type": "WINDOW"
                            },
                            {
                                "first_name": "Roushan",
                                "last_name": "Kumar",
                                "gender": "MALE",
                                "age": 28,
                                "age_category": "Adult",
                                "hand_baggage": 0.0,
                                "check_in_baggage": 14.0,
                                "seat": "02F",
                                "seat_type": "WINDOW"
                            }
                        ]
                    },
                    "return_booking": {
                        "booking_ref": "154B6D",
                        "flight": 23,
                        "payment_status": "NOT_ATTEMPTED",
                        "trip_type": "ROUND_TRIP",
                        "booking_status": "PENDING",
                        "booked_at": "2023-11-04T09:11:23.067527+05:30",
                        "flight_dep_date": "2023-11-12",
                        "flight_arriv_date": "2023-11-12",
                        "seat_class": "ECONOMY",
                        "coupon_used": false,
                        "extra_baggage_booking_mode": "AT_AIRPORT",
                        "extra_check_in_baggage": 1.0,
                        "extra_baggage_price": 550.0,
                        "coupon_code": "",
                        "coupon_discount": 0.0,
                        "total_fare": 17261.0,
                        "flight_depart_time": "18:20:00",
                        "flight_arrival_time": "20:35:00",
                        "passengers": [
                            {
                                "first_name": "Ashwin",
                                "last_name": "chowbe",
                                "gender": "MALE",
                                "age": 32,
                                "age_category": "Adult",
                                "hand_baggage": 0.0,
                                "check_in_baggage": 14.0,
                                "seat": "02D",
                                "seat_type": "AISLE"
                            },
                            {
                                "first_name": "Abhishek",
                                "last_name": "kumar",
                                "gender": "MALE",
                                "age": 38,
                                "age_category": "Adult",
                                "hand_baggage": 6.5,
                                "check_in_baggage": 16.0,
                                "seat": "04A",
                                "seat_type": "WINDOW"
                            },
                            {
                                "first_name": "Roushan",
                                "last_name": "Kumar",
                                "gender": "MALE",
                                "age": 28,
                                "age_category": "Adult",
                                "hand_baggage": 0.0,
                                "check_in_baggage": 14.0,
                                "seat": "04F",
                                "seat_type": "WINDOW"
                            }
                        ]
                    }
                }
                ```
                - lastly, if both departing and returning airlines is same
                Sample Response:
                ```
                {
                    "booking_ref": "ACB4C4",
                    "flight": 598,
                    "payment_status": "NOT_ATTEMPTED",
                    "trip_type": "ROUND_TRIP",
                    "booking_status": "PENDING",
                    "booked_at": "2023-11-04T10:10:20.341760+05:30",
                    "flight_dep_date": "2023-11-05",
                    "flight_arriv_date": "2023-11-05",
                    "seat_class": "ECONOMY",
                    "coupon_used": false,
                    "extra_baggage_booking_mode": "AT_AIRPORT",
                    "extra_check_in_baggage": 1.0,
                    "extra_baggage_price": 550.0,
                    "coupon_code": "",
                    "coupon_discount": 0.0,
                    "total_fare": 17877.0,
                    "flight_depart_time": "19:45:00",
                    "flight_arrival_time": "22:00:00",
                    "passengers": [
                        {
                            "first_name": "Ashwin",
                            "last_name": "chowbe",
                            "gender": "MALE",
                            "age": 32,
                            "age_category": "Adult",
                            "hand_baggage": 0.0,
                            "check_in_baggage": 14.0,
                            "seat": "02C",
                            "seat_type": "AISLE"
                        },
                        {
                            "first_name": "Abhishek",
                            "last_name": "kumar",
                            "gender": "MALE",
                            "age": 38,
                            "age_category": "Adult",
                            "hand_baggage": 6.5,
                            "check_in_baggage": 16.0,
                            "seat": "03A",
                            "seat_type": "WINDOW"
                        },
                        {
                            "first_name": "Roushan",
                            "last_name": "Kumar",
                            "gender": "MALE",
                            "age": 28,
                            "age_category": "Adult",
                            "hand_baggage": 0.0,
                            "check_in_baggage": 14.0,
                            "seat": "03F",
                            "seat_type": "WINDOW"
                        }
                    ],
                    "return_flight": 7,
                    "return_flight_dep_date": "2023-11-12",
                    "return_flight_arrival_date": "2023-11-12",
                    "return_booking_status": "PENDING",
                    "return_total_fare": 16716.0,
                    "return_passengers": [
                        {
                            "first_name": "Ashwin",
                            "last_name": "chowbe",
                            "gender": "MALE",
                            "age": 32,
                            "age_category": "Adult",
                            "hand_baggage": 0.0,
                            "check_in_baggage": 14.0,
                            "seat": "01C",
                            "seat_type": "AISLE"
                        },
                        {
                            "first_name": "Abhishek",
                            "last_name": "kumar",
                            "gender": "MALE",
                            "age": 38,
                            "age_category": "Adult",
                            "hand_baggage": 6.5,
                            "check_in_baggage": 16.0,
                            "seat": "01A",
                            "seat_type": "WINDOW"
                        },
                        {
                            "first_name": "Roushan",
                            "last_name": "Kumar",
                            "gender": "MALE",
                            "age": 28,
                            "age_category": "Adult",
                            "hand_baggage": 0.0,
                            "check_in_baggage": 14.0,
                            "seat": "01F",
                            "seat_type": "WINDOW"
                        }
                    ]
                }
                ```

            *  401 (**Unauthorized**)
                - returns this message if user does not have proper permission for this request

            *  403 (**Forbidden**)
                - returns this error if user is not authenticated  or missing some csrf token in the request header
                - sample error message 
                ```
                {
                    "detail": "CSRF Failed: CSRF token from the 'X-Csrftoken' HTTP header incorrect."
                }
                ```
            *  500 (**Internal Server Error**)
                - returns internal server error with proper exception handling message


* **/bookings/:booking_ref**
    Allowed Methods: GET, PUT
    {{BASE_URL}}/bookings/:booking_ref
    **GET**

    **PUT**
    - Header Parameters
        - X-CSRFToken
            - type: string
            - description: csrf token value returned after logging in                
            - example: 3CwkDICL51KCKCF3QbIflWlXvDiMN55S


    - Path Parameters
        * booking_ref
            - type: string
            - Description: booking_ref returned on booking a flight
            - max length: 6
            - example: /bookings/DE56RH

    - Body Parameters
        * booking_status (**required**)
            - type: string
            - Description: Desired booking status of the tickets, **CANCELED** in this case
            - max length: 10
        
        * cancellation_type 
            - type: string
            - Description: In case of round trip flights, it is very **required**, must have mentioned whether **DEPARTING**, **RETURNING** or **BOTH**
            - max length: 20
            - example: DEPARTING
        
        - sample PUT body example for cancelling round_trip flights
        ```
        {
            "booking_status": "CANCELED",
            "cancellation_type": "RETURNING"
        }
        ```
    - Responses

        * 200 (**succesfully cancelled**)
            - if cancellation is successfull , it returns appropriate message of successfull cancellation and url link to receipt pdf deacribing returned amount 

            ```
            {
                "message": "succesfully cancelled ticket , receipt PDF is being generated. You can download it here once it's ready."
            }
            ```

        * 400 (**Bad Request**)
            - appropirate error messages , if request is bad like ticket cancellation time is less than 2 hours 

        *  401 (**Unauthorized**)
                - returns this message if user does not have proper permission for this request

        *  403 (**Forbidden**)
            - returns this error if user is not authenticated  or missing some csrf token in the request header
            - sample error message 
            ```
            {
                "detail": "CSRF Failed: CSRF token from the 'X-Csrftoken' HTTP header incorrect."
            }
            ```
        * 500 (**Internal Server Error**)
            - returns internal server error message with proper exception handling data




* **/payments/:booking_ref**
    Allowed Methods: POST

    {{BASE_URL}}/payments/:booking_ref

    **POST**
    - Header Parameters
        - X-CSRFToken (**required**)
            - type: string
            - description: csrf token value returned after logging in                
            - example: 3CwkDICL51KCKCF3QbIflWlXvDiMN55S


    - Path Parameters
        * booking_ref (**required**)
            - type: string
            - Description: booking_ref returned on booking a flight
            - max length: 6
            - example: /bookings/DE56RH

    
    - Responses
        * 200 (**succesfull payment**)
            - on succesfull payment , booking status is changed to **CONFIRMED** and response is returned which contains pdf tickets url (separate for departing and returning , if different airline!) to be clicked to retreive pdfs , stripe sdk url (which needs to be validated by either making GET requests to it or pasting URL in browser)

            - Sample Response Object
            ```
            {
                "payemnt_intent_id": "pi_3O8ko0SBlwNpuxB20CYOI1XB",
                "ticket_pdf_url": "Your Ticket will be availalbe <a href='/v1/flight_api/download_pdf/ACB4C4/ticket/booking_ticket_ACB4C4.pdf'>here</a> once you have succesfully completed next_action of authenticating url !!",
                "next_action": "Click on the hook url with this response and ping GET endpoint for payment confirmation ",
                "url": {
                    "type": "use_stripe_sdk",
                    "use_stripe_sdk": {
                        "source": "src_1O8ko0SBlwNpuxB2irjv3blE",
                        "stripe_js": "https://hooks.stripe.com/redirect/authenticate/src_1O8ko0SBlwNpuxB2irjv3blE?client_secret=src_client_secret_3HjekD5R3RJb24LTmuDS0CiS&source_redirect_slug=test_YWNjdF8xTlRQWWhTQmx3TnB1eEIyLF9Pd2U2azFMS0Zlejd2UWpiTWlZMjhrNTk4OVU5WDFv0100ouAWuBpq",
                        "type": "three_d_secure_redirect"
                    }
                }
            }
            ```
        
        * 400 (**Bad Request**)
            - appropriate error message

        *  401 (**Unauthorized**)
                - returns this message if user does not have proper permission for this request

        *  403 (**Forbidden**)
            - returns this error if user is not authenticated  or missing some csrf token in the request header
            - sample error message 
            ```
            {
                "detail": "CSRF Failed: CSRF token from the 'X-Csrftoken' HTTP header incorrect."
            }
            ```
        * 500 (**Internal Server Error**)
            - returns internal server error message with proper exception handling data


        



                        



