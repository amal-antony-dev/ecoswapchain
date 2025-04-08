from rest_framework import generics, status
from rest_framework.response import Response
from .models import Trader
from .serializer import TraderRegistrationSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from .serializer import TraderRetrieveSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

class TraderRegistrationView(generics.CreateAPIView):
    """
    View for registering a trader (creates User, EcoUser, and Trader instances)
    """
    queryset = Trader.objects.all()
    serializer_class = TraderRegistrationSerializer

    def create(self, request, *args, **kwargs):
        try:
            # Validate and save the trader instance
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            trader = serializer.save()

            # Generate JWT tokens for the newly created user
            refresh = RefreshToken.for_user(trader.eco_user)
            access_token = str(refresh.access_token)

            # Use a separate serializer for the response
            trader_data = EcoUserRetrieveSerializer(trader.eco_user).data

            

            # Prepare the response
            response = Response(
                {"token": access_token, "user": trader_data},
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
            # Handle unexpected errors
            print(e)
            return Response(
                {"message": "Something went wrong on the server. Try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TraderLoginView(APIView):
    def post(self, request):
        try:
            email = request.data['email']
            password = request.data['password']
            print(email)
            if Trader.objects.filter(eco_user__email=email).exists():
                trader = Trader.objects.get(eco_user__email=email)
                if trader.eco_user.check_password(password):
                    refresh = RefreshToken.for_user(trader.eco_user)
                    access_token = str(refresh.access_token)
                    trader_data = EcoUserRetrieveSerializer(trader.eco_user).data

                    response = Response({"token": access_token, "user" : trader_data}, status=status.HTTP_200_OK)

                    response.set_cookie(
                    key="refresh_token",
                    value=str(refresh),
                    httponly=True,
                    secure=True,  
                    samesite="None",
                    path="/",
                )

                    return response
                else: 
                    return Response({
                        "message": "Invalid credentials"
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    "message": "Trader does not exist"
                }, status=status.HTTP_404_NOT_FOUND)
        except KeyError as e:
            return Response({
                "message": "Missing key"
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({
                "message": "Something went wrong on the server. Try again later."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class TraderRetrieveView(APIView):
    """
    View for retrieving a trader's details
    """
    permision_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        try:
            trader = TraderRetrieveSerializer(Trader.objects.filter(eco_user=request.user).first()).data
            return Response({"trader" : trader}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"error" : str(e)}, status=status.HTTP_400_BAD_REQUEST)