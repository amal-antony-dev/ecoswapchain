from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"^ws/chat/(?P<order_id>[0-9a-fA-F-]+)/$", consumers.ChatConsumer.as_asgi()),
    re_path(r"^ws/updates/(?P<order_id>[0-9a-fA-F-]+)/$", consumers.OrderConsumer.as_asgi()),
]
