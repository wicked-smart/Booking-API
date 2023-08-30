from flask import Flask, jsonify, request
import os
import requests
import stripe
from dotenv import load_dotenv 
from pathlib import Path

import json 

app = Flask(__name__)

BASE_DIR  = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / 'booking_api/.env')

# load all the secrets from .env
stripe.api_key = os.environ.get('STRIPE_TEST_API_KEY')
endpoint_secret = "whsec_KhG1qA8cTG9kdNYZjaj7nr0IVUuC0xFy"

print("endpoint secret := ", endpoint_secret)


@app.route('/')
def hello_world():
    return '<pre>Testing 1..2..3..!!!'

@app.route('/webhook', methods=['POST'])
def webhook():

    print("webhook endpoint reached")

    event = None
    payload = request.data

    print("payload := ", payload)

    try:
        event = json.loads(payload)
        #print('Received event:', event)
    except:
        print('⚠️  Webhook error while parsing basic request.' + str(e))
        return jsonify(success=False)
    

    
    if endpoint_secret:
        # Only verify the event if there is an endpoint secret defined
        # Otherwise use the basic event deserialized with json
        sig_header = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except stripe.error.SignatureVerificationError as e:
            print('⚠️  Webhook signature verification failed.' + str(e))
            return jsonify(success=False)

    
    
    # Handle the event
    if event and event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']  # contains a stripe.PaymentIntent
        print('Payment for {} succeeded'.format(payment_intent['amount']))


        # Then define and call a method to handle the successful payment intent.
        # handle_payment_intent_succeeded(payment_intent)

        
        if "metadata" in payment_intent:

            #print(payment_intent["metadata"])
            booking_ref = payment_intent["metadata"].get('booking_ref')
        
            data = {
                "booking_ref": booking_ref,
                "payment_id": payment_intent["id"],
                "payment_status": payment_intent["status"],
                "webhook_secret": os.environ.get('WEBHOOK_SECRET'),
                "event": "payment"
            }

            url  = "http://127.0.0.1:8000/v1/flight_api/update_booking"

            response = requests.post(url, json=data)

            print("response := ", response.content)

            if response.status_code == 200:
                return jsonify("Booking updated successfully"), 200
            else:
                return jsonify("Failed to update booking"), 500
            
        else:
            print('⚠️  Metadata attribute not found in payment_intent object')
            return jsonify(success=False)
        
    elif event['type'] == 'payment_method.attached':
        payment_method = event['data']['object']  # contains a stripe.PaymentMethod
        # Then define and call a method to handle the successful attachment of a PaymentMethod.
        # handle_payment_method_attached(payment_method)
        print("Event payment_method.attached succeeded....")
    
    elif event['type'] == 'charge.refunded':
        refund_object = event['data']['object']  # contains a stripe.PaymentMethod
        # Then define and call a method to handle the successful attachment of a PaymentMethod.
        # handle_payment_method_attached(payment_method)
        print("Event charge.refund succeeded....")
        

        if "metadata" in refund_object:

            print(refund_object["metadata"])
            booking_ref = refund_object["metadata"].get('booking_ref')
            receipt_url = refund_object["receipt_url"]
            print("reciept url := ", refund_object["receipt_url"])
        
            data = {
                "booking_ref": booking_ref,
                "refund_status": "CREATED",
                "webhook_secret": os.environ.get('WEBHOOK_SECRET'),
                "receipt_url": receipt_url,
                "event": "refund"
            }

            url  = "http://127.0.0.1:8000/v1/flight_api/update_booking"

            response = requests.post(url, json=data)

            if response.status_code == 200:
                return jsonify("Refund Created  successfully"), 200
            else:
                return jsonify("Failed to create refund!!"), 500
            
        else:
            print('⚠️  Refund metadata attribute not found in payment_intent object')
            return jsonify(success=False)



    else:
        # Unexpected event type
        print('Unhandled event type {}'.format(event['type']))

    
    return jsonify(success=True)


if __name__ == '__main__':
    app.run(debug=True)