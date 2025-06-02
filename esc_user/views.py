from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import EcoUser
from .serializer import EcoUserRetrieveSerializer

class TokenUpdateView(APIView):
    def post(self, request):
            refresh_token = request.COOKIES.get("refresh_token")
            if not refresh_token:
                print("Refresh token missing")
                return Response({"message": "Refresh token missing"}, status=status.HTTP_401_UNAUTHORIZED)
            try:
                refresh = RefreshToken(refresh_token)
                access_token = str(refresh.access_token)
                response = Response({"access_token": access_token}, status=status.HTTP_200_OK)
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
                print(str(e))
                return Response({"message": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

            
class CheckUser(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        print(request.user)
        try:
            user_data = EcoUserRetrieveSerializer(request.user).data
            return Response(user_data, status=status.HTTP_200_OK)
        
        except AuthenticationFailed:
            return Response({
                "message": "Unauthorized"
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        except Exception as e:
            return Response({
                "message": "Internal server error"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




        except Exception as e:
            print("OAuth2 Callback Error:", str(e))
            return Response({"message": "OAuth2 callback error", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        
class LogoutView(APIView):
    def post(self, request):
        response = Response({"message": "Logged out"}, status=status.HTTP_200_OK)
        response.delete_cookie("refresh_token")  # Remove refresh token cookie
        return response


