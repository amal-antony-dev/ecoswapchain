from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import HubLoginView, ProductVerificationView, HubOrderRetrieveView

urlpatterns = [
    path("login/", HubLoginView.as_view(), name="hub-login"),
    path("order/list/", HubOrderRetrieveView.as_view(), name="order-list"),
    path("product/verify/", ProductVerificationView.as_view(), name="product-verification"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)