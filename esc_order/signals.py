from django.dispatch import Signal
import requests
from django.db import Q
from esc_hub.models import Hub


hub_exist_or_not_signal = Signal(providing_args=["order"])

def get_lat_lon(pincode):
    url = f"https://nominatim.openstreetmap.org/search?postalcode={pincode}&country=India&format=json"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; MyGeocoder/1.0)"
    }
    
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data:
            lat = data[0]["lat"]
            lon = data[0]["lon"]
            return lat, lon
        else:
            return "No data found for this PIN code"
    else:
        return f"Error: {response.status_code}"
    

@reciever(hub_exist_or_not_signal)
def hub_exist_or_not(sender, **kwargs):
    order = kwargs.get("order")
    
    buyer_hubs = Hub.objects.filter(
        Q(district=order.shipping_details.buyer_address.district) &
        Q(state=order.shipping_details.buyer_address.state)
    )
    
    seller_hubs = Hub.objects.filter(
        Q(district=order.shipping_details.seller_address.district) &
        Q(state=order.shipping_details.seller_address.state)
    )
    
    
    

    