import streamlit as st
from datetime import datetime, date, time
from geopy import geocoders, exc
import pandas as pd
import folium
from streamlit_folium import folium_static
import requests
from geopy.distance import geodesic
import random
import re
import math 

#Used to handale the API with a rate limit (unrelible conditions)
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
    return None  

#Call of the first API (Parkhaus platzte)

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
    
# Call of the second API (all the Parkings)   
 
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



# Used to convert a textual address into geographical coordinates (latitude and longitude) using the Nominatim geocoding API

def geocode_address(location):
    """Converts an address to a point (latitude, longitude) using the Nominatim API."""
    if location:
        geolocator = geocoders.Nominatim(user_agent="geocoding_app", timeout=10)
        try:
            geocoded_location = geolocator.geocode(location + ", St. Gallen, Switzerland")
            if geocoded_location:
                return (geocoded_location.longitude, geocoded_location.latitude)
        except exc.GeocoderRateLimited as e:
            st.warning("Rate limit exceeded, waiting to retry...")
            time.sleep(10)  # Wait 10 seconds before retrying
        except Exception as e:
            st.error(f"Geocoding error: {e}")
    return None



def add_markers_to_map(map_folium, original_data, additional_data, location_point, destination_point, radius, show_parkhaus, show_extended_blue, show_white, show_handicapped, address):
    address_provided = bool(address)
    filtered_original_data = filter_parking_by_radius(original_data, destination_point, radius, show_parkhaus, address_provided)
    filtered_additional_data = filter_parking_by_radius(additional_data, destination_point, radius, False, address_provided)

    # Inizializza i conteggi a zero
    blue_count = 0
    white_count = 0
    handicapped_count = 0

    if show_parkhaus:
        for _, row in filtered_original_data.iterrows():
            if row.get('category', '') == 'Parkhaus':
                add_marker(map_folium, row, "🅿️", destination_point)

    if show_extended_blue:
        for _, row in filtered_additional_data.iterrows():
            if "erweiterte blaue zone" in row.get('info', '').lower():
                add_marker(map_folium, row, "🔵", None)
                blue_count += 1

    if show_white:
        for _, row in filtered_additional_data.iterrows():
            if "weiss (bewirtschaftet)" in row.get('info', '').lower() or "weisse zone" in row.get('info', '').lower():
                add_marker(map_folium, row, "⚪", None)
                white_count += 1

    if show_handicapped:
        for _, row in filtered_additional_data.iterrows():
            if "invalidenparkplatz" in row.get('info', '').lower():
                add_marker(map_folium, row, "♿", None)
                handicapped_count += 1
    
    return blue_count, white_count, handicapped_count

# Function used to add various types of parking markers to a map created with Folium


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

# Function is used  to add visual markers for the user's location and destination on a Folium map

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


# Function used to display the radius on the map

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
        st.error("Destination not specified or no parking data available.")
        return None, None

    # Filter for Parkhaus
    parkhaus_data = data[data['category'] == 'Parkhaus']
    if parkhaus_data.empty:
        st.error("No 'Parkhaus' available in the data.")
        return None, None

    # Calculate the distance of each Parkhaus from the destination
    parkhaus_data['distance_to_destination'] = parkhaus_data.apply(
        lambda row: geodesic(
            (row['latitude'], row['longitude']),
            (destination_point[1], destination_point[0])
        ).meters, axis=1
    )

    # Find the nearest Parkhaus
    nearest_parkhaus = parkhaus_data.loc[parkhaus_data['distance_to_destination'].idxmin()] if not parkhaus_data.empty else None
    if nearest_parkhaus is not None:
        estimated_walking_time = nearest_parkhaus['distance_to_destination'] / 1000 / 1.1 * 60  # Convert meters to minutes assuming 1.1 m/s walking speed
        return nearest_parkhaus, estimated_walking_time
    else:
        st.error("No nearby valid Parkhaus found.")
        return None, None



def calculate_and_display_distances(map_folium, location_point, destination_point, nearest_parking):
    if destination_point:
        if location_point:
            # Calculate distance from location point to destination
            distance_to_destination = geodesic((location_point[1], location_point[0]), (destination_point[1], destination_point[0])).meters
            time_to_destination = distance_to_destination / 1.1 / 60  # Convert to minutes
            st.markdown(f"*Estimated walking time from your location to destination:* {int(time_to_destination)} minutes")

        # Check if nearest_parking DataFrame is not empty and is specifically a Parkhaus
        if nearest_parking is not None and not nearest_parking.empty and nearest_parking['category'] == 'Parkhaus':
            # Calculate distance from nearest parking to destination
            parking_distance = geodesic((nearest_parking['latitude'], nearest_parking['longitude']), (destination_point[1], destination_point[0])).meters
            parking_time = parking_distance / 1.1 / 60
            name = nearest_parking.get('phname', 'No Name Provided')
            description = f"Description: {nearest_parking.get('phstate', 'No State Provided')}"
            spaces_available = nearest_parking.get('shortfree', 'N/A')
            total_spaces = nearest_parking.get('shortmax', 'N/A')
        else:
            st.error("No nearby Parkhaus found.")

def parse_datetime(date_str, time_str):
    try:
        if re.match(r'^\d{4}$', time_str):  # HHMM
            time_str = f"{time_str[:2]}:{time_str[2:]}"
        elif re.match(r'^\d{2}\.\d{2}$', time_str):  # HH.MM
            time_str = time_str.replace('.', ':')
        return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    except ValueError:
        return None

def calculate_duration(arrival_datetime, departure_datetime):
    """Calculates the duration between arrival and departure times and returns the duration in days, hours, and minutes."""
    if departure_datetime <= arrival_datetime:
        st.sidebar.write("Departure datetime must be later than arrival datetime.")
        return 0, 0, 0  # Return zero days, hours, and minutes if invalid.
    duration_delta = departure_datetime - arrival_datetime
    days = duration_delta.days
    hours = (duration_delta.seconds // 3600) % 24
    minutes = (duration_delta.seconds % 3600) // 60
    return days, hours, minutes


def calculate_parking_fees(parking_name, arrival_datetime, duration_hours):
    rates = {
        "Manor": {
            "daytime": (5.5, 21),
            "nighttime": (21, 0.5),
            "rates": [(1, 2), (3, 3, 20), (None, 4.5, 20)],
            "night_rate": 1
        },
        "Bahnhof": {
            "free_minutes": 10,
            "rates": [(0.5, 1.5), (1, 3), (None, 4, 30)]
        },
        "Neumarkt": {
            "flat_rate": 1
        },
        "Rathaus": {
            "daytime": (7, 22),
            "nighttime": (22, 7),
            "day_rate": 2.4,
            "night_rate": 1.2
        },
        "Kreuzbleiche": {
            "daytime": (7, 22),
            "nighttime": (22, 7),
            "day_rate": 1.5,
            "night_rate": 1
        },
        "Oberer Graben": {
            "daytime": (6, 23),
            "nighttime": (23, 6),
            "day_rate": 2,
            "night_rate": 1.5
        },
        "Raiffeisen": {
            "rates": [(3, 2), (None, 1.5, 60)]
        },
        "Einstein": {
            "flat_rate": 2.5
        },
        "Spisertor": {
            "flat_rate": 2.5
        },
        "Burggraben": {
            "daytime": (7, 24),
            "nighttime": (24, 7),
            "extended_rate": [(3, 2), (None, 1, 60)],
            "night_rate": 0.6
        },
        "Brühltor": {
            "daytime": (7, 24),
            "nighttime": (24, 7),
            "extended_rate": [(3, 2), (None, 1, 60)],
            "night_rate": 0.6
        },
        "Stadtpark/AZSG": {
            "daytime": (7, 24),
            "nighttime": (24, 7),
            "extended_rate": [(3, 1.6), (None, 0.8, 60)],
            "night_rate": 0.6
        },
        "Spelterini": {
            "daytime": (7, 24),
            "nighttime": (24, 7),
            "extended_rate": [(3, 2), (None, 1.5, 60)],
            "night_rate": 0.6
        },
        "Olma fairs": {
            "rates": [(3, 2), (None, 1.5, 60)]
        },
        "Unterer Graben": {
            "flat_rate": 2
        },
        "Olma parking lot": {
            "daytime": (6, 23),
            "nighttime": (23, 6),
            "day_rate": 2,
            "night_rate": 1.5
        }
    }

    park_info = rates.get(parking_name)
    if not park_info:
        return f"Information not available for {parking_name}."

    if 'flat_rate' in park_info:
        total_fee = park_info['flat_rate'] * math.floor(duration_hours)
        return f"Total parking fee at {parking_name}: {total_fee:.2f} CHF"

    total_fee = 0
    hours_left = math.floor(duration_hours)  # Use math.floor to round down the hours
    current_time = arrival_datetime.hour + arrival_datetime.minute / 60

    # Calculate fees based on day and night rates
    while hours_left > 0:
        if 'daytime' in park_info and current_time < park_info['daytime'][1]:
            if current_time < park_info['daytime'][0]:
                current_time = park_info['daytime'][0]  # Jump to daytime start if before it
            day_hours = min(hours_left, park_info['daytime'][1] - current_time)
            total_fee += day_hours * park_info.get('day_rate', 0)
            hours_left -= day_hours
            current_time += day_hours
        elif 'nighttime' in park_info:
            if current_time >= park_info['nighttime'][1] and current_time < 24:
                current_time = 24  # Skip to end of day if after nighttime
            else:
                night_hours = min(hours_left, park_info['nighttime'][1] - current_time)
                total_fee += night_hours * park_info.get('night_rate', 0)
                hours_left -= night_hours
                current_time += night_hours
        current_time %= 24  # Reset time to start of the next day if needed

    return f"Total parking fee at {parking_name}: {total_fee:.2f} CHF"


       
# Funzione ausiliaria per visualizzare le informazioni del parcheggio
def display_parking_information(nearest_parkhaus, parking_fee, blue_count, white_count, handicapped_count, estimated_walking_time):
    info_column, extra_info_column = st.columns(2)
    with info_column:
        st.markdown(f"""
        <div style="background-color:#86B97A; padding:10px; border-radius:5px;">
            <h4>Nearest Parkhaus Information</h4>
            <p>Name: {nearest_parkhaus.get('phname', 'Unknown')}</p>
            <p>Estimated Walking Time: {int(estimated_walking_time)} minutes</p>
            <p>Description: {nearest_parkhaus.get('phstate', 'No Description')}</p>
            <p>Spaces: {nearest_parkhaus.get('shortfree', 'N/A')}/{nearest_parkhaus.get('shortmax', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
    with extra_info_column:
        st.markdown(f"""
        <div style="background-color:#ADF09E; padding:10px; border-radius:5px;">
            <h4>Additional Information</h4>
            <p>Blue parking spots: {blue_count}</p>
            <p>White parking spots: {white_count}</p>
            <p>Handicapped parking spots: {handicapped_count}</p>
            <p>Estimated parking fee: {parking_fee}</p>
        </div>
        """, unsafe_allow_html=True)





#The Whole MAIN function 
        
def main():
    st.set_page_config(page_title="Parking Spaces in St.Gallen", page_icon="🅿️", layout="wide")

    # User Interface Configuration
    top_row = st.container()
    with top_row:
        col1, col2 = st.columns([0.4, 4])
        with col1:
            logo_path = "image-removebg-preview (1).png"  # Ensure the image path is correct
            st.image(logo_path, width=100)
        with col2:
            st.title("arkGallen")

    # Address and Destination Input
    st.sidebar.image(logo_path, width=120)
    st.sidebar.markdown("### Enter a valid destination in St. Gallen")
    address = st.sidebar.text_input("Enter an address in St. Gallen:", key="address")
    destination = st.sidebar.text_input("Enter destination in St. Gallen:", key="destination")

    # Date and Time Selection
    arrival_date = st.sidebar.date_input("Arrival Date", date.today())
    departure_date = st.sidebar.date_input("Departure Date", date.today())
    arrival_time_str = st.sidebar.text_input("Enter arrival time (HHMM or HH.MM):", key="arrival_time")
    departure_time_str = st.sidebar.text_input("Enter departure time (HHMM or HH.MM):", key="departure_time")

    # Parse datetime using custom function for flexibility
    arrival_datetime = parse_datetime(arrival_date.strftime("%Y-%m-%d"), arrival_time_str)
    departure_datetime = parse_datetime(departure_date.strftime("%Y-%m-%d"), departure_time_str)
    if arrival_datetime is None or departure_datetime is None:
        st.sidebar.error("Invalid time format. Please use HHMM or HH.MM.")
        return

    # Calculate duration and format it
    if departure_datetime > arrival_datetime:
        duration_delta = departure_datetime - arrival_datetime
        days, remainder = divmod(duration_delta.total_seconds(), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes = remainder // 60
        st.sidebar.write(f"Duration of parking: {int(days)} days, {int(hours)} hours, {int(minutes)} minutes")
    else:
        st.sidebar.error("Departure time must be after arrival time.")
        return

    total_seconds = (departure_datetime - arrival_datetime).total_seconds()
    total_hours = total_seconds / 3600
    rounded_total_hours = math.floor(total_hours)  # Ensure charges are for complete hours only

    # Geocode addresses
    location_point = geocode_address(address) if address else None
    destination_point = geocode_address(destination) if destination else None

    # Check for valid destination
    if not destination_point:
        st.sidebar.error("Please provide a valid destination.")
        return

    # Slider and parking options
    radius = st.sidebar.slider("Select search radius (in meters):", min_value=50, max_value=1000, value=500, step=50)
    show_parkhaus = st.sidebar.checkbox("🅿️ Parkhaus (Free & Limited)", True)
    show_extended_blue = st.sidebar.checkbox("🔵 Extended Blue Zone", True)
    show_white = st.sidebar.checkbox("⚪ White Parking", True)
    show_handicapped = st.sidebar.checkbox("♿ Handicapped Parking", True)

    # Display parking and calculate fees
    if st.sidebar.button("Show Parking and Calculate Fees"):
        with st.spinner("Loading information for you"):
            original_data = fetch_parking_data()
            additional_data = fetch_additional_data()
            filtered_data = filter_parking_by_radius(original_data, destination_point, radius, True, bool(address))
            map_folium = create_map()
            add_search_radius(map_folium, destination_point, radius)
            add_user_markers(map_folium, location_point, destination_point)
            blue_count, white_count, handicapped_count = add_markers_to_map(map_folium, original_data, additional_data, location_point, destination_point, radius, show_parkhaus, show_extended_blue, show_white, show_handicapped, address)
            
            folium_static(map_folium)
            
            # Display the legend above the map
            st.markdown("### Legend")
            st.markdown("🏡 = Your Location | 📍= Your Destination | 🅿️ = Parkhaus | 🔵 = Extended Blue Zone | ⚪ = White Parking | ♿ = Handicapped")
            
            nearest_parkhaus, estimated_walking_time = find_nearest_parking_place(filtered_data, destination_point)
            if nearest_parkhaus is not None and not nearest_parkhaus.empty:
                parking_fee = calculate_parking_fees(nearest_parkhaus.get('phname', 'Unknown'), arrival_datetime, (departure_datetime - arrival_datetime).total_seconds() / 3600)
                if "Information not available" in parking_fee or "Rate information is incomplete" in parking_fee:
                    st.error(parking_fee)
                else:
                    # Include the estimated walking time in the display function
                    display_parking_information(nearest_parkhaus, parking_fee, blue_count, white_count, handicapped_count, estimated_walking_time)
            else:
                st.error("No nearby valid Parkhaus found or the Parkhaus name is missing.")


if __name__ == "__main__":
    main()