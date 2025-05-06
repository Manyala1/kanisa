import requests
from datetime import datetime, date
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from twilio.rest import Client

db = SQLAlchemy()

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)


def fetch_todays_readings():
    """
    Fetch today's Catholic Mass readings from the Catholic Mass Readings API.
    """
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        API_URL = "http://localhost:8000/api/readings"  # Updated port to 8000

        # Log API request attempt
        current_app.logger.info(f"Fetching readings from API for {today}")

        # Add timeout to prevent hanging
        response = requests.get(f"{API_URL}/{today}", timeout=5)
        response.raise_for_status()
        
        # Log raw response for debugging
        current_app.logger.debug(f"API Response Status: {response.status_code}")
        current_app.logger.debug(f"API Response: {response.text[:500]}...")  # Log first 500 chars
        
        readings_data = response.json()

        # Format readings data
        formatted_readings = {
            'date': today,
            'liturgical_day': readings_data.get('liturgical_info', {}).get('season', 'Unknown Season'),
            'first_reading': {
                'reference': readings_data.get('readings', [{}])[0].get('source', 'No reference available'),
                'content': "\n".join(readings_data.get('readings', [{}])[0].get('content', ['Reading not available']))
            },
            'second_reading': {
                'reference': readings_data.get('readings', [{}])[1].get('source', 'No reference available'),
                'content': "\n".join(readings_data.get('readings', [{}])[1].get('content', ['Reading not available']))
            },
            'responsorial_psalm': {
                'reference': readings_data.get('readings', [{}])[2].get('source', 'No reference available'),
                'content': "\n".join(readings_data.get('readings', [{}])[2].get('content', ['Psalm not available']))
            },
            'gospel': {
                'reference': readings_data.get('readings', [{}])[3].get('source', 'No reference available'),
                'content': "\n".join(readings_data.get('readings', [{}])[3].get('content', ['Gospel not available']))
            }
        }

        current_app.logger.debug(f"Formatted readings: {formatted_readings}")
        return formatted_readings

    except requests.ConnectionError:
        current_app.logger.error("Failed to connect to Mass Readings API. Is it running?")
        return None
    except requests.Timeout:
        current_app.logger.error("API request timed out")
        return None
    except requests.RequestException as e:
        current_app.logger.error(f"API Request failed: {str(e)}")
        return None
    except Exception as e:
        current_app.logger.error(f"Unexpected error: {str(e)}")
        return None

def get_readings_for_chat():
    """
    Fetch and format today's readings for chat display.
    """
    readings = fetch_todays_readings()
    if not readings:
        return "Sorry, I couldn't fetch today's readings. Please try again later."

    chat_message = (
        f"📅 Date: {readings['date']}\n"
        f"🙏 Liturgical Day: {readings['liturgical_day']}\n\n"
        f"📖 First Reading ({readings['first_reading']['reference']}):\n{readings['first_reading']['content']}\n\n"
        f"📖 Second Reading ({readings['second_reading']['reference']}):\n{readings['second_reading']['content']}\n\n"
        f"🎵 Responsorial Psalm ({readings['responsorial_psalm']['reference']}):\n{readings['responsorial_psalm']['content']}\n\n"
        f"📖 Gospel ({readings['gospel']['reference']}):\n{readings['gospel']['content']}"
    )
    return chat_message

def send_sms_notification(to_phone_number, message_body):
    """
    Send an SMS notification using Twilio.
    """
    try:
        # Twilio credentials from the app configuration
        account_sid = current_app.config.get("TWILIO_ACCOUNT_SID")
        auth_token = current_app.config.get("TWILIO_AUTH_TOKEN")
        from_phone_number = current_app.config.get("TWILIO_PHONE_NUMBER")

        if not all([account_sid, auth_token, from_phone_number]):
            current_app.logger.error("Missing Twilio configuration")
            return False

        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=message_body,
            from_=from_phone_number,
            to=to_phone_number
        )
        current_app.logger.info(f"SMS sent successfully to {to_phone_number}: {message.sid}")
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send SMS to {to_phone_number}: {e}")
        return False

def notify_readings_via_sms(to_phone_number):
    """
    Fetch today's readings and send them via SMS.
    """
    readings = fetch_todays_readings()
    if not readings:
        current_app.logger.error("Failed to fetch readings for SMS notification.")
        return False

    message_body = (
        f"📅 {readings['date']}\n"
        f"🙏 {readings['liturgical_day']}\n\n"
        f"📖 First Reading ({readings['first_reading']['reference']}): {readings['first_reading']['content']}\n"
        f"📖 Second Reading ({readings['second_reading']['reference']}): {readings['second_reading']['content']}\n"
        f"🎵 Responsorial Psalm ({readings['responsorial_psalm']['reference']}): {readings['responsorial_psalm']['content']}\n"
        f"📖 Gospel ({readings['gospel']['reference']}): {readings['gospel']['content']}"
    )
    return send_sms_notification(to_phone_number, message_body)

def fetch_todays_events():
    """
    Fetch today's events from the database.
    """
    try:
        today = date.today()
        events = Event.query.filter_by(date=today).all()
        if not events:
            current_app.logger.info("No events found for today.")
            return []

        formatted_events = [{"time": event.time, "title": event.title} for event in events]
        current_app.logger.debug(f"Fetched events: {formatted_events}")
        return formatted_events
    except Exception as e:
        current_app.logger.error(f"Failed to fetch events from the database: {e}")
        return []

def notify_events_via_sms(to_phone_number):
    """
    Fetch today's events and send them via SMS.
    """
    events = fetch_todays_events()
    if not events:
        current_app.logger.error("No events found for SMS notification.")
        return False

    # Format the events into a message body
    message_body = "📅 Today's Events:\n"
    for event in events:
        message_body += f"⏰ {event['time']} - {event['title']}\n"

    return send_sms_notification(to_phone_number, message_body)
