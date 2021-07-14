import uuid
import json

from flask import Flask, request, jsonify, url_for, Response, redirect
from flask_cors import CORS
from twilio.rest import Client
from twilio.twiml.voice_response import Gather, VoiceResponse, Say
from twilio.twiml.messaging_response import Message, MessagingResponse

from config import CUSTOMER_NUMBER, TWILIO_SANDBOX, TWILIO_NUMBER, DRIVER_NUMBER, SERVICE_SID, ACCOUNT_SID, AUTH_TOKEN

PUBLIC_URL = "Put-an easy to use public ip to access your service from twilio"

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

client = Client(ACCOUNT_SID, AUTH_TOKEN)
my_service = client.proxy.services(sid=SERVICE_SID).fetch()


def twiml(resp):
    resp = Response(str(resp))
    resp.headers['Content-Type'] = 'text/xml'
    return resp

@app.route('/taxi', methods=['POST'])
def taxi():
    args = dict(request.values)
    name = args["name"] if 'name' in args else ""
    open_sessions = my_service.sessions.list()
    for sess in open_sessions:
        print(sess.__dict__)
        sess.delete()
    session = my_service.sessions.create(unique_name=uuid.uuid4().hex)
    participant_driver = session.participants.create(friendly_name="Driver",
                                                     identifier=DRIVER_NUMBER,
                                                     proxy_identifier=TWILIO_NUMBER,
                                                     fail_on_participant_conflict=False)

    participant_customer = session.participants.create(friendly_name="Customer",
                                                       identifier=CUSTOMER_NUMBER,
                                                       proxy_identifier=TWILIO_NUMBER)
    data = {}
    with open("data.json", 'r') as w:
        data = json.load(w)
        data[session.sid] = [name, DRIVER_NUMBER, TWILIO_NUMBER]
    with open("data.json", 'w') as w:
        json.dump(data, w)

    return jsonify({"session": session.sid})


@app.route('/taxi', methods=['DELETE'])
def closeTaxi():
    # Get the digit pressed by the user
    data = dict(request.json)
    session_sid = data.get('sessionSid')
    if session_sid:
        my_service.sessions(sid=session_sid).delete()
        return jsonify({"session_deleted":session_sid})
    else:
        return jsonify({"session_deleted":"No session found"})


@app.route('/whatsappBot', methods=['POST'])
def whatsappBot():
    resp = MessagingResponse()
    msg = resp.message()

    found_session = False

    incoming_msg = request.values.get('Body', '').lower()
    waid = "+" + request.values.get('WaId', '').lower()
    for sess in my_service.sessions.list():
        for participant in sess.participants.list():
            print("Participant is:", participant.identifier, " with session", participant.session_sid)
            if participant.identifier == waid:
                if "where" in incoming_msg:
                    msg.body("The driver is on his way. \nETA: 7 minutes. Would be parked at B122 in the parkplatz. What else would you like to know")
                    found_session = True
                elif "payment" in incoming_msg:
                    msg.body("Your current payment option is selected as Mastercard number: XXXXX1234. Please call us to change your payment method")
                    found_session = True
                else:
                    msg.body("You have an open ride with M-AB 1234. What would you like to do?")
                    found_session = True
    if not found_session:
        msg.body("No sessions open with your name. Please call ")

    print(incoming_msg, waid)
    return str(resp)


@app.route('/non_session_call', methods=['POST'])
def non_session_call():
    print("Out of session the call",request.values)


@app.route('/whatsappUpdate', methods=['POST'])
def send_whatsapp_msg():
    message = client.messages.create(
                                  from_=f'whatsapp:{TWILIO_SANDBOX}',
                                  body='Your appointment is coming up on July 21 at 3PM',
                                  to=f'whatsapp:{CUSTOMER_NUMBER}'
                              )
    return jsonify({"message": message.sid})


@app.route('/smsUpdate', methods=['POST'])
def send_sms_msg():
    message = client.messages.create(
                                  from_=f'{TWILIO_NUMBER}',
                                  body='Hi Hans, your appointment is coming up on July 25 at 11AM',
                                  to=f'{CUSTOMER_NUMBER}'
                              )
    print(message.sid)
    return jsonify({"message": message.sid})


if __name__ == '__main__':
    app.run()
