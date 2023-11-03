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
    Allowed Methods :- POST, PUT

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
            * 200 (**succesfully registered**)
                - returns info of newly registered user

            sample response body: 
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

* 