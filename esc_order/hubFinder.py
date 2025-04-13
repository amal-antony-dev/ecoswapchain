from esc_hub.models import Hub
from esc_hub.serializers import HubRetrieveSerializer
import json
import os
from .utils import get_lat_lon, get_distance 
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from esc_order.models import SwapOrder


def findHub(orderId, **kwargs):
    channel_layer = get_channel_layer()



    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Build the full path to the JSON file
    json_path = os.path.join(BASE_DIR, 'district_number_map.json')

    # Load district adjacency data
    with open(json_path, 'r') as f:
        district_neighbours = json.load(f)
        
    order = SwapOrder.objects.get(id=orderId)

    # Get district numbers for seller and buyer
    seller_address_num = order.shipping_details.seller_address.district_number
    buyer_address_num = order.shipping_details.buyer_address.district_number
    
    visited = set()

    print(f"[DEBUG] Seller district: {seller_address_num}, Buyer district: {buyer_address_num}")

    # Get coordinates for distance calculations
    seller_lat, seller_lon = get_lat_lon(order.shipping_details.seller_address.postal_code)
    buyer_lat, buyer_lon = get_lat_lon(order.shipping_details.buyer_address.postal_code)

    # Initialize distance tracking
    distances = {
        'source': {'hub': None, 'distance': float('inf')},
        'destination': {'hub': None, 'distance': float('inf')},
        'direct_distance': get_distance(seller_lat, seller_lon, buyer_lat, buyer_lon)
    }
    
    sourceHub = None
    destinationHub = None

    print(f"[DEBUG] Direct distance between seller and buyer: {distances['direct_distance']}")

    # Case 1: Same district
    if seller_address_num == buyer_address_num:
        print("[DEBUG] Seller and buyer are in the same district")
        visited.add(order.shipping_details.seller_address.district)
        for hub in Hub.objects.filter(district=order.shipping_details.seller_address.district):
            hub_distance = get_distance(seller_lat, seller_lon, hub.latitude, hub.longitude)
            print(f"[DEBUG] Checking seller hub: {hub.id}, Distance: {hub_distance}")
            if hub_distance < distances['source']['distance']:
                distances['source']['hub'] = hub
                distances['source']['distance'] = hub_distance

        for hub in Hub.objects.filter(district=order.shipping_details.buyer_address.district):
            hub_distance = get_distance(buyer_lat, buyer_lon, hub.latitude, hub.longitude)
            print(f"[DEBUG] Checking buyer hub: {hub.id}, Distance: {hub_distance}")
            if hub_distance < distances['destination']['distance']:
                distances['destination']['hub'] = hub
                distances['destination']['distance'] = hub_distance

        total_hub_route = distances['source']['distance'] + distances['destination']['distance']
        print(f"[DEBUG] Total hub route distance: {total_hub_route}")


        if distances['source']['hub'] and distances['destination']['hub']:
            total_hub_route = distances['source']['distance'] + distances['destination']['distance']
            print(f"[DEBUG] Final hub route distance: {total_hub_route}")

            if total_hub_route < distances['direct_distance']:
                print("[DEBUG] Using hub-based swap shipping.")
                order.shipping_details.source_hub = distances["source"]["hub"]
                order.shipping_details.destination_hub = distances["destination"]["hub"]
                sourceHub = HubRetrieveSerializer(order.shipping_details.source_hub).data
                destinationHub = HubRetrieveSerializer(order.shipping_details.destination_hub).data
                order.shipping_details.shipping_method = "swap"
            else:
                print("[DEBUG] Using self-shipping (direct route is better).")
                order.shipping_details.shipping_method = "self"
        else:
            print("[DEBUG] No hubs found in district. Using self-shipping.")
            order.shipping_details.shipping_method = "self"

        order.shipping_details.save()

        print(f"[DEBUG] Final shipping method: {order.shipping_details.shipping_method}")
        print(f"[DEBUG] Source Hub: {sourceHub}")
        print(f"[DEBUG] Destination Hub: {destinationHub}")

        async_to_sync(channel_layer.group_send)(
            f"order_{order.id}", 
            {
                "type": "order_update",
                "shippingMethod": order.shipping_details.shipping_method,
                "sourceHub": sourceHub,
                "destinationHub": destinationHub,
            }
        )
        
        return


    # Case 2: Different districts
    print("[DEBUG] Seller and buyer are in different districts")
    
    print(district_neighbours["district_adjacency_graph"][str(order.shipping_details.seller_address.district)])
    print(district_neighbours["district_adjacency_graph"][str(order.shipping_details.buyer_address.district)])
    
    seller_neighbours = district_neighbours["district_adjacency_graph"][str(order.shipping_details.seller_address.district)]
    buyer_neighbours = district_neighbours["district_adjacency_graph"][str(order.shipping_details.buyer_address.district)]

    if seller_address_num > buyer_address_num:
        for hub in Hub.objects.filter(district=order.shipping_details.seller_address.district):
            hub_distance = get_distance(seller_lat, seller_lon, hub.latitude, hub.longitude)
            print(f"[DEBUG] Checking seller hub: {hub.id}, Distance: {hub_distance}")
            if hub_distance < distances['source']['distance']:
                distances['source']['hub'] = hub
                distances['source']['distance'] = hub_distance
                
        for hub in Hub.objects.filter(district=order.shipping_details.buyer_address.district):
            hub_distance = get_distance(buyer_lat, buyer_lon, hub.latitude, hub.longitude)
            print(f"[DEBUG] Checking buyer hub: {hub.id}, Distance: {hub_distance}")
            if hub_distance < distances['destination']['distance']:
                distances['destination']['hub'] = hub   
                distances['destination']['distance'] = hub_distance
                
        for neighbour in seller_neighbours:
            if int(neighbour) < seller_address_num:
                for hub in Hub.objects.filter(district=district_neighbours["number_district_map"][str(neighbour)]):
                    hub_distance = get_distance(seller_lat, seller_lon, hub.latitude, hub.longitude)
                    print(f"[DEBUG] Seller neighbor hub: {hub.id}, Distance: {hub_distance}")
                    if hub_distance < distances['source']['distance']:
                        distances['source']['hub'] = hub
                        distances['source']['distance'] = hub_distance

        for neighbour in buyer_neighbours:
            if int(neighbour) > buyer_address_num:
                for hub in Hub.objects.filter(district=district_neighbours["number_district_map"][str(neighbour)]):
                    hub_distance = get_distance(buyer_lat, buyer_lon, hub.latitude, hub.longitude)
                    print(f"[DEBUG] Buyer neighbor hub: {hub.id}, Distance: {hub_distance}")
                    if hub_distance < distances['destination']['distance']:
                        distances['destination']['hub'] = hub
                        distances['destination']['distance'] = hub_distance

    elif seller_address_num < buyer_address_num:
        
        for hub in Hub.objects.filter(district=order.shipping_details.seller_address.district):
            hub_distance = get_distance(seller_lat, seller_lon, hub.latitude, hub.longitude)
            print(f"[DEBUG] Checking seller hub: {hub.id}, Distance: {hub_distance}")
            if hub_distance < distances['source']['distance']:
                distances['source']['hub'] = hub
                distances['source']['distance'] = hub_distance
                
        for hub in Hub.objects.filter(district=order.shipping_details.buyer_address.district):
            hub_distance = get_distance(buyer_lat, buyer_lon, hub.latitude, hub.longitude)
            print(f"[DEBUG] Checking buyer hub: {hub.id}, Distance: {hub_distance}")
            if hub_distance < distances['destination']['distance']:
                distances['destination']['hub'] = hub   
                distances['destination']['distance'] = hub_distance
        
        for neighbour in seller_neighbours:
            if int(neighbour) > seller_address_num:
                for hub in Hub.objects.filter(district=district_neighbours["number_district_map"][str(neighbour)]):
                    hub_distance = get_distance(seller_lat, seller_lon, hub.latitude, hub.longitude)
                    print(f"[DEBUG] Seller neighbor hub: {hub.id}, Distance: {hub_distance}")
                    if hub_distance < distances['source']['distance']:
                        distances['source']['hub'] = hub
                        distances['source']['distance'] = hub_distance

        for neighbour in buyer_neighbours:
            if int(neighbour) < buyer_address_num:
                for hub in Hub.objects.filter(district=district_neighbours["number_district_map"][str(neighbour)]):
                    hub_distance = get_distance(buyer_lat, buyer_lon, hub.latitude, hub.longitude)
                    print(f"[DEBUG] Buyer neighbor hub: {hub.id}, Distance: {hub_distance}")
                    if hub_distance < distances['destination']['distance']:
                        distances['destination']['hub'] = hub
                        distances['destination']['distance'] = hub_distance

    # Final decision
    sourceHub = None
    destinationHub = None

    if distances['source']['hub'] and distances['destination']['hub']:
        total_hub_route = distances['source']['distance'] + distances['destination']['distance']
        print(f"[DEBUG] Final hub route distance: {total_hub_route}")

        if total_hub_route < distances['direct_distance']:
            print("[DEBUG] Using hub-based swap shipping.")
            order.shipping_details.source_hub = distances["source"]["hub"]
            order.shipping_details.destination_hub = distances["destination"]["hub"]
            sourceHub = HubRetrieveSerializer(order.shipping_details.source_hub).data
            destinationHub = HubRetrieveSerializer(order.shipping_details.destination_hub).data
            order.shipping_details.shipping_method = "swap"
        else:
            print("[DEBUG] Using self-shipping (direct route is better).")
            order.shipping_details.shipping_method = "self"
    else:
        print("[DEBUG] No hubs found in neighboring districts. Using self-shipping.")
        order.shipping_details.shipping_method = "self"

    order.shipping_details.save()

    print(f"[DEBUG] Final shipping method: {order.shipping_details.shipping_method}")
    print(f"[DEBUG] Source Hub: {sourceHub}")
    print(f"[DEBUG] Destination Hub: {destinationHub}")

    async_to_sync(channel_layer.group_send)(
        f"order_{order.id}", 
        {
            "type": "order_update",
            "shippingMethod": order.shipping_details.shipping_method,
            "sourceHub": sourceHub,
            "destinationHub": destinationHub,
        }
    )
