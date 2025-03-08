from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
import json
from .models import NFT
from esc_product.models import Product, ProductImage, RootCategory, MainCategory
from .serializer import NFTSerializer, ProductSerializer, NFTListSerializer, NFTDetailSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from esc_trader.models import Trader
from .uploadImage import get_uri
from .mintNFT import mint
from esc_transaction.serializer import TokenTransactionCreationSerializer
from esc_product.models import Materials, Certification

class NFTCreateView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            request_data = request.data.copy()
            
            print(request_data)
            # Extract and validate product data
            product_data = request_data.pop("product", None)
            if not product_data:
                return Response({"error": "Product data is required."}, status=status.HTTP_400_BAD_REQUEST)

            if isinstance(product_data, list):
                if not product_data:
                    return Response({"error": "Product data cannot be an empty list."}, status=status.HTTP_400_BAD_REQUEST)
                product_data = product_data[0]

            if isinstance(product_data, str):
                try:
                    product_data = json.loads(product_data)
                except json.JSONDecodeError:
                    return Response({"error": "Invalid JSON format for product."}, status=status.HTTP_400_BAD_REQUEST)

            if not isinstance(product_data, dict):
                return Response({"error": "Product data must be a dictionary."}, status=status.HTTP_400_BAD_REQUEST)

            # Validate and save product
            certificate_data = product_data.pop("certifications", [])
            materials_data = product_data.pop("materialsUsed", [])
            additionalMaterials = product_data.pop("additionalMaterials", [])
            
            
            product_serializer = ProductSerializer(data=product_data)
            if not product_serializer.is_valid():
                return Response(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            product = product_serializer.save()
            
            product.additional_materials = additionalMaterials
            
            for certificate in certificate_data:
                Certification.objects.create(product=product, **certificate)
            for material in materials_data:
                m, created = Materials.objects.get_or_create(name=material)
                product.materials.add(m)
            product.save()

            # Handle features (JSONField)
            features = product_data.get("features", "[]")
            
            if isinstance(features, str):
                try:
                    features = json.loads(features)
                except json.JSONDecodeError:
                    return Response({"error": "Invalid JSON format for features."}, status=status.HTTP_400_BAD_REQUEST)
            
            product.features = features  # Assign parsed JSON list

            # Assign root and main categories
            root, _ = RootCategory.objects.get_or_create(name=product_data['rootCategory']['name'])
            main, _ = MainCategory.objects.get_or_create(name=product_data["mainCategory"]["name"])
            
            product.rootCategory = root
            product.mainCategory = main
            product.save()

            # Extract additional images
            additional_images = [
                file for key, file in request.FILES.items() if "product[additionalImages]" in key
            ]

            # Remove additional images from request.FILES
            for key in list(request.FILES.keys()):
                if "product[additionalImages]" in key:
                    del request_data[key]

            # Save additional images
            for image in additional_images:
                ProductImage.objects.create(product=product, image=image)
                
            print(request_data)
     
            nft_serializer = NFTSerializer(data=request_data)
            if not nft_serializer.is_valid():
                print(nft_serializer.errors)
                return Response({"error": nft_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            nft = nft_serializer.save()
            nft.owner = Trader.objects.get(eco_user=request.user)
            nft.product = product
            nft.save()

            return Response({"NFT": NFTSerializer(nft, many=False).data}, status=status.HTTP_201_CREATED)


        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NFTMintView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self, request):
        try:
            nft_id = request.data.get("id")
            txHash = request.data.get("txHash")
            
            print(request.data)
            
            if not txHash:
                return Response({"message": "Missing Transaction Signature"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not nft_id:
                return Response({"message": "Missing NFT ID"}, status=status.HTTP_400_BAD_REQUEST)
            
            nft = None
            
            # Check if NFT exists and belongs to the authenticated user
            print(nft_id)
            try:
                trader = Trader.objects.get(eco_user=request.user)
                print(trader.id)
                nft = NFT.objects.get(id=nft_id, owner=trader)
                print(nft.id)
                print(nft.owner.wallet.pk)
                transactionData = {
                    "transaction_hash": txHash,
                    "amount": 20,
                    "transfered_from": nft.owner.wallet.pk,
                    "transaction_type": "FEE",
                    "status": "CONFIRMED"
                }

                transaction_serializer = TokenTransactionCreationSerializer(data=transactionData)
                if transaction_serializer.is_valid():
                    transaction_serializer.save()
                else:
                    print(transaction_serializer.errors)
                    raise ValidationError(transaction_serializer.errors)
            except Exception as e:
                print(str(e))
                return Response({"message": "NFT not found"}, status=status.HTTP_404_NOT_FOUND)

            # Get and update the NFT URI
            try:
                uri = get_uri(nft)
                nft.uri = uri["uri"]
                nft.save()
            except Exception as e:
                return Response({"message": f"Error generating URI: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Mint the NFT
            try:
                tx = mint(nft)
                if tx is not None:
                    print("NFT data: ", tx)
                    return Response({"tx" : {
                    "txHash" : tx["txHash"], "mintAddress" : tx["mintAddress"]}}, status=status.HTTP_200_OK)
            except Exception as e:
                print(str(e))
                return Response({"message": f"Error minting NFT: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        except Exception as e:
            print(str(e))
            return Response({"message": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
        
class DeleteNFTObjectView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def delete(self, request, nftId):
        try:
            nft = NFT.objects.get(pk=nftId)
            if not nft.status:
                nft.delete()
                return Response({"message" : "Successfully Deleted"}, status=status.HTTP_200_OK)
            else:
                return Response({"message" : "Cannot delete a verified Asset"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class OwnedNFTListView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        try:
            nfts = NFT.objects.filter(owner__eco_user=request.user)  # ✅ Use filter() to get multiple NFTs
            
            if not nfts.exists():  # ✅ Handle case where user has no NFTs
                return Response({"message": "No NFTs found"}, status=status.HTTP_404_NOT_FOUND)

            nft_serializer = NFTListSerializer(nfts, many=True)  # ✅ Correct serializer usage
            return Response({"nfts": nft_serializer.data}, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(e)
            return Response({"message": f"Internal Server Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
              
class NFTListView(APIView):
    
    def get(self, request):
        try:
            nfts = NFT.objects.filter(status=True)
            nft_serializer = NFTListSerializer(nfts, many=True)
            return Response({"nfts": nft_serializer.data}, status=status.HTTP_200_OK)
        except Exception as e: 
            print(e)
            return Response({"message": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        

class NFTRetrieveView(APIView):
    def get(self, request, nftId):
        try:
            nft = NFT.objects.get(pk=nftId)
            nft_serializer = NFTDetailSerializer(nft)
            return Response({"nft": nft_serializer.data}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"message": "NFT not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({"message": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)