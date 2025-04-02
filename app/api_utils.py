import requests
from flask import current_app
from datetime import datetime

def fetch_todays_readings():
    """Fetch today's liturgical calendar data and readings from Church Calendar and API.Bible."""
    # Fetch liturgical day from Church Calendar API
    today = datetime.now()
    year, month, day = today.year, today.month, today.day
    calendar_url = f"http://calapi.inadiutorium.cz/api/v0/en/calendars/general-en/{year}/{month}/{day}"
    
    try:
        calendar_response = requests.get(calendar_url, timeout=10)
        calendar_response.raise_for_status()
        calendar_data = calendar_response.json()

        # Extract liturgical day
        celebrations = calendar_data.get("celebrations", [{}])
        liturgical_day = celebrations[0].get("title", "Unknown Liturgical Day")

        # Extract readings references from the calendar API (if available)
        readings_references = calendar_data.get("readings", {})
        first_reading_ref = readings_references.get("first_reading", "N/A")
        second_reading_ref = readings_references.get("second_reading", "N/A")
        responsorial_psalm_ref = readings_references.get("responsorial_psalm", "N/A")
        gospel_ref = readings_references.get("gospel", "N/A")

    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Failed to fetch calendar data from {calendar_url}: {e}")
        return None

    # Step 2: Fetch readings content from API.Bible
    bible_api_base = "https://api.scripture.api.bible/v1/bibles"
    bible_id = "de4e12af7f28f599-02"  # NABRE (New American Bible Revised Edition) ID
    api_key = current_app.config.get('API_BIBLE_KEY')  
    headers = {"api-key": api_key}

    formatted_readings = {
        "date": today.strftime("%A, %B %d, %Y"),
        "liturgical_day": liturgical_day,
        "first_reading": {"reference": first_reading_ref, "content": "N/A"},
        "responsorial_psalm": {"reference": responsorial_psalm_ref, "content": "N/A"},
        "gospel": {"reference": gospel_ref, "content": "N/A"}
    }

    # Fetch each reading dynamically
    for reading_type, passage_ref in {
        "first_reading": first_reading_ref,
        "second_reading": second_reading_ref,
        "responsorial_psalm": responsorial_psalm_ref,
        "gospel": gospel_ref
    }.items():
        if passage_ref != "N/A":
            try:
                # Format the passage reference if needed
                formatted_ref = passage_ref.replace(" ", "").replace(":", ".")
                bible_url = f"{bible_api_base}/{bible_id}/passages/{formatted_ref}"
                current_app.logger.info(f"Fetching {reading_type} from {bible_url}")
                
                bible_response = requests.get(bible_url, headers=headers, timeout=10)
                bible_response.raise_for_status()
                bible_data = bible_response.json()
                content = bible_data["data"]["content"]
                formatted_readings[reading_type]["content"] = content
            except requests.exceptions.RequestException as e:
                current_app.logger.error(f"Failed to fetch {reading_type} from {bible_url}: {e}")
                # Keep "N/A" as fallback if a reading fails

    return formatted_readings