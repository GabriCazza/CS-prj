import streamlit as st
import requests
import json
import folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

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

# Function to filter parking data within a radius of a given location
def filter_parking_data(location, radius_km):
    filtered_data = []
    for record in fetch_parking_data():
        park_location = (record["standort"]["lat"], record["standort"]["lon"])
        distance = geodesic(location, park_location).kilometers
        if distance <= radius_km:
            record["distance_km"] = distance
            filtered_data.append(record)
    return filtered_data

# Function to display parking data on a map
def display_parking_map(location, parking_data):
    map = folium.Map(location=location, zoom_start=15)
    folium.Marker(location, popup="Your Location", icon=folium.Icon(color='green')).add_to(map)
    for record in parking_data:
        park_location = (record["standort"]["lat"], record["standort"]["lon"])
        folium.Marker(park_location, popup=f"{record['phname']} - {record['distance_km']:.2f} km").add_to(map)
    return map

# Streamlit web app
def main():
    st.title("Find Parking Spaces in St. Gallen")

    # Get user's location
    location_str = st.text_input("Enter your location (e.g., address, city)")
    geolocator = Nominatim(user_agent="parking_locator")
    location = geolocator.geocode(location_str)

    if location:
        st.success(f"Location found: ({location.latitude}, {location.longitude})")
        radius_km = st.slider("Select radius (km)", min_value=1, max_value=10, value=2)

        # Filter parking data within the specified radius
        parking_data = filter_parking_data((location.latitude, location.longitude), radius_km)

        if parking_data:
            st.success(f"Found {len(parking_data)} parking spaces within {radius_km} km")
            st.write("Showing Parking Spaces within Radius:")
            st.write(parking_data)

            # Display parking locations on a map
            st.subheader("Map of Parking Spaces")
            parking_map = display_parking_map((location.latitude, location.longitude), parking_data)
            folium_static(parking_map)
        else:
            st.warning("No parking spaces found within the specified radius.")
    elif location_str:
        st.error("Location not found. Please enter a valid location.")

if __name__ == "__main__":
    main()

