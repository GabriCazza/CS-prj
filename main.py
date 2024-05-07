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
import script 
import geocode_function.py


def fetch_additional_data():
    """Fetch all additional parking data from the API with pagination."""
    base_url = "https://daten.stadt.sg.ch/api/explore/v2.1/catalog/datasets/points-of-interest-/records"
    params = {
        "refine": 'kategorie:"Parkplätze, Parkhäuser"',
        "limit": 100,  # Maximum number of results per page
        "offset": 0
    }
    parking_data = []

    while True:
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            if not results:
                break  # Break the loop if no more results are available

            for item in results:
                geo_point = item['geo_point_2d']
                parking_data.append({
                    'latitude': geo_point['lat'],
                    'longitude': geo_point['lon'],
                    'name': item.get('name', 'No Name Provided'),
                    'description': item.get('informatio', 'No Description Provided'),
                    'address': item.get('adresse', 'No Address Provided')
                })

            params['offset'] += params['limit']  # Increase offset to fetch the next page of results
        else:
            st.error(f"Failed to fetch additional data: HTTP Status Code {response.status_code}")
            break

    return pd.DataFrame(parking_data)

    
def fetch_parking_data():
    """Fetch parking data from an API."""
    API_ENDPOINT = "https://daten.stadt.sg.ch/api/explore/v2.1/catalog/datasets/freie-parkplatze-in-der-stadt-stgallen-pls/records?limit=20"
    response = requests.get(API_ENDPOINT)
    if response.status_code == 200:
        data = response.json()['results']
        # Convertiamo i dati in DataFrame e aggiungiamo una colonna per la categoria Parkhaus
        parking_data = pd.DataFrame(data)
        parking_data['category'] = parking_data.apply(lambda x: 'Parkhaus' if x['phstate'] == 'offen' else 'Closed', axis=1)
        return parking_data
    else:
        st.error(f'Failed to retrieve data: HTTP Status Code {response.status_code}')
        return pd.DataFrame()
