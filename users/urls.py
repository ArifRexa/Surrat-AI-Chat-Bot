from django.urls import path
from .views import ChatHistoryListCreateView

urlpatterns = [
    path('chat-history/', ChatHistoryListCreateView.as_view(), name='chat-history'),
]
