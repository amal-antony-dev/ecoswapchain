from esc_order.serializer import OrderHubSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from esc_order.models import SwapOrder
from esc_user.serializer import EcoUserRetrieveSerializer
from esc_order.serializer import OrderHubSerializer
from .models import Hub
from .serializers import HubRetrieveSerializer
from esc_user.models import EcoUser
from rest_framework_simplejwt.tokens import RefreshToken

class HubLoginView(APIView):

    def post(self, request):
        try:
            email = request.data.get('email')
            password = request.data.get('password')
            if not EcoUser.objects.filter(email=email).exists():
                return Response({"message" : "User does not exist"}, status=status.HTTP_400_BAD_REQUEST)
            user = EcoUser.objects.get(email=email)
            if not user.check_password(password):
                return Response({"message" : "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)
            
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
        
            
            user_data = EcoUserRetrieveSerializer(user).data
            
            print(user_data)
            
            response = Response(
                {"token": access_token, "user": user_data},
                status=status.HTTP_201_CREATED,
            )

            # Set the refresh token in an HttpOnly cookie
            response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=True,  
            samesite="None",
            path="/",
            )

            return response
        except Exception as e:
            print(e)
            return Response(
                {"message": "Something went wrong on the server. Try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
   
         
class HubOrderRetrieveView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        try:
            hub = Hub.objects.get(manager=request.user)
            orders = SwapOrder.objects.filter(shipping_details__source_hub=hub)
            hub_serializer = HubRetrieveSerializer(hub, many=False)
            order_serializer = OrderHubSerializer(orders, many=True)
            return Response({"orders" : order_serializer.data, "hub" : hub_serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"error" : str(e)}, status=status.HTTP_400_BAD_REQUEST)
            

class ProductVerificationView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self, request):
        try:
            orderId = request.data.get("orderId")
            verificationStatus = request.data.get("verificationStatus")
            if not orderId:
                return Response({"error": "Missing orderId"}, status=status.HTTP_400_BAD_REQUEST)
            order = SwapOrder.objects.get(id=orderId)
            order.shipping_details.product_verified = verificationStatus
            order.shipping_details.save()
            return Response({"message": "Product verification status updated successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"error" : str(e)}, status=status.HTTP_400_BAD_REQUEST)

