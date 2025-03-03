from django.urls import path
from .views import WalletRetrieveView, WalletInitializeView, WalletBalanceView, NFTMintFeeTransferView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('retrieve/', WalletRetrieveView.as_view(), name='wallet-retrieve'),
    path('reward/' , WalletInitializeView.as_view(), name="waller-init"),
    path('balance/', WalletBalanceView.as_view(), name="wallet-balance"),
    path('mintFee/tx/init', NFTMintFeeTransferView.as_view(), name="mint-fee-tx")
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)