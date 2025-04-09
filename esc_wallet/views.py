from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializer import WalletRetrieveSerializer, WalletSerializer
from rest_framework.exceptions import NotFound
from esc_trader.models import Trader
from .models import Wallet
from esc_wallet.walletActions import transferFromTreasury 
from decouple import RepositoryEnv, Config
import requests

# Load environment variables

class WalletInitializeView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = WalletRetrieveSerializer

    def post(self, request):
        pubKey = request.data.get("public_key")
        wallet_serializer = WalletSerializer(data=request.data)

        if wallet_serializer.is_valid():
            wallet = wallet_serializer.save()
            wallet.refresh_from_db()  

            tx = transferFromTreasury(wallet, "REWARD", 100)

            trader = Trader.objects.get(eco_user=request.user)
            trader.wallet = wallet
            trader.save()
            
        else:
            return Response({"message": "Error creating wallet", "errors": wallet_serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)


        return Response({"transactionData": tx}, status=status.HTTP_200_OK)


class WalletRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = WalletRetrieveSerializer
    
    def get(self, request):
        try:
            trader = Trader.objects.get(eco_user=request.user)  # Get trader instance
            wallet = trader.wallet  # Get wallet field or related object
            
             
            return Response({"wallet": WalletRetrieveSerializer(wallet).data}, status=status.HTTP_200_OK)
        except NotFound as e:
            return Response({"message": "Wallet not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(str(e))
            return Response({"message": "Something went wrong on the server. Try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class WalletBalanceView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        try:
            trader = Trader.objects.get(eco_user=request.user)
            return Response({"balance" : trader.wallet.balance}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class NFTMintFeeTransferView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    
    def post(self, request):
        try:
            # Ensure "password" is provided in the request
            password = request.data.get("password")
            if not password:
                return Response({"error": "Password is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch trader associated with the authenticated user
            try:
                trader = Trader.objects.get(eco_user=request.user)
            except ObjectDoesNotExist:
                return Response({"error": "Trader profile not found."}, status=status.HTTP_404_NOT_FOUND)

            # Ensure trader has a wallet
            if not hasattr(trader, 'wallet'):
                return Response({"error": "Trader wallet not found."}, status=status.HTTP_404_NOT_FOUND)

            # Validate password for wallet access
            file_path = "/media/alastor/New Volume/EcoSwapChain/ESC-Backend/swap-server/ecoswapchain/configure .env"  # Ensure there's no space in ".env"
            env_config = Config(RepositoryEnv(file_path))
            if trader.wallet.check_key(password):
                return Response(
                    {"treasuryKey": "6iPxdjHimmNrLemHX7RX6NwvEJiBAaChVLA9ivQtUy3b", "encKey": trader.wallet.private_key, 
                     "rpcUrl" : env_config.get('devnet_url'), 
                     "mintAddress" : env_config.get('token_mint_address')},
                    status=status.HTTP_200_OK
                )
            else:
                return Response({"error": "Invalid password."}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({"error": "An unexpected error occurred.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AirDropView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def transfer(self, pubKey, amount):
        """
        Transfers tokens to the specified public key.

        Args:
            pubKey (str): The recipient's public key.
            amount (float): The amount of tokens to transfer.

        Returns:
            tuple: (success: bool, message: str)
                - success: True if the transfer was successful, False otherwise.
                - message: A descriptive message about the result.
        """
        try:
            # Input validation
            if not pubKey or not isinstance(pubKey, str):
                return False, "Invalid public key."
            if not isinstance(amount, (int, float)) or amount <= 0:
                return False, "Amount must be a positive number."

            # Prepare the request data
            data = {
                "publicKey": pubKey,
                "amount": amount
            }
            

            # Make the HTTP POST request
            response = requests.post("http://localhost:3000/airdrop/transfer", json=data)

            # Check the response status code
            if response.status_code == 200:
                # Success
                return True, "Transfer successful."
            elif response.status_code == 400:
                # Client error (e.g., invalid input)
                return False, f"Client error: {response.json().get('message', 'Invalid request')}"
            elif response.status_code == 500:
                # Server error
                return False, f"Server error: {response.json().get('message', 'Internal server error')}"
            else:
                # Handle other status codes
                return False, f"Unexpected response: {response.status_code}"

        except requests.exceptions.RequestException as e:
            # Handle network-related errors (e.g., connection issues)
            return False, f"Network error: {str(e)}"
        except Exception as e:
            # Handle any other unexpected errors
            return False, f"Unexpected error: {str(e)}"

    def post(self, request):
        try:
            # Ensure "password" is provided in the request
            password = request.data.get("password")
            need = request.data.get("need")
            publicKey = request.data.get("publicKey")
            if not password:
                return Response({"error": "Password is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch trader associated with the authenticated user
            try:
                trader = Trader.objects.get(eco_user=request.user)
            except ObjectDoesNotExist:
                return Response({"error": "Trader profile not found."}, status=status.HTTP_404_NOT_FOUND)
            
            if not (trader.wallet.check_key(password)):
                return Response({"error": "Invalid password."}, status=status.HTTP_403_FORBIDDEN)
            
            amount = 0
            if need == "mint":
                amount = 250000
            
            result, message = self.transfer(publicKey, amount)
            if result:
                return Response({"message": message}, status=status.HTTP_200_OK)
            else:                
                return Response({"message": message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:            
            return Response({"error": "An unexpected error occurred.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        
              
        
class SwapCoinPurchaseView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self, request, *args, **kwargs):
            user_wallet_address = request.data.get("user_wallet_address")  # Get user wallet address
            amount = request.data.get("amount")  # Amount in USD (e.g., $50)
            
            print(request.data)

            if not user_wallet_address or not amount:
                return Response({"error": "Wallet address and amount are required."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                amount = float(amount)
                print(amount)
                wallet = Wallet.objects.get(public_key=user_wallet_address)
                if wallet:
                    tx = transferFromTreasury(wallet, "BUY", amount)
                    return Response({"transactionData": tx}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Wallet not found."}, status=status.HTTP_404_NOT_FOUND)
                
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            