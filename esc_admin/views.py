from esc_hub.models import Hub
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAdminUser
from esc_hub.serializers import HubSerializer

class AdminLoginView(APIView):
    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            if not EcoUser.objects.filter(username=username).exists():
                return Response({"message" : "User does not exist"}, status=status.HTTP_400_BAD_REQUEST)
            user = EcoUser.objects.get(username=username)
            if not user.check_password(password):
                return Response({"message" : "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)
            
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            
            user_data = {
                role: user.role,
                email: user.email,
            }
            
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

class HubCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def post(self, request):
        try:
            hub_serializer = HubSerializer(data=request.data)
            if not hub_serializer.is_valid():
                hub_serializer.save()
                return Response({"message" : "Hub creation Failed"}, status=status.HTTP_400_BAD_REQUEST)
            hub_serializer.save()
            return Response({"message" : "Hub creation Successful"}, status=status.HTTP_201_CREATED)
        except Exception as e:  
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)