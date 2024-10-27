# from functools import wraps
# from django.shortcuts import redirect
# from .models import UserSubscription
#
#
# def subscription_required(view_func):
#     @wraps(view_func)
#     def _wrapped_view(request, *args, **kwargs):
#         if request.user.is_authenticated:
#             try:
#                 user_subscription = UserSubscription.objects.get(user=request.user)
#                 if not user_subscription.is_active:
#                     return redirect('subscription_required')
#             except UserSubscription.DoesNotExist:
#                 return redirect('subscription_required')
#         return view_func(request, *args, **kwargs)
#
#     return _wrapped_view
