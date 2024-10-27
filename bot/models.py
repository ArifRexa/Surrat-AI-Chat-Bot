from django.core.exceptions import ValidationError
from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class AudioRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    page_number = models.PositiveIntegerField(null=True, blank=True)
    audio = models.FileField(upload_to="audio/", null=True, blank=True)
    response_audio = models.FileField(upload_to="audio/", null=True, blank=True)
    instruction = models.TextField(null=True, blank=True)
    transcribed_text = models.TextField(blank=True, null=True)
    translated_text = models.TextField(blank=True, null=True)
    gpt_response = models.TextField(blank=True, null=True)
    translated_response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # request_count = models.PositiveIntegerField(default=0)
    # # daily_request_count = models.PositiveIntegerField(default=0)  # Track daily requests
    # last_request_at = models.DateTimeField(default=timezone.now, null=True, blank=True)  # Track last request time

    # def reset_daily_request_count(self):
    #     if self.last_request_at and self.last_request_at < timezone.now() - timedelta(days=1):
    #         self.daily_request_count = max(self.daily_request_count - 1, 0)
    #         self.save()

    def __str__(self):
        return f"Request by {self.user.email} on {self.created_at}"



class RequestCounter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    page_number = models.PositiveIntegerField()
    request_count = models.PositiveIntegerField(default=0)
    last_request_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    # def update_request_count(self):
    #     current_time = timezone.now()
    #     if self.last_request_at:
    #         time_since_last_request = current_time - self.last_request_at
    #         if time_since_last_request.days >= 1:
    #             # Reset or decrease request count based on the days passed
    #             self.request_count = max(int(self.request_count) - time_since_last_request.days, 0)
    #     else:
    #         self.request_count = 0  # First time request handling case
    #     self.last_request_at = current_time
    #     self.request_count += 1
    #     self.save()


class instruction_per_page(models.Model):
    page_number = models.PositiveIntegerField(unique=True, null=True, blank=True)
    instruction_text = models.TextField(null=True, blank=True)
    instruction_image = models.ImageField(upload_to='instructions/', null=True, blank=True)

    def __str__(self):
        return f"Page {self.page_number}"

    # def clean(self):
    #     super().clean()
    #     if not self.instruction_text and not self.instruction_image:
    #         raise ValidationError("You must provide either an instruction text or an instruction image.")
    #     if self.instruction_text and self.instruction_image:
    #         raise ValidationError("You can only provide either an instruction text or an instruction image, not both.")
