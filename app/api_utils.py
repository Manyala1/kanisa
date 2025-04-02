import requests
from flask import current_app

def fetch_daily_readings():
    """Fetch daily readings from the Church Calendar API."""
    api_url = current_app.config.get("CHURCH_CALENDAR_API_URL")  # Use the Church Calendar API URL
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
        data = response.json()  # Parse the JSON response

        # Log the response for debugging
        current_app.logger.info(f"Daily readings API response: {data}")

        # Check if the response contains readings
        if isinstance(data, dict) and "readings" in data:
            readings = data["readings"]
            if isinstance(readings, list) and readings:
                return readings  # Return the readings list
            else:
                current_app.logger.warning("Readings list is empty or invalid.")
        else:
            current_app.logger.warning("Unexpected API response format.")
        return []  # Return an empty list if readings are not found
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Failed to fetch daily readings: {e}")
        return []  # Return an empty list if the API call fails
