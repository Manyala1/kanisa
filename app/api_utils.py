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
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    
def send_sms_notification(to_phone_number, message):
    """Send SMS using Twilio client."""
    try:
        client = Client(
            current_app.config.get('TWILIO_ACCOUNT_SID'),
            current_app.config.get('TWILIO_AUTH_TOKEN')
        )
        
        message = client.messages.create(
            body=message,
            from_=current_app.config.get('TWILIO_PHONE_NUMBER'),
            to=to_phone_number
        )
        current_app.logger.info(f"SMS sent successfully. SID: {message.sid}")
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send SMS: {str(e)}")
        return False

def fetch_todays_readings():
    """Fetch today's Catholic Mass readings from Universalis API."""
    try:
        api_url = f"{current_app.config['UNIVERSALIS_API_URL']}/readings"
        params = {'apikey': current_app.config['UNIVERSALIS_API_KEY']}
        
        current_app.logger.info("Fetching readings from Universalis API")
        
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Format the readings data
        formatted_readings = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'liturgical_info': {
                'season': data.get('season', ''),
                'celebration': data.get('celebration', '')
            },
            'readings': {
                'first_reading': _extract_reading(data.get('first_reading', {})),
                'responsorial_psalm': _extract_reading(data.get('psalm', {})),
                'second_reading': _extract_reading(data.get('second_reading', {})),
                'gospel': _extract_reading(data.get('gospel', {}))
            }
        }
        
        current_app.logger.debug(f"Formatted readings: {formatted_readings}")
        return formatted_readings

    except requests.ConnectionError:
        current_app.logger.error("Failed to connect to Universalis API")
        return None
    except Exception as e:
        current_app.logger.error(f"Error fetching readings: {str(e)}")
        return None

def _extract_reading(reading_data):
    """Helper function to extract reading content from Universalis API response."""
    if not reading_data:
        return {
            'reference': '',
            'content': [],
            'response': ''
        }
    
    return {
        'reference': reading_data.get('reference', ''),
        'content': reading_data.get('text', '').split('\n'),
        'response': reading_data.get('response', '')
    }

def fetch_todays_events():
    """Fetch today's church events."""
    try:
        events = Event.query.filter_by(date=date.today()).all()
        return [{'time': event.time, 'title': event.title} for event in events]
    except Exception as e:
        current_app.logger.error(f"Error fetching events: {str(e)}")
        return None

def get_readings_for_chat():
    """Format today's readings for chat display."""
    readings = fetch_todays_readings()
    if not readings:
        return "Sorry, I couldn't fetch today's readings. Please try again later."

    chat_message = (
        f"📅 Date: {readings['date']}\n"
        f"🙏 Liturgical Day: {readings['liturgical_info']['celebration']}\n\n"
        f"📖 First Reading ({readings['readings']['first_reading']['reference']}):\n"
        f"{' '.join(readings['readings']['first_reading']['content'])}\n\n"
        f"📖 Second Reading ({readings['readings']['second_reading']['reference']}):\n"
        f"{' '.join(readings['readings']['second_reading']['content'])}\n\n"
        f"🎵 Responsorial Psalm ({readings['readings']['responsorial_psalm']['reference']}):\n"
        f"{' '.join(readings['readings']['responsorial_psalm']['content'])}\n\n"
        f"📖 Gospel ({readings['readings']['gospel']['reference']}):\n"
        f"{' '.join(readings['readings']['gospel']['content'])}"
    )
    return chat_message

def send_digichurch_notification(to_phone_number, notification_type='all'):
    """Send DigiChurch notifications via SMS."""
    try:
        message_parts = []
        
        if notification_type in ['readings', 'all']:
            readings = fetch_todays_readings()
            if readings:
                message_parts.append(
                    f"📖 TODAY'S READINGS - {readings['date']}\n"
                    f"🙏 {readings['liturgical_info']['celebration']}\n\n"
                    f"First Reading: {readings['readings']['first_reading']['reference']}\n"
                    f"Second Reading: {readings['readings']['second_reading']['reference']}\n"
                    f"Psalm: {readings['readings']['responsorial_psalm']['reference']}\n"
                    f"Gospel: {readings['readings']['gospel']['reference']}"
                )
        
        if notification_type in ['events', 'all']:
            events = fetch_todays_events()
            if events:
                events_text = "\n\n📅 TODAY'S EVENTS:"
                for event in events:
                    events_text += f"\n⏰ {event['time']} - {event['title']}"
                message_parts.append(events_text)
        
        if not message_parts:
            current_app.logger.warning("No content available for notification")
            return False
            
        full_message = "\n---\n".join(message_parts)
        full_message += "\n\nSent via DigiChurch ✝️"
        
        return send_sms_notification(to_phone_number, full_message)
        
    except Exception as e:
        current_app.logger.error(f"Failed to send notification: {str(e)}")
        return False