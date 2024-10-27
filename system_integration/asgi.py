"""
ASGI config for system_integration project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

# import os
# import bot.routing
# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'system_integration.settings')
#
# # application = get_asgi_application()
# application = ProtocolTypeRouter({
#     'http': get_asgi_application(),
#     'websocket': URLRouter(
#         bot.routing.websocket_urlpatterns
#     )
# })
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
 # Import your app's routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'system_integration.settings')
print(os.environ.get("DJANGO_SETTINGS_MODULE"))

asgi_app = get_asgi_application()

from bot import routing

application = ProtocolTypeRouter({
    "http": asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})

