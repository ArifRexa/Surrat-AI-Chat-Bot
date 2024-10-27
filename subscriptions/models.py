from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model


User = get_user_model()


class Subscription(models.Model):
    DURATION_CHOICES = [
        (1, "Free"),
        (5, "5 Minutes"),
        (30, "1 Month"),
        (90, "3 Months"),
        (180, "6 Months"),
        (365, "1 Year"),
    ]

    name = models.CharField(max_length=100)
    duration_days = models.IntegerField(choices=DURATION_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=False, null=False)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()

    @property
    def is_active(self):
        return self.end_date > timezone.now()

    def renew(self):
        is_subscription_active = self.is_active
        self.start_date = timezone.now()
        if self.subscription.duration_days == 5:
            self.end_date = self.start_date + timedelta(minutes=5)
        else:
            self.end_date = self.start_date + timedelta(
                days=self.subscription.duration_days
            )

        self.save()

    def save(self, *args, **kwargs):
        if not self.start_date:
            self.start_date = timezone.now()

        if self.subscription.duration_days == 5:
            self.end_date = self.start_date + timedelta(minutes=5)
        else:
            self.end_date = self.start_date + timedelta(
                days=self.subscription.duration_days
            )

        super(UserSubscription, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - {self.subscription.name}"
