"""
ASGI config for ecoswapchain project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import esc_order.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecoswapchain.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            esc_order.routing.websocket_urlpatterns
        )
    ),
})
