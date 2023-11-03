## API Docs

BASE_URL := **https://flight-booking-rest-api-355b8ab4795a.herokuapp.com/v1/flight_api/**

endpoints := 
* /login
    - allowed methods = POST

    * POST
        - {{BASE-URL}}/login
        - body parameters 
            * username (**required**) 
                - type: string
                - description: usernameid of the user
            * password (**required**)
                - type: string
                - description: password 
        - responses
            * 200 (**succesfully logged in**)
                - returns csrfToken and sessionId which needs to passed with every endpoint
            * 400 (**Bad Request**)
                - returns appropriate field error message 
            * 500 (**Some error from app side**)
                - returns the raised exception message

* /register 