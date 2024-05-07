def main():
    st.set_page_config(page_title="Parking Spaces in St.Gallen", page_icon="🅿️", layout="wide")
    st.title("🅿️ Parking Spaces in St. Gallen")

    # Inputs for address and destination
    address = st.sidebar.text_input("Enter an address in St. Gallen:", key="address")
    destination = st.sidebar.text_input("Enter destination in St. Gallen:", key="destination")
    location_point = geocode_address(address) if address else None
    destination_point = geocode_address(destination) if destination else None
    radius = st.sidebar.slider("Select search radius (in meters):", min_value=100, max_value=3000, value=1000, step=50, key='radius')

    # Sidebar checkboxes for filtering parking data
    show_parkhaus = st.sidebar.checkbox("🅿️ Show Parkhaus (Free & Limited)", True)
    show_extended_blue = st.sidebar.checkbox("🔵 Show Extended Blue Zone", True)
    show_white = st.sidebar.checkbox("⚪ Show White Parking", True)
    show_handicapped = st.sidebar.checkbox("♿ Show Handicapped Parking", True)

    # Button to show parking based on filters
    if st.sidebar.button("Show Parking"):
        original_data = fetch_parking_data()
        additional_data = fetch_additional_data()
        filtered_data = filter_parking_by_radius(original_data, location_point, radius, True, bool(address))

        map_folium = create_map()
        add_markers_to_map(map_folium, filtered_data, additional_data, location_point, destination_point, radius, show_parkhaus, show_extended_blue, show_white, show_handicapped)
        folium_static(map_folium)

    # Display map legend
    st.write("### Legend")
    st.write("🏡 = Your Location | 📍= Your Destination | 🅿️ = Parkhaus | 🔵 = Extended Blue Zone | ⚪ = White Parking | ♿ = Handicapped Parking")

if __name__ == "__main__":
    main()
