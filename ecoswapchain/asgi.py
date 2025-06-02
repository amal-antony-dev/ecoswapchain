import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecoswapchain.settings")
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

import esc_order.routing
import esc_wallet.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            esc_order.routing.websocket_urlpatterns + esc_wallet.routing.websocket_urlpatterns
        )
    ),
})
