import streamlit as st
import requests
from PIL import Image
from io import BytesIO

def download_satellite_image(api_key, lat, lon, zoom, img_file_name):
    """
    Downloads a satellite image from Google Maps for the specified location.

    Parameters:
    - api_key: Your Google Maps API key as a string.
    - lat: Latitude of the location as a float.
    - lon: Longitude of the location as a float.
    - zoom: Zoom level as an integer (values from 0 to 21+).
    - img_file_name: File name to save the image.
    """
    url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom={zoom}&size=600x600&maptype=satellite&key={api_key}"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        with open(img_file_name, 'wb') as file:
            file.write(response.content)
        print(f"Image successfully downloaded: {img_file_name}")
    else:
        print("Failed to download the image. Check your API key and quota.")

def find_places(api_key, query, location, radius=5000):
    """
    Finds places matching a query within a specified location and radius.

    Parameters:
    - api_key: Your Google Places API key as a string.
    - query: The search query (e.g., "camp sites") as a string.
    - location: The latitude and longitude of the center of the search area, in "lat,lon" format.
    - radius: The radius of the search area in meters (default is 5000).

    Returns:
    A list of dictionaries with details of each place found.
    """
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": query,
        "location": location,
        "radius": radius,
        "key": api_key
    }
    
    response = requests.get(url, params=params)
    results = response.json().get("results", [])
    
    places = []
    for result in results:
        place = {
            "name": result["name"],
            "latitude": result["geometry"]["location"]["lat"],
            "longitude": result["geometry"]["location"]["lng"],
            "zoom": 12  # Example zoom level, adjust as needed
        }
        places.append(place)
    
    return places

def get_lat_long(api_key, address):
    """
    Returns the latitude and longitude of a given address using the Google Geocoding API.

    Parameters:
    - api_key: Your Google Geocoding API key as a string.
    - address: The address of the location as a string.

    Returns:
    A tuple containing the latitude and longitude of the address, or (None, None) if not found.
    """
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": api_key}
    response = requests.get(url, params=params)
    result = response.json()

    if result["status"] == "OK":
        latitude = result["results"][0]["geometry"]["location"]["lat"]
        longitude = result["results"][0]["geometry"]["location"]["lng"]
        return latitude, longitude
    else:
        print(f"Error finding location: {result['status']}")
        return None, None
    
def download_image_as_bytes(api_key, lat, lon, zoom):
    """Downloads a satellite image and returns it as bytes."""
    url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom={zoom}&size=600x600&maptype=satellite&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return BytesIO(response.content)
    else:
        return None

# Streamlit application starts here
st.title('CampRecon')

api_key = st.text_input('Enter your Google API Key', '')

address = st.text_input('Enter an address or location', '')

# Add a number_input for zoom level
zoom = st.number_input('Zoom Level', min_value=0, max_value=21, value=12, step=1)

if address and api_key:
    latitude, longitude = get_lat_long(api_key, address)
    if latitude is not None and longitude is not None:
        st.write(f"Latitude: {latitude}, Longitude: {longitude}")
        query = st.text_input('Enter search query for nearby places', 'camp sites')
        if query:
            places = find_places(api_key, query, f"{latitude},{longitude}")
            if places:
                place_options = [f"{place['name']} ({place['latitude']}, {place['longitude']})" for place in places]
                selected_place = st.selectbox('Select a place to view', place_options)
                if selected_place:
                    selected_index = place_options.index(selected_place)
                    selected_lat = places[selected_index]['latitude']
                    selected_lon = places[selected_index]['longitude']
                    image_bytes = download_image_as_bytes(api_key, selected_lat, selected_lon, zoom)  # Use the user-specified zoom level
                    if image_bytes:
                        image = Image.open(image_bytes)
                        st.image(image, caption='Satellite Image', use_column_width=True)
                    else:
                        st.error('Failed to download the image. Check your API key and quota.')
            else:
                st.write('No places found.')
    else:
        st.write('Location not found.')
else:
    st.write('Please enter a valid API key and address.')