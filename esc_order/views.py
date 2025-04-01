from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from esc_trader.models import Trader
from .models import SwapOrder, ShippingDetails
from .serializer import OrderSerializer, MessageSerializer, OrderListSerializer, AddressSerializer
from esc_nft.models import NFT
from django.db.models import Q
from django.db import transaction
import uuid
import random
import string
from datetime import datetime
from esc_hub.models import Hub
# Create your views here.

class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self, request):
        try:
            nft_id = request.data.get("nftId")
            
            trader = Trader.objects.get(eco_user=request.user)
            nft = NFT.objects.get(id=nft_id)
            nft.in_processing = True
            nft.save()
            
 
            order = SwapOrder.objects.create(
                item=nft,
                buyer=trader,
                seller=nft.owner
            )
            
   
            shipping_details = ShippingDetails.objects.create()
            order.shipping_details = shipping_details
            order.save()
            
            return Response({"orderId" : order.id}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response({"error" : str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class OrderListView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        try:
            orders = SwapOrder.objects.filter(
                Q(buyer__eco_user=request.user) | Q(seller__eco_user=request.user)
            )

            return Response({"orders" : OrderListSerializer(orders, many=True).data}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"error" : str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class OrderRetrieveView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, order_id):
        try:
            order = SwapOrder.objects.get(id=order_id)
            return Response({"order" : OrderSerializer(order).data}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"error" : str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
        
class OrderPriceUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def put(self, request, order_id):
        try:
            order = SwapOrder.objects.get(id=order_id)
            if order.seller.eco_user != request.user:
                return Response({"error" : "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
            
            order.item.price = request.data.get("price")
            order.item.save()
            order.save()
            return Response({"message" : "Order price updated successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"error" : str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        

class OrderAddressUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def generate_tracking_number(self, prefix="TR"):
        """
        Generates a unique tracking number.

        Args:
            prefix (str): A prefix for the tracking number (e.g., "TR" for "Tracking").

        Returns:
            str: A unique tracking number in the format: <PREFIX>-<TIMESTAMP>-<RANDOM_CHARS>-<UUID_SHORT>
                Example: "TR-20231025-ABC7X-9B4F"
        """
        # Get the current timestamp in YYYYMMDD format
        timestamp = datetime.now().strftime("%Y%m%d")

        # Generate 4 random uppercase letters
        random_chars = ''.join(random.choices(string.ascii_uppercase, k=4))

        # Generate a short UUID (first 8 characters of a UUID4)
        short_uuid = str(uuid.uuid4()).replace("-", "")[:8]

        # Combine all parts into a tracking number
        tracking_number = f"{prefix}-{timestamp}-{random_chars}-{short_uuid}"

        return tracking_number

    @transaction.atomic   
    def put(self, request, order_id):
        try:
            # Fetch the order and check if it exists
            order = SwapOrder.objects.filter(id=order_id).first()
            if not order:
                return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

            # Validate and save the address
            address_data = request.data.get("address")
            if not address_data:
                return Response({"error": "Address data is required"}, status=status.HTTP_400_BAD_REQUEST)

            address_serializer = AddressSerializer(data=address_data)
            if not address_serializer.is_valid():
                return Response({"error": address_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the trader associated with the user
            try:
                trader = Trader.objects.get(eco_user=request.user)
            except Trader.DoesNotExist:
                return Response({"error": "Trader not found for the current user"}, status=status.HTTP_404_NOT_FOUND)

            # Save the address with the trader
            address = address_serializer.save()
            address.trader = trader
            address.save()

            # Determine if the user is the seller or buyer
            is_seller = order.seller.eco_user == request.user

            if is_seller:
                order.shipping_details.seller_address = address
                order.shipping_details.shipping_confirmed_by_seller = True
                if not order.shipping_details.shipping_method == "self":
                    if Hub.objects.filter(
                        Q(district=order.shipping_details.seller_address.district) &
                        Q(state=order.shipping_details.seller_address.state)
                    ).exists():
                        order.shipping_details.shipping_method = "swap"
                        order.shipping_details.tracking_number = self.generate_tracking_number()
                    else:
                        order.shipping_details.shipping_method = "self"
                order.status = "confirmed"
                order.save()
            else:
                order.shipping_details.buyer_address = address
                order.shipping_details.shipping_confirmed_by_buyer = True
                if Hub.objects.filter(
                    Q(district=order.shipping_details.buyer_address.district) &
                    Q(state=order.shipping_details.buyer_address.state)
                ).exists():
                    order.shipping_details.shipping_method = "swap"
                else:
                    order.shipping_details.shipping_method = "self"
    

            order.shipping_details.save()
            if is_seller:
                return Response({"trackingNumber" : order.shipping_details.tracking_number, 
                                 "shippingMethod" : order.shipping_details.shipping_method
                                 }, status=status.HTTP_201_CREATED)
            else:   
                return Response({"message": "Address updated successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            # Rollback the transaction in case of an error
            transaction.set_rollback(True)
            # Log the error for debugging purposes
            print(f"Error: {e}")
            return Response({"error": "An error occurred while updating the address"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
                
class MessageRetrieveView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, order_id):
        try:
            order = SwapOrder.objects.get(id=order_id)
            messages = order.messages.all()
            return Response({"messages" : MessageSerializer(messages, many=True).data}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"error" : str(e)}, status=status.HTTP_400_BAD_REQUEST)