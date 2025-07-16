from mcp.server.fastmcp import FastMCP
from geopy.geocoders import Nominatim
import requests
import re

mcp = FastMCP("Weather App")


@mcp.tool()
def open_weather_app(query):
    """
    Get information about the current weather in a specified location.
    """
    query = extract_location(query)
    lat, lon = get_lat_lon(query)
    return (f"Weather: {get_weather(lat, lon)}")


weathercode_desc = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Rime fog", 51: "Light drizzle", 61: "Light rain",
    71: "Light snow", 80: "Rain showers", 95: "Thunderstorm"
}


def get_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    try:
        r = requests.get(url, timeout=5)
        data = r.json()["current_weather"]
        units = r.json()["current_weather_units"]
        temp_c = str(data["temperature"]) + " " + units["temperature"]
        windspeed = str(data["windspeed"]) + " " + units["windspeed"]
        weather_desc = weathercode_desc.get(data["weathercode"], f"Code {data['weathercode']}")

        return {
            "temperature": temp_c,
            "windspeed": windspeed,
            "weathercode": weather_desc
        }
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return {"temperature": "N/A", "windspeed": "N/A", "weathercode": "N/A"}


def get_lat_lon(location_name):
    geolocator = Nominatim(user_agent="geoapi")
    location = geolocator.geocode(location_name)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None


def extract_location(query: str) -> str:
    # Normalize the query
    query = query.lower().strip()

    # Common patterns
    patterns = [
        r"weather\s+(in|at|for|about)?\s*(.+)",  # e.g. "weather in new york"
        r"what(?:'s| is)? the weather (in|at|for|about)?\s*(.+)",  # "what is the weather in new york"
        r"how is the weather (in|at|for|about)?\s*(.+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, query)
        if match:
            location = match.group(2)
            return location.strip(" ?.,").title()

    match = re.match(r"(.*?)(?:\s+weather)?$", query)
    if match:
        location = match.group(1)
        return location.strip().title()
    # fallback
    return query.title()  # Try returning the whole thing capitalized
