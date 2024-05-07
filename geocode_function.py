def geocode_address(location):
    """Converts an address to a point (latitude, longitude) using Nominatim API."""
    if location:
        geolocator = Nominatim(user_agent="geocoding_app")
        full_address = f"{location}, St. Gallen, Switzerland"
        for _ in range(3):  # Retry logic
            try:
                geocoded_location = geolocator.geocode(full_address)
                if geocoded_location:
                    return (geocoded_location.longitude, geocoded_location.latitude)
            except GeocoderRateLimited as e:
                st.warning("Rate limit exceeded, waiting to retry...")
                time.sleep(10)  # wait 10 seconds before retrying
            except Exception as e:
                st.error(f"Geocoding error: {e}")
                break
    return None


def add_markers_to_map(map_folium, original_data, additional_data, location_point, destination_point, radius, show_parkhaus, show_extended_blue, show_white, show_handicapped):
    # Handling parking data from the first API
    if not original_data.empty:
        for _, row in original_data.iterrows():
            if row['phstate'].lower() == 'offen':  # Solo se il parcheggio è aperto
                # Filtra per Parkhaus se ci sono posti liberi o meno di 25
                if show_parkhaus and (row['shortfree'] > 0): 
                    popup_text = f"{row['phname']} - Spazi liberi: {row['shortfree']}/{row['shortmax']}"
                    folium.Marker(
                        [row['standort']['lat'], row['standort']['lon']],
                        icon=folium.DivIcon(html=f'<div style="font-size: 18pt">🅿️</div>'),
                        popup=folium.Popup(popup_text, max_width=250)
                    ).add_to(map_folium)

    # Handling additional data from the second API (points of interest)
    if not additional_data.empty:
        for index, row in additional_data.iterrows():
            description = row['description'].lower()  # Normalize the text for reliable matching
            
            if "erweiterte blaue zone" in description and show_extended_blue:
                add_marker(map_folium, row, "🔵")
            if ("weiss (bewirtschaftet)" in description or "weisse zone" in description) and show_white:
                add_marker(map_folium, row, "⚪")
            if "invalidenparkplatz" in description and show_handicapped:
                add_marker(map_folium, row, "♿")

    add_user_markers(map_folium, location_point, destination_point)
    add_search_radius(map_folium, destination_point, radius)

def add_marker(map_folium, row, icon):
    popup_text = f"Nome: {row['name']}<br>Descrizione: {row['description']}<br>Indirizzo: {row['address']}"
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=popup_text,
        icon=folium.DivIcon(
            icon_size=(150,36),
            icon_anchor=(7,20),
            html=f'<div style="font-size: 24pt">{icon}</div>',
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


def filter_parking_by_radius(data, location_point, radius, show_only_free, address_provided):
    """Filter parking data by radius from a given location point and availability.
    Automatically shows only free spaces if an address is provided."""
    if location_point is None:
        return data
    # Define a non-recursive condition for filtering by radius and availability
    def condition(row):
        distance_within_radius = geodesic(
            (row['standort']['lat'], row['standort']['lon']), 
            (location_point[1], location_point[0])
        ).meters <= radius
        if address_provided or show_only_free:
            return distance_within_radius and row['shortfree'] > 0
        return distance_within_radius

    # Apply the condition to filter data
    filtered_data = data[data.apply(condition, axis=1)]
    return filtered_data

def find_nearest_parking_place(data, destination_point):
    """Find the nearest parking place to the destination."""
    if destination_point is None:
        return None, None, None
    data['distance_to_destination'] = data.apply(
        lambda row: geodesic(
            (row['standort']['lat'], row['standort']['lon']),
            (destination_point[1], destination_point[0])
        ).meters, axis=1
    )
    nearest_place = data.loc[data['distance_to_destination'].idxmin()]
    if 'phname' in nearest_place:
        nearest_place_name = nearest_place['phname']
        estimated_walking_time = nearest_place['distance_to_destination'] / 60  # Assuming walking speed of 1 m/s
        free_spaces = nearest_place.get('shortfree', None)  # Get free spaces, return None if not available
        return nearest_place_name, estimated_walking_time, free_spaces
    else:
        return None, None, None

