import random
from django.utils import timezone
from datetime import timedelta
from django.conf import settings


def generate_otp():
    return str(random.randint(100000, 999999))


def set_otp(user):
    otp = generate_otp()
    user.otp = otp
    opt_expiration_time = int(getattr(settings, 'OTP_EXPIRATION_TIME', 5))
    user.otp_expiration = timezone.now() + timedelta(minutes=opt_expiration_time)
    user.save()
    return otp
