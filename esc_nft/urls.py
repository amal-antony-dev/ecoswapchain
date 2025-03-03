from django.urls import path
from .views import NFTCreateView, NFTMintView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("create/", NFTCreateView.as_view(), name="nft-create"),  # Create NFT
    path("mint/", NFTMintView.as_view(), name="nft-mint")
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)