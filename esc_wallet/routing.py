from django.urls import re_path
from . import consumer

websocket_urlpatterns = [
    re_path(r"^ws/transaction/(?P<public_key>[^/]+)/$", consumer.WalletConsumer.as_asgi()),
]
