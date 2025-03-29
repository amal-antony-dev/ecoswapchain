from django.urls import path
from .views import NFTCreateView, NFTMintView, DeleteNFTObjectView, OwnedNFTListView, NFTListView, NFTRetrieveView, NFTActivateView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("create/", NFTCreateView.as_view(), name="nft-create"),  # Create NFT
    path("mint/", NFTMintView.as_view(), name="nft-mint"),
    path("owner/list/", OwnedNFTListView.as_view(), name="owned-list"),
    path("del/object/<int:nftId>/", DeleteNFTObjectView.as_view(), name="del-object-nft"),
    path('list/all/', NFTListView.as_view(), name='nft-list-all'),
    path('retrieve/<int:nftId>/', NFTRetrieveView.as_view(), name='nft-retrieve'),
    path('activate/<int:nftId>/', NFTActivateView.as_view(), name='nft-activate'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)