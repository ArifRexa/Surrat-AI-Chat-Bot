from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_message = models.TextField()
    bot_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email}: {self.user_message[:50]} - {self.bot_reply[:50]}"
