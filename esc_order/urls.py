from django.urls import path
from .views import OrderCreateView, OrderRetrieveView, MessageRetrieveView, OrderListView, OrderPriceUpdateView, OrderConfirmView, AddressCreateView, AddressUpdateView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('create/', OrderCreateView.as_view(), name='order-create'),
    path('list/', OrderListView.as_view(), name='order-list'),
    path('retrieve/<str:order_id>/', OrderRetrieveView.as_view(), name='order-retrieve'),
    path("update/<str:order_id>/price/", OrderPriceUpdateView.as_view(), name="order-price-update"),
    path("confirm/<str:order_id>/", OrderConfirmView.as_view(), name="order-confirm"),
    path("address/create/", AddressCreateView.as_view(), name="address-create"),
    path('retrieve/<str:order_id>/messages/', MessageRetrieveView.as_view(), name='message-retrieve'),
    path('update/address/<str:address_id>/', AddressUpdateView.as_view(), name="address-update"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)