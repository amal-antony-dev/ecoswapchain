import requests
import json
from .utils import get_lat_lon
from .models import Address
import os



def map_number(addressPk):
    
    district_number_map = {}
    
    address = Address.objects.get(pk=addressPk)
    
    # Get the directory where the current file lives
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Build the full path to the JSON file
    json_path = os.path.join(BASE_DIR, 'district_number_map.json')

    
    with open(json_path, 'r') as f:
        district_number_map = json.load(f)
        
    address.district_number = district_number_map["district_number_map"][address.district]
    lat, lon = get_lat_lon(address.postal_code)
    address.latitude = lat
    address.longitude = lon
    address.save()