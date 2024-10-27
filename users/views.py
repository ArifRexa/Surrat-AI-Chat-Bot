from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from users.models import ChatHistory
from users.serializers import ChatHistorySerializer


# Create your views here.
class ChatHistoryListCreateView(generics.ListCreateAPIView):
    queryset = ChatHistory.objects.all()
    serializer_class = ChatHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
