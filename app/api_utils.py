import requests
from flask import current_app
from datetime import datetime, date
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
    """Fetch today's liturgical calendar data and display readings directly."""
    # Step 1: Fetch liturgical day from Church Calendar API
    today = datetime.now()
    year, month, day = today.year, today.month, today.day
    calendar_url = f"http://calapi.inadiutorium.cz/api/v0/en/calendars/general-en/{year}/{month}/{day}"
    
    try:
        current_app.logger.info(f"Fetching calendar data from {calendar_url}")
        calendar_response = requests.get(calendar_url, timeout=10)
        calendar_response.raise_for_status()
        calendar_data = calendar_response.json()

        # Log the raw calendar data for debugging
        current_app.logger.debug(f"Calendar API response: {calendar_data}")

        # Extract liturgical day
        celebrations = calendar_data.get("celebrations", [])
        if not celebrations:
            current_app.logger.warning("No celebrations found in calendar data.")
            liturgical_day = "Unknown Liturgical Day"
        else:
            liturgical_day = celebrations[0].get("title", "Unknown Liturgical Day")

        # Extract readings references
        readings_references = calendar_data.get("readings", {})
        first_reading = readings_references.get("first_reading", "No reference available")
        second_reading = readings_references.get("second_reading", "No reference available")
        responsorial_psalm = readings_references.get("responsorial_psalm", "No reference available")
        gospel = readings_references.get("gospel", "No reference available")

        # Log missing references for debugging
        if first_reading == "No reference available":
            current_app.logger.warning("First Reading is missing.")
        if second_reading == "No reference available":
            current_app.logger.warning("Second Reading is missing.")
        if responsorial_psalm == "No reference available":
            current_app.logger.warning("Responsorial Psalm is missing.")
        if gospel == "No reference available":
            current_app.logger.warning("Gospel is missing.")

    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Failed to fetch calendar data from {calendar_url}: {e}")
        return None
    except ValueError as e:
        current_app.logger.error(f"Failed to parse calendar API response: {e}")
        return None

    # Step 2: Format readings for display
    formatted_readings = {
        "date": today.strftime("%A, %B %d, %Y"),
        "liturgical_day": liturgical_day,
        "first_reading": first_reading,
        "second_reading": second_reading,
        "responsorial_psalm": responsorial_psalm,
        "gospel": gospel
    }

    # Log the final formatted readings for debugging
    current_app.logger.debug(f"Formatted readings: {formatted_readings}")

    return formatted_readings

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
        f"📖 First Reading:\n{readings['first_reading']}\n\n"
        f"📖 Second Reading:\n{readings['second_reading']}\n\n"
        f"🎵 Responsorial Psalm:\n{readings['responsorial_psalm']}\n\n"
        f"📖 Gospel:\n{readings['gospel']}"
    )
    return chat_message

# Step 3: Send SMS notification using Twilio
def send_sms_notification(to_phone_number, message_body):
    """
    Send an SMS notification using Twilio.
    """
    try:
        # Twilio credentials from the app configuration
        account_sid = current_app.config.get("")
        auth_token = current_app.config.get("")
        from_phone_number = current_app.config.get("")

        if not all([account_sid, auth_token, from_phone_number]):
            current_app.logger.error("")
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
        f"📖 First Reading: {readings['first_reading']}\n"
        f"📖 Second Reading: {readings['second_reading']}\n"
        f"🎵 Responsorial Psalm: {readings['responsorial_psalm']}\n"
        f"📖 Gospel: {readings['gospel']}"
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