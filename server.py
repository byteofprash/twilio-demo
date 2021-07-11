import uuid

from flask import Flask, request, jsonify, url_for, Response, redirect
from flask_cors import CORS
from twilio.rest import Client
from twilio.twiml.voice_response import Gather, VoiceResponse
from twilio.twiml.messaging_response import Message, MessagingResponse

from config import MY_NUMBER, TWILIO_NUMBER, DRIVER_NUMBER, SERVICE_SID, ACCOUNT_SID, AUTH_TOKEN

PUBLIC_URL = "https://d7a22cf0d722.ngrok.io"

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
                                                       identifier=MY_NUMBER,
                                                       proxy_identifier=TWILIO_NUMBER)
    return jsonify({"session": session.sid})


@app.route('/taxi', methods=['delete'])
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

    incoming_msg = request.values.get('Body', '').lower()
    waid = "+" + request.values.get('WaId', '').lower()
    for sess in my_service.sessions.list():
        for participant in sess.participants.list():
            print("Participant is:", participant.identifier, " with session", participant.session_sid)
            if participant.identifier == waid:
                if "where" in incoming_msg:
                    msg.body("The driver is on his way. \nETA: 15 minutes. What else would you like to know")
                elif "payment" in incoming_msg:
                    msg.body("Your current payment option is selected as Mastercard number: XXXXX1234. Please call us to change your payment method")
                else:
                    msg.body("You have an open ride with M-AB 1234. What would you like to do?")

    print(incoming_msg, waid)
    return str(resp)


@app.route('/call', methods=['POST'])
def call():
    # Get the digit pressed by the user
    print("Intercepted the call",request.values)
    # session_sid = data.get('sessionSid')
    # if session_sid:
    #     my_service.sessions(sid=session_sid).delete()
    #     return jsonify({"session_deleted":session_sid})
    # else:
    #     return jsonify({"session_deleted":"No session found"})


@app.route('/non_session_call', methods=['POST'])
def non_session_call():
    # Get the digit pressed by the user
    print("Out of session the call",request.values)


@app.route('/ivr/welcome', methods=['POST'])
def welcome():
    response = VoiceResponse()
    with response.gather(num_digits=1, action=PUBLIC_URL + '/ivr/menu', method="POST") as g:
        g.say(message="Thanks for calling the OWL taxis. " +
              "Please press 1 new bookings." +
              "Press 2 to speak to your current ride driver.", loop=1)
    return twiml(response)


@app.route('/ivr/menu', methods=['POST'])
def menu():
    selected_option = request.form['Digits']
    print("Selected option is", selected_option)
    option_actions = {'1': _give_instructions,
                      '2': _call_driver}
    if selected_option == '2':
        return redirect(PUBLIC_URL + '/ivr/call_driver')
    # if selected_option in option_actions.keys():
    #     # option_actions[selected_option](response)
    #     return twiml(response)

    return _redirect_welcome()


@app.route('/ivr/planets', methods=['POST'])
def planets():
    selected_option = request.form['Digits']
    option_actions = {'2': "+12024173378",
                      '3': "+12027336386",
                      "4": "+12027336637"}

    if selected_option in option_actions:
        response = VoiceResponse()
        response.dial(option_actions[selected_option])
        return twiml(response)

    return _redirect_welcome()


# private methods

def _give_instructions(response):
    response.say("To get to your extraction point, get on your bike and go " +
                 "down the street. Then Left down an alley. Avoid the police" +
                 " cars. Turn left into an unfinished housing development." +
                 "Fly over the roadblock. Go past the moon. Soon after " +
                 "you will see your mother ship.",
                 voice="alice", language="en-GB")

    response.say("Thank you for calling the E T Phone Home Service - the " +
                 "adventurous alien's first choice in intergalactic travel")

    response.hangup()
    return response


def _list_planets(response):
    with response.gather(
        numDigits=1, action=PUBLIC_URL +'planets', method="POST"
    ) as g:
        g.say("To call the planet Broh doe As O G, press 2. To call the " +
              "planet DuhGo bah, press 3. To call an oober asteroid " +
              "to your location, press 4. To go back to the main menu " +
              " press the star key.",
              voice="alice", language="en-GB", loop=3)

    return response

@app.route('/ivr/call_driver', methods=['GET','POST'])
def _call_driver():
    print("Calling driver")
    response = VoiceResponse()
    response.dial(DRIVER_NUMBER)
    return twiml(response)


def _redirect_welcome():
    response = VoiceResponse()
    response.say("Returning to the main menu", voice="alice", language="en-GB")
    response.redirect(url_for('welcome'))

    return twiml(response)

if __name__ == '__main__':
    app.run()
