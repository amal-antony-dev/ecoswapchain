from esc_hub.models import Hub
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAdminUser
from esc_hub.serializers import HubSerializer, HubRetrieveSerializer, RouteSerializer
from esc_user.serializer import EcoUserRetrieveSerializer
from esc_user.models import EcoUser
from esc_hub.models import Route



class AdminLoginView(APIView):
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
            

class HubCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def post(self, request):
        try:
            print(request.data)
            hub_serializer = HubSerializer(data=request.data)
            if not hub_serializer.is_valid():
                return Response({"message": hub_serializer.errors[list(hub_serializer.errors.keys())[0]][0]}, status=status.HTTP_400_BAD_REQUEST) 
            hub_serializer.save()
            return Response({"message" : "Hub creation Successful"}, status=status.HTTP_201_CREATED)
        except Exception as e:  
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class AdminHubListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            hubs = Hub.objects.all()
            serializer = HubRetrieveSerializer(hubs, many=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class AdminRouteAddView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def post(self, request):
        print("\n=== Starting route creation ===")
        try:
            data = request.data["newPath"]
            print(f"Received data: {data}")
            
            if not isinstance(data, list):
                print("ERROR: Expected list but got:", type(data))
                return Response(
                    {"error": "Payload must be a list of edges"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            routes = []
            error_count = 0

            for i, edge in enumerate(data):
                print(f"\nProcessing edge #{i+1}: {edge}")
                
                try:
                    # Validate edge structure
                    if 'fromNode' not in edge or 'to' not in edge:
                        print(f"ERROR: Edge missing 'from' or 'to' fields")
                        error_count += 1
                        continue

                    from_id = edge['fromNode'].get('id')
                    to_id = edge['to'].get('id')
                    
                    if not from_id or not to_id:
                        print(f"ERROR: Missing hub IDs in edge")
                        error_count += 1
                        continue

                    print(f"Looking for hubs - From: {from_id}, To: {to_id}")
                    source_hub = Hub.objects.filter(id=from_id).first()
                    dest_hub = Hub.objects.filter(id=to_id).first()

                    if not source_hub:
                        print(f"ERROR: Source hub {from_id} not found")
                    if not dest_hub:
                        print(f"ERROR: Destination hub {to_id} not found")
                    
                    if source_hub and dest_hub:
                        print("Both hubs found, creating route...")
                        route = Route(source=source_hub, destination=dest_hub)
                        route.save()
                        routes.append(route)
                        print(f"Successfully created route ID: {route.id}")
                    else:
                        error_count += 1

                except Exception as e:
                    print(f"ERROR processing edge #{i+1}: {str(e)}")
                    error_count += 1

            print(f"\n=== Summary ===")
            print(f"Total edges processed: {len(data)}")
            print(f"Successfully created: {len(routes)}")
            print(f"Errors encountered: {error_count}")

            if error_count == 0:
                return Response(
                    {"message": "All routes created successfully", "count": len(routes)},
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {
                        "message": f"Created {len(routes)} routes with {error_count} errors",
                        "success_count": len(routes),
                        "error_count": error_count
                    },
                    status=status.HTTP_207_MULTI_STATUS
                )

        except Exception as e:
            print("\n=== FATAL ERROR ===")
            print(f"Unexpected error: {str(e)}")
            print("Full traceback:")
            import traceback
            traceback.print_exc()
            
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            

class AdminRouteListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            print("got in")
            routes = Route.objects.all()
            route_serializer = RouteSerializer(routes, many=True)
            return Response(route_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

