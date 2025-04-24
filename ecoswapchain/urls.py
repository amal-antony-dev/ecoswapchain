from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', include('esc_admin.urls')),
    path('django-admin/', admin.site.urls),
    path('trader/', include('esc_trader.urls')),
    path('verification/', include('esc_verification.urls')),
    path('auth/', include('esc_user.urls')),
    path('wallet/', include('esc_wallet.urls')),
    path('nfts/', include('esc_nft.urls')),
    path('product/', include('esc_product.urls')),
    path('order/', include('esc_order.urls')),
    path('hub/', include('esc_hub.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
