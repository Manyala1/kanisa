import requests
from flask import current_app
from datetime import datetime

def fetch_todays_readings():
    """Fetch today's readings from the Universalis API."""
    api_url = current_app.config['UNIVERSALIS_API_URL']
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
        data = response.json()

        # Format the readings
        formatted_readings = {
            "date": datetime.now().strftime("%A, %B %d, %Y"),
            "liturgical_day": data.get("liturgical_day", "Unknown Liturgical Day"),
            "first_reading": {
                "reference": data.get("first_reading", {}).get("reference", "N/A"),
                "content": data.get("first_reading", {}).get("content", "N/A"),
            },
            "responsorial_psalm": {
                "reference": data.get("responsorial_psalm", {}).get("reference", "N/A"),
                "content": data.get("responsorial_psalm", {}).get("content", "N/A"),
            },
            "gospel": {
                "reference": data.get("gospel", {}).get("reference", "N/A"),
                "content": data.get("gospel", {}).get("content", "N/A"),
            },
        }
        return formatted_readings
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Failed to fetch today's readings: {e}")
        return None  # Return None if the API call fails