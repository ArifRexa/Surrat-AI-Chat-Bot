from django.urls import path, re_path
from . import consumers

websocket_urlpatterns = [
    path('ws/sc/', consumers.MySyncConsumer.as_asgi()),
    path('ws/ac/', consumers.MyAsyncConsumer.as_asgi()),
    # re_path(r'/ws/audio/{user_id}/{page_number}/', consumers.TTSConsumer.as_asgi()),
]

# from django.urls import path
# from . import consumers
#
# websocket_urlpatterns = [
#     path('ws/chat/', consumers.ChatConsumer.as_asgi()),
# ]
