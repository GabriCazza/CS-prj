import requests

def fetch_parking_data(api_url, limit=20):
    try:
        # Make a GET request to the API endpoint
        response = requests.get(api_url, params={"limit": limit})
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the JSON response
        data = response.json()
        return data.get("records", [])
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch parking data: {e}")

# Example usage:
API_URL = "https://daten.stadt.sg.ch/api/explore/v2.1/catalog/datasets/freie-parkplatze-in-der-stadt-stgallen-pls/records"
parking_data = fetch_parking_data(API_URL)
print(parking_data)

