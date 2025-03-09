from django.urls import path
from .views import OrderCreateView, OrderRetrieveView, MessageRetrieveView, OrderListView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('create/', OrderCreateView.as_view(), name='order-create'),
    
    path('list/', OrderListView.as_view(), name='order-list'),
    path('retrieve/<str:order_id>/', OrderRetrieveView.as_view(), name='order-retrieve'),

    path('retrieve/<str:order_id>/messages/', MessageRetrieveView.as_view(), name='message-retrieve'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)