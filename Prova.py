import streamlit as st
import requests

# API endpoint URL
API_URL = "https://daten.stadt.sg.ch/api/explore/v2.1/catalog/datasets/freie-parkplatze-in-der-stadt-stgallen-pls/records"

# Function to fetch parking data
def fetch_parking_data():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        return response.json().get("results", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch parking data: {e}")

# Function to calculate distance between two points using their coordinates
def calculate_distance(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1_rad, lon1_rad, lat2_rad, lon2_rad = map(
        lambda x: x * (3.141592653589793 / 180), [lat1, lon1, lat2, lon2]
    )

    # Haversine formula to calculate distance between two points on Earth's surface
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = (pow(dlat / 2, 2) + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * pow(dlon / 2, 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    earth_radius_km = 6371
    distance_km = earth_radius_km * c
    return distance_km

# Function to filter parking data within a radius of a given location
def filter_parking_data(location, radius_km):
    filtered_data = []
    for record in fetch_parking_data():
        park_location = record["standort"]
        distance = calculate_distance(location[0], location[1], park_location["lat"], park_location["lon"])
        if distance <= radius_km:
            record["distance_km"] = distance
            filtered_data.append(record)
    return filtered_data

# Streamlit web app
def main():
    st.title("Find Parking Spaces in St. Gallen")

    # Get user's location
    location_str = st.text_input("Enter your location (e.g., address, city)")
    location = None
    if location_str:
        st.write("Location entered:", location_str)
        location = geolocator.geocode(location_str)
        if location:
            st.success(f"Location found: ({location.latitude}, {location.longitude})")
        else:
            st.error("Location not found. Please enter a valid location.")

    if location:
        radius_km = st.slider("Select radius (km)", min_value=1, max_value=10, value=2)

        # Filter parking data within the specified radius
        parking_data = filter_parking_data((location.latitude, location.longitude), radius_km)

        if parking_data:
            st.success(f"Found {len(parking_data)} parking spaces within {radius_km} km")
            st.write("Showing Parking Spaces within Radius:")
            st.write(parking_data)
        else:
            st.warning("No parking spaces found within the specified radius.")

if __name__ == "__main__":
    main()
