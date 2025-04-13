from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from math import radians, sin, cos, sqrt, atan2
from math import inf


def get_lat_lon(pincode, country='India'):
    try:
        geolocator = Nominatim(user_agent="ecoswap_locator")
        location = geolocator.geocode(f"{pincode}, {country}")
        if location:
            return location.latitude, location.longitude
    except GeocoderTimedOut:
        return get_lat_lon(pincode, country)  # Retry on timeout
    return None, None

def get_distance(lat1, lon1, lat2, lon2):
    # Radius of the Earth in km
    R = 6371.0

    # Convert degrees to radians
    lat1_r = radians(lat1)
    lon1_r = radians(lon1)
    lat2_r = radians(lat2)
    lon2_r = radians(lon2)

    # Haversine formula
    dlon = lon2_r - lon1_r
    dlat = lat2_r - lat1_r

    a = sin(dlat / 2)**2 + cos(lat1_r) * cos(lat2_r) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance