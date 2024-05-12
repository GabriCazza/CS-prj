import streamlit as st
from geopy.geocoders import Nominatim
import pandas as pd
import folium
from streamlit_folium import folium_static
import requests
from geopy.distance import geodesic
from datetime import datetime
import time
import threading
from geopy.exc import GeocoderRateLimited
import random
import re



def safe_request(url, params):
    """Make a request with exponential backoff."""
    attempts = 0
    max_attempts = 5
    backoff_factor = 1.5
    while attempts < max_attempts:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response
        elif response.status_code == 429:
            sleep_time = (backoff_factor ** attempts) + random.uniform(0, 1)
            time.sleep(sleep_time)
            attempts += 1
        else:
            break
    return None  # Return None if all attempts fail

def fetch_additional_data():
    base_url = "https://daten.stadt.sg.ch/api/explore/v2.1/catalog/datasets/points-of-interest-/records"
    params = {
        "refine": 'kategorie:"Parkplätze, Parkhäuser"',
        "limit": 100,
        "offset": 0
    }
    parking_data = []

    while True:
        response = safe_request(base_url, params)
        if response and response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            if not results:
                break

            for item in results:
                geo_point = item.get('geo_point_2d', {})
                parking_data.append({
                    'latitude': geo_point.get('lat', 0),  # Default to 0 if no latitude
                    'longitude': geo_point.get('lon', 0),  # Default to 0 if no longitude
                    'name': item.get('name', 'No Name Provided'),
                    'description': item.get('description', 'No Description Provided'),
                    'address': item.get('adresse', 'No Address Provided'),
                    'info': item.get('informatio', 'No Information Provided')  # Additional info
                })
            params['offset'] += params['limit']
        else:
            st.error("Failed to fetch additional data after multiple attempts.")
            break

    return pd.DataFrame(parking_data)  # Assicurati di restituire sempre un DataFrame

def fetch_parking_data():
    """Fetch parking data from an API."""
    API_ENDPOINT = "https://daten.stadt.sg.ch/api/explore/v2.1/catalog/datasets/freie-parkplatze-in-der-stadt-stgallen-pls/records?limit=20"
    response = requests.get(API_ENDPOINT)
    if response.status_code == 200:
        data = response.json()['results']
        if data:
            parking_data = pd.DataFrame(data)
            parking_data['latitude'] = parking_data['standort'].apply(lambda x: x.get('lat'))
            parking_data['longitude'] = parking_data['standort'].apply(lambda x: x.get('lon'))
            parking_data['category'] = parking_data.apply(lambda x: 'Parkhaus' if x['phstate'] == 'offen' else 'Closed', axis=1)
            return parking_data
        else:
            st.error("No data available from the API.")
            return pd.DataFrame()
    else:
        st.error(f'Failed to retrieve data: HTTP Status Code {response.status_code}')
        return pd.DataFrame()



def geocode_address(location):
    """Converts an address to a point (latitude, longitude) using Nominatim API."""
    if location:
        geolocator = Nominatim(user_agent="geocoding_app", timeout=10)  # Aumento del timeout a 10 secondi
        try:
            geocoded_location = geolocator.geocode(location + ", St. Gallen, Switzerland")
            if geocoded_location:
                return (geocoded_location.longitude, geocoded_location.latitude)
        except GeocoderRateLimited as e:
            st.warning("Rate limit exceeded, waiting to retry...")
            time.sleep(10)  # wait 10 seconds before retrying
        except Exception as e:
            st.error(f"Geocoding error: {e}")
    return None


def add_markers_to_map(map_folium, original_data, additional_data, location_point, destination_point, radius, show_parkhaus, show_extended_blue, show_white, show_handicapped, address):
    address_provided = bool(address)
    filtered_original_data = filter_parking_by_radius(original_data, destination_point, radius, show_parkhaus, address_provided)
    filtered_additional_data = filter_parking_by_radius(additional_data, destination_point, radius, False, address_provided)

    if show_parkhaus:
        for _, row in filtered_original_data.iterrows():
            if row.get('category', '') == 'Parkhaus':
                add_marker(map_folium, row, "🅿️", destination_point)  # Pass destination point for Parkhaus markers

    # Adding other types of markers
    if show_extended_blue:
        for _, row in filtered_additional_data.iterrows():
            if "erweiterte blaue zone" in row.get('info', '').lower():
                add_marker(map_folium, row, "🔵", None)

    if show_white:
        for _, row in filtered_additional_data.iterrows():
            if "weiss (bewirtschaftet)" in row.get('info', '').lower() or "weisse zone" in row.get('info', '').lower():
                add_marker(map_folium, row, "⚪", None)

    if show_handicapped:
        for _, row in filtered_additional_data.iterrows():
            if "invalidenparkplatz" in row.get('info', '').lower():
                add_marker(map_folium, row, "♿", None)

    add_user_markers(map_folium, location_point, destination_point)
    add_search_radius(map_folium, destination_point, radius)



def add_marker(map_folium, row, icon, destination_point):
    latitude = row.get('latitude')
    longitude = row.get('longitude')
    if latitude is None or longitude is None:
        return

    if icon == "🅿️" and destination_point:
        # Handling for Parkhaus markers
        name = row.get('phname', 'No Name Provided')
        # Format description to include "Description:" followed by the Parkhaus state
        description = f"Description: {row.get('phstate', 'No State Provided')}"
        parking_distance = geodesic((latitude, longitude), (destination_point[1], destination_point[0])).meters
        estimated_walking_time = int(parking_distance / 1.1 / 60)  # Walking speed approximation
        spaces_available = row.get('shortfree', 'N/A')
        total_spaces = row.get('shortmax', 'N/A')
        popup_text = f"Name: {name}<br>{description}<br>Estimated Walking Time: {estimated_walking_time} minutes<br>Spaces: {spaces_available}/{total_spaces}"
    else:
        # Simplified handling for other markers
        address = row.get('address', 'No Address Provided')
        popup_text = f"Address: {address}"

    folium.Marker(
        location=[latitude, longitude],
        popup=folium.Popup(popup_text, max_width=250),
        icon=folium.DivIcon(
            icon_size=(150, 36),
            icon_anchor=(7, 20),
            html=f'<div style="font-size: 10pt">{icon}</div>'
        )
    ).add_to(map_folium)



def add_user_markers(map_folium, location_point, destination_point):
    if location_point:
        folium.Marker(
            [location_point[1], location_point[0]],
            popup='La tua posizione',
            icon=folium.DivIcon(html='<div style="font-size: 30pt;">🏡</div>')
        ).add_to(map_folium)
    if destination_point:
        folium.Marker(
            [destination_point[1], destination_point[0]],
            popup='La tua destinazione',
            icon=folium.DivIcon(html='<div style="font-size: 30pt;">📍</div>')
        ).add_to(map_folium)


def add_search_radius(map_folium, destination_point, radius):
    if destination_point and radius:
        folium.Circle(
            radius=radius,
            location=[destination_point[1], destination_point[0]],
            color='Blue',
            fill=False
        ).add_to(map_folium)


def create_map():
    """Create an initial folium map centered on St. Gallen."""
    map_folium = folium.Map(location=[47.4237, 9.3747], zoom_start=14)
    return map_folium


def filter_parking_by_radius(data, destination_point, radius, show_only_free, address_provided):
    if destination_point is None:
        return data  # Restituisce i dati invariati se il punto di destinazione non è definito

    def condition(row):
        # Estrai le coordinate direttamente dai dati se disponibili, altrimenti usa 0,0 come default
        lat = row.get('latitude') or row.get('standort', {}).get('lat', 0)
        lon = row.get('longitude') or row.get('standort', {}).get('lon', 0)
        if lat and lon:
            distance_within_radius = geodesic(
                (lat, lon), (destination_point[1], destination_point[0])
            ).meters <= radius
            if show_only_free:
                # Considera solo i parcheggi liberi se richiesto
                return distance_within_radius and row.get('shortfree', 0) > 0
            return distance_within_radius
        return False

    filtered_data = data[data.apply(condition, axis=1)]
    return filtered_data


def find_nearest_parking_place(data, destination_point):
    if destination_point is None or data.empty:
        return None, None
    # Calculate the distance to the destination for each parking spot
    data['distance_to_destination'] = data.apply(
        lambda row: geodesic(
            ((row['latitude'] if pd.notna(row['latitude']) else 0),
             (row['longitude'] if pd.notna(row['longitude']) else 0)),
            (destination_point[1], destination_point[0])
        ).meters, axis=1
    )
    # Check if there are any data points to evaluate
    if not data['distance_to_destination'].empty:
        min_distance_index = data['distance_to_destination'].idxmin()
        nearest_place = data.loc[min_distance_index] if min_distance_index is not None else None
        if nearest_place is not None:
            estimated_walking_time = nearest_place['distance_to_destination'] / 1.1 / 60  # Convert seconds to minutes
            return nearest_place, estimated_walking_time
    return None, None

def display_time(time_container):
    # Define a custom style for the clock
    clock_style = """
    <style>
    .clock {
        font-size: 60px; /* Large font size for visibility */
        font-family: 'Arial', sans-serif; /* Modern sans-serif font */
        color: #333; /* Dark grey color for the text */
    }
    </style>
    """
    
    while True:
        current_time = datetime.now().strftime("%H:%M:%S")
        # Use custom styling and update the clock display
        time_container.markdown(clock_style + f"<div class='clock'>{current_time}</div>", unsafe_allow_html=True)
        time.sleep(1)  # Update every second

def calculate_and_display_distances(map_folium, location_point, destination_point, nearest_parking):
    if destination_point:
        if location_point:
            # Calculate distance from location point to destination
            distance_to_destination = geodesic((location_point[1], location_point[0]), (destination_point[1], destination_point[0])).meters
            time_to_destination = distance_to_destination / 1.1 / 60  # Convert to minutes
            st.markdown(f"**Estimated walking time from your location to destination:** {int(time_to_destination)} minutes")

        # Check if nearest_parking DataFrame is not empty and is specifically a Parkhaus
        if nearest_parking is not None and not nearest_parking.empty and nearest_parking['category'] == 'Parkhaus':
            # Calculate distance from nearest parking to destination
            parking_distance = geodesic((nearest_parking['latitude'], nearest_parking['longitude']), (destination_point[1], destination_point[0])).meters
            parking_time = parking_distance / 1.1 / 60
            name = nearest_parking.get('phname', 'No Name Provided')
            description = f"Description: {nearest_parking.get('phstate', 'No State Provided')}"
            spaces_available = nearest_parking.get('shortfree', 'N/A')
            total_spaces = nearest_parking.get('shortmax', 'N/A')

            # Display detailed parking information with HTML and CSS styling
            info_html = f"""
            <div style="background-color: #E5E4E2; padding: 10px; border-radius: 10px; margin: 10px 0;">
                <h4><b>Nearest Parkhaus Information</b></h4>
                <p><b>Name:</b> {name}</p>
                <p><b>Estimated Walking Time:</b> {int(parking_time)} minutes</p>
                <p><b>{description}</b></p>
                <p><b>Spaces:</b> {spaces_available}/{total_spaces}</p>
            </div>
            """
            st.markdown(info_html, unsafe_allow_html=True)
        else:
            st.error("No nearby Parkhaus found.")

def parse_datetime(date_str, time_str):
    try:
        return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    except ValueError:
        st.sidebar.error("Invalid datetime format. Please enter the date as YYYY-MM-DD and time as HHMM or HH:MM.")
        return None

def parse_datetime(date_str, time_str):
    try:
        if re.match(r'^\d{4}$', time_str):  # HHMM
            time_str = f"{time_str[:2]}:{time_str[2:]}"
        elif re.match(r'^\d{2}.\d{2}$', time_str):  # HH.MM
            time_str = time_str.replace('.', ':')
        return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    except ValueError:
        st.sidebar.error("Please enter the correct format for date and time.")
        return None

def calculate_duration(arrival_datetime, departure_datetime):
    if departure_datetime < arrival_datetime:
        st.sidebar.error("Departure datetime must be later than arrival datetime.")
        return None
    duration_delta = departure_datetime - arrival_datetime
    days = duration_delta.days
    hours = duration_delta.seconds // 3600
    minutes = (duration_delta.seconds % 3600) // 60
    return days, hours, minutes
    

def main():
    # Set page configuration with the new title and icon
    st.set_page_config(page_title="ParkGallen", page_icon="🅿️", layout="wide")

    # Define a container for the top row where the logo and the title will be placed
    top_row = st.container()
    with top_row:
        # Place logo in the top right corner above the search bar
        col1, col2 = st.columns([4,1])
        with col1:
            st.title("🅿️ ParkGallen")
        with col2:
            # Using a raw string to handle file path on Windows
            logo_path = r"C:\Users\gcazz\Downloads\Screenshot_2024-05-12_134147-removebg.png"
            st.image(logo_path, width=300)  # Adjust size as needed

    address = st.sidebar.text_input("Enter an address in St. Gallen:", key="address")
    destination = st.sidebar.text_input("Enter destination in St. Gallen:", key="destination")

    arrival_date_str = st.sidebar.date_input("Arrival Date")
    departure_date_str = st.sidebar.date_input("Departure Date")
    arrival_time_str = st.sidebar.text_input("Arrival Time")
    departure_time_str = st.sidebar.text_input("Departure Time")

    arrival_datetime = parse_datetime(arrival_date_str.strftime("%Y-%m-%d"), arrival_time_str) if arrival_time_str else None
    departure_datetime = parse_datetime(departure_date_str.strftime("%Y-%m-%d"), departure_time_str) if departure_time_str else None

    if arrival_datetime and departure_datetime:
        duration_info = calculate_duration(arrival_datetime, departure_datetime)
        if duration_info:
            days, hours, minutes = duration_info
            st.sidebar.text(f"Duration: {days} days, {hours} hours, {minutes} minutes")

    radius = st.sidebar.slider("Select search radius (in meters):", min_value=50, max_value=1000, value=500, step=50)

    show_parkhaus = st.sidebar.checkbox("🅿️ Parkhaus (Free & Limited)", True)
    show_extended_blue = st.sidebar.checkbox("🔵 Extended Blue Zone", True)
    show_white = st.sidebar.checkbox("⚪ White Parking", True)
    show_handicapped = st.sidebar.checkbox("♿ Handicapped Parking", True)

    if st.sidebar.button("Show Parking"):
        # Assuming other necessary data-fetching and processing functions are defined elsewhere
        st.write("Implement the logic to show parking data on the map")

    st.write("### Legend")
    st.write("🏡 = Your Location | 📍= Your Destination | 🅿️ = Parkhaus | 🔵 = Extended Blue Zone | ⚪ = White Parking | ♿ = Handicapped")

if __name__ == "__main__":
    main()
