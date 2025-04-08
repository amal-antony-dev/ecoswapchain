from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from esc_trader.models import Trader
from .models import SwapOrder, ShippingDetails, Address
from .serializer import OrderSerializer, MessageSerializer, OrderListSerializer, AddressSerializer
from esc_nft.models import NFT
from django.db.models import Q
from django.db import transaction
import uuid
import random
import string
from datetime import datetime
from esc_hub.models import Hub
from .signals import order_creation_signal, map_number_signal
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from esc_transaction.serializer import TokenTransactionCreationSerializer
# Create your views here.

channel_layer = get_channel_layer()

class AddressCreateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self, request):
        try:
            print(request.data)
            address = request.data.get("address")
            trader = Trader.objects.get(eco_user=request.user)
            address_serializer = AddressSerializer(data=address)
            if address_serializer.is_valid():
                address = address_serializer.save()
                address.trader = trader
                address.save()
                map_number_signal.send(sender = self, address = address)
                return Response(data={"address" : address_serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return Response(data={"message": address_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Trader.DoesNotExist:
            return Response(data={"message": "Trader does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(data={"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
class AddressUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def put(self, request, address_id):
        try:
            address = Address.objects.get(id=address_id)
            address_serializer = AddressSerializer(address, data=request.data)
            if address_serializer.is_valid():
                address_serializer.save()
                return Response(data={"message": "Address Updated Successfully"}, status=status.HTTP_200_OK)
            else:
                return Response(data={"message": address_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Trader.DoesNotExist:
            return Response(data={"message": "Trader does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(data={"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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
                seller=nft.owner,
                price=nft.price
            )
            
            shipping_details = ShippingDetails.objects.create()
            shipping_details.buyer_address = Address.objects.filter(trader=trader, default=True).first()
            shipping_details.seller_address = Address.objects.filter(trader=nft.owner, default=True).first()
            shipping_details.save()
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
            
            order.price = request.data.get("price")
            order.save()
            async_to_sync(channel_layer.group_send)(
                f'order_{order.id}',
                {
                    'type' : 'update_price',
                    'updated_price' : order.price
                }
            )
            return Response({"message" : "Order price updated successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"error" : str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
class OrderConfirmView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def put(self, request, order_id):
        if not order_id:
            return Response({"error": "orderId is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = SwapOrder.objects.get(id=order_id)
        except SwapOrder.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            if order.buyer.eco_user == request.user:
                # Buyer confirmation
                order.shipping_details.shipping_confirmed_by_buyer = True
                order.shipping_details.save()
                async_to_sync(channel_layer.group_send)(
                    f'order_{order.id}',
                    {
                        'type' : 'buyer_confirmation'
                    }
                )
                return Response({"message": "Buyer confirmed shipping details successfully"}, status=status.HTTP_200_OK)
            elif order.seller.eco_user == request.user:
                # Seller confirmation
                order.shipping_details.shipping_confirmed_by_seller = True
                order.status = "confirmed"
                order.shipping_details.save()
                order.save()
                async_to_sync(channel_layer.group_send)(
                    f'order_{order.id}',
                    {
                        'type' : 'buyer_confirmation'
                    }
                )
                order_creation_signal.send(sender=self, order=order)

                return Response({"message": "Seller confirmed shipping details successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"message" : "You are not authorized to perform this action"}, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            print(e)
            return Response({"error": f"Failed to confirm shipping: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InitEscrowView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            tx = request.data.get("tx")
            amount = request.data.get("amount")
            trader_id = request.data.get("traderId")
            order_id = request.data.get("orderId")
            trader = Trader.objects.get(id=trader_id)
            order = SwapOrder.objects.get(id=order_id)
            transactionData = {
                    "transaction_hash": tx,
                    "amount": amount,
                    "transfered_from": Trader.objects.get(eco_user=request.user).wallet.pk,
                    "transfered_to": trader.wallet.pk,
                    "transaction_type": "ESCROW",
                    "status": "HOLD"
                }

            transaction_serializer = TokenTransactionCreationSerializer(data=transactionData)
            if transaction_serializer.is_valid():
                transaction = transaction_serializer.save()
                order.escrow_transaction = transaction
                order.payment_status = "escrow"
                order.save()
            else:
                print(transaction_serializer.errors)
                raise ValidationError(transaction_serializer.errors)
        except exception as e:
            return Response({"error": "Missing transaction hash"}, status=status.HTTP_400_BAD_REQUEST)

                
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