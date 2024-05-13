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
        st.error("Destination not specified or no parking data available.")
        return None, None

    # Filtra solo i Parkhaus
    parkhaus_data = data[data['category'] == 'Parkhaus']
    if parkhaus_data.empty:
        st.error("No 'Parkhaus' available in the data.")
        return None, None

    # Calcola la distanza di ogni Parkhaus dalla destinazione
    parkhaus_data['distance_to_destination'] = parkhaus_data.apply(
        lambda row: geodesic(
            (row['latitude'], row['longitude']),
            (destination_point[1], destination_point[0])
        ).meters, axis=1
    )

    # Trova il Parkhaus più vicino
    nearest_parkhaus = parkhaus_data.loc[parkhaus_data['distance_to_destination'].idxmin()] if not parkhaus_data.empty else None
    if nearest_parkhaus is not None:
        print("Nearest Parkhaus Found:", nearest_parkhaus)
        estimated_walking_time = nearest_parkhaus['distance_to_destination'] / 1000 / 1.1 * 60  # Converti i metri in minuti
        return nearest_parkhaus, estimated_walking_time
    else:
        st.error("No nearby valid Parkhaus found.")
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

            # Display detailed parking information with HTML and CSS styling
            info_html = f"""
            <div style="background-color: #9CC8A1 ; padding: 10px; border-radius: 10px; margin: 10px 0;">
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
        if re.match(r'^\d{4}$', time_str):  # HHMM
            time_str = f"{time_str[:2]}:{time_str[2:]}"
        elif re.match(r'^\d{2}.\d{2}$', time_str):  # HH.MM
            time_str = time_str.replace('.', ':')
        return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    except ValueError:
        st.sidebar.error("Please enter the correct format for date and time.")
        return None

def calculate_duration(arrival_datetime, departure_datetime):
    """Calculates the duration between arrival and departure times and returns the duration in days, hours, and minutes."""
    if departure_datetime <= arrival_datetime:
        st.sidebar.error("Departure datetime must be later than arrival datetime.")
        return 0, 0, 0  # Return zero days, hours, and minutes if invalid.
    duration_delta = departure_datetime - arrival_datetime
    days = duration_delta.days
    hours = (duration_delta.seconds // 3600) % 24
    minutes = (duration_delta.seconds % 3600) // 60
    return days, hours, minutes


def calculate_parking_fees(parking_name, arrival_datetime, duration_hours):
    rates = {
        "Manor": {
            "daytime": (5.5, 21),  # Active hours start, end
            "nighttime": (21, 0.5),  # Night hours start, end
            "rates": [(1, 2), (3, 1, 20), (None, 1.5, 20)],
            "night_rate": 1
        },
        "Bahnhof": {
            "free_minutes": 10,
            "rates": [(0.5, 1.5), (1, 3), (None, 2, 30)]
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
            "flat_rate": 2,
            "extended_rate": 1.5,
            "extended_after_hours": 3
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
            "day_rate": 2,
            "extended_rate": 1,
            "extended_after_hours": 3,
            "night_rate": 0.6
        },
        "Brühltor": {
            "daytime": (7, 24),
            "nighttime": (24, 7),
            "day_rate": 2,
            "extended_rate": 1,
            "extended_after_hours": 3,
            "night_rate": 0.6
        },
        "Stadtpark/AZSG": {
            "daytime": (7, 24),
            "nighttime": (24, 7),
            "day_rate": 1.6,
            "extended_rate": 0.8,
            "extended_after_hours": 3,
            "night_rate": 0.6
        },
        "Spelterini": {
            "daytime": (7, 24),
            "nighttime": (24, 7),
            "day_rate": 2,
            "extended_rate": 1.5,
            "extended_after_hours": 3,
            "night_rate": 0.6
        },
        "Olma fairs": {
            "flat_rate": 2,
            "extended_rate": 1.5,
            "extended_after_hours": 3
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
        return "Parking rate information not available."

    total_fee = 0
    current_time = arrival_datetime.hour + arrival_datetime.minute / 60

    # Handle flat rate parking
    if "flat_rate" in park_info:
        return f"Total parking fee at {parking_name}: {duration_hours * park_info['flat_rate']:.2f} CHF"

    # Check free minutes
    if "free_minutes" in park_info and duration_hours * 60 <= park_info["free_minutes"]:
        return f"Total parking fee at {parking_name}: {total_fee:.2f} CHF"

    hours_left = duration_hours

    # Calculate daytime and nighttime fees
    while hours_left > 0:
        if park_info['daytime'][0] <= current_time < park_info['daytime'][1]:
            # Daytime rate calculation
            day_hours = min(hours_left, park_info['daytime'][1] - current_time)
            total_fee += day_hours * park_info.get('day_rate', 0)
        else:
            # Nighttime rate calculation
            night_hours = min(hours_left, 24 - current_time + park_info['nighttime'][0] if current_time >= park_info['nighttime'][0] else park_info['nighttime'][1] - current_time)
            total_fee += night_hours * park_info.get('night_rate', 0)

        # Update the time and remaining hours
        current_time = (current_time + night_hours + day_hours) % 24
        hours_left -= (night_hours + day_hours)

    return f"Total parking fee at {parking_name}: {total_fee:.2f} CHF"

def main():
    st.set_page_config(page_title="Parking Spaces in St.Gallen", page_icon="🅿️", layout="wide")

    # Setup the top row with title and optional image
    top_row = st.container()
    with top_row:
        col1, col2 = st.columns([0.4, 4])
        with col2:
            st.title("Parking in St. Gallen")
        with col1:
            logo_path = "image-removebg-preview (1).png"  # Update the path if necessary
            st.image(logo_path, width=100)

    # Input fields for user to enter address and destination
    address = st.sidebar.text_input("Enter an address in St. Gallen:", key="address")
    destination = st.sidebar.text_input("Enter destination in St. Gallen:", key="destination")

    # Input fields for selecting arrival and departure dates and times
    arrival_date = st.sidebar.date_input("Arrival Date", date.today())
    departure_date = st.sidebar.date_input("Departure Date", date.today())
    arrival_time = st.sidebar.time_input("Arrival Time", time(8, 0))
    departure_time = st.sidebar.time_input("Departure Time", time(18, 0))

    # Combine date and time inputs into datetime objects
    arrival_datetime = datetime.combine(arrival_date, arrival_time)
    departure_datetime = datetime.combine(departure_date, departure_time)

    # Calculate duration of stay
    days, hours, minutes = calculate_duration(arrival_datetime, departure_datetime)
    total_hours = days * 24 + hours + minutes / 60
    st.sidebar.write(f"Duration: {days} days, {hours} hours, {minutes} minutes")

    # Geocode the address and destination input by the user
    location_point = geocode_address(address) if address else None
    destination_point = geocode_address(destination) if destination else None

    # Validate the destination point
    if not destination_point:
        st.sidebar.write("Please enter a valid destination to find nearby parking.")
        return

    # Additional settings for parking search
    radius = st.sidebar.slider("Select search radius (in meters):", min_value=50, max_value=1000, value=500, step=50)
    show_parkhaus = st.sidebar.checkbox("🅿️ Parkhaus (Free & Limited)", True)
    show_extended_blue = st.sidebar.checkbox("🔵 Extended Blue Zone", True)
    show_white = st.sidebar.checkbox("⚪ White Parking", True)
    show_handicapped = st.sidebar.checkbox("♿ Handicapped Parking", True)

    # Button to trigger parking search
    if st.sidebar.button("Show Parking"):
        original_data = fetch_parking_data()
        additional_data = fetch_additional_data()
        filtered_data = filter_parking_by_radius(original_data, destination_point, radius, True, bool(address))

        map_folium = create_map()
        # Only include parking spots that are 'open' and have 'shortfree' > 1
        open_parking_data = original_data[(original_data['phstate'] == 'offen') & (original_data['shortfree'] > 1)]
        # Ensure add_markers_to_map function is called with all necessary parameters including address
        add_markers_to_map(map_folium, open_parking_data, additional_data, location_point, destination_point, radius, show_parkhaus, show_extended_blue, show_white, show_handicapped, address)
        
        nearest_parking, _ = find_nearest_parking_place(filtered_data, destination_point)
        if nearest_parking is not None:
            calculate_and_display_distances(map_folium, location_point, destination_point, nearest_parking)
            parking_fee = calculate_parking_fees(parking_name, arrival_datetime, total_hours)
            st.sidebar.write(parking_fee)
            calculate_and_display_distances(map_folium, location_point, destination_point, nearest_parking)
        folium_static(map_folium)
    # Display legend for map markers
    st.write("### Legend")
    st.write("🏡 = Your Location | 📍= Your Destination | 🅿️ = Parkhaus | 🔵 = Extended Blue Zone | ⚪ = White Parking | ♿ = Handicapped")

if __name__ == "__main__":
    main()

