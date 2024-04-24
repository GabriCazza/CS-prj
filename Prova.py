import streamlit as st
import requests
import folium

# Define the API endpoint URL
API_URL = "https://daten.stadt.sg.ch/api/explore/v2.1/catalog/datasets/freie-parkplatze-in-der-stadt-stgallen-pls/records"

def fetch_parking_data():
    try:
        # Make a GET request to the API endpoint
        response = requests.get(API_URL)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the JSON response
        data = response.json()
        return data.get("records", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch parking data: {e}")

def main():
    # Set page title
    st.title("St. Gallen Parking Spaces")

    # Fetch parking data
    parking_data = fetch_parking_data()

    # Display parking data in a table
    if parking_data:
        st.write("Available Parking Spaces:")
        st.write(parking_data)
    else:
        st.write("No parking data available.")

    # Create map
    st.write("Map with Parking Spots")
    m = folium.Map(location=[47.4239, 9.3747], zoom_start=15)

    # Add markers for parking spots
    for spot in parking_data:
        lat = spot["standort"]["lat"]
        lon = spot["standort"]["lon"]
        name = spot["phname"]
        folium.Marker([lat, lon], popup=name).add_to(m)

    # Display map
    st.write(m)

    # Input radius
    radius = st.slider("Select Radius (meters)", min_value=100, max_value=2000, step=100)

    # Input destination address
    destination = st.text_input("Enter Destination Address")

    # Display radius and destination
    st.write(f"Selected Radius: {radius} meters")
    st.write(f"Destination Address: {destination}")

if __name__ == "__main__":
    main()
