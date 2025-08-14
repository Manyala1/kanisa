import requests
from flask import current_app
from datetime import datetime

# Universalis: Fetch Catholic daily readings
def fetch_readings(date=None):
    """Fetch daily readings from Universalis API"""
    url = "https://universalis.app/api/daily-readings"
    params = {"date": date} if date else {}
    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        current_app.logger.error(f"Readings fetch error: {e}")
        return None

# CalAPI: Fetch liturgical calendar events
def fetch_liturgical_events(date=None):
    """Fetch feast/saint info from CalAPI (InAdiutorium)"""
    if not date:
        date = datetime.today().strftime("%Y/%m/%d")
    else:
        try:
            # Ensure format is YYYY/MM/DD for CalAPI
            date = datetime.strptime(date, "%Y-%m-%d").strftime("%Y/%m/%d")
        except ValueError:
            current_app.logger.error(f"Invalid date format for CalAPI: {date}")
            return None

    url = f"https://calapi.inadiutorium.cz/api/v0/en/calendars/default/{date}"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        current_app.logger.error(f"Liturgical events fetch error: {e}")
        return None
