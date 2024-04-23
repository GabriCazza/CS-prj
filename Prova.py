import streamlit as st
import requests

# Define the API endpoint URL
API_URL = "https://daten.stadt.sg.ch/api/explore/v2.1/catalog/datasets/freie-parkplatze-in-der-stadt-stgallen-pls/records"

def fetch_parking_data(limit=20):
    try:
        # Make a GET request to the API endpoint
        response = requests.get(API_URL, params={"limit": limit})
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

if __name__ == "__main__":
    main()
