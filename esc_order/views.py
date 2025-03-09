from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from esc_trader.models import Trader
from .models import SwapOrder
from .serializer import OrderSerializer, MessageSerializer, OrderListSerializer
from esc_nft.models import NFT
from django.db.models import Q

# Create your views here.

class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self, request):
        try:
            nft_id = request.data.get("nftId")
            
            trader = Trader.objects.get(eco_user=request.user)
            nft = NFT.objects.get(id=nft_id)
            
 
            order = SwapOrder.objects.create(
                item=nft,
                buyer=trader,
                seller=nft.owner
            )
            
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