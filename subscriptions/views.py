from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.views import APIView

from .models import Subscription, UserSubscription
from .serializers import (
    SubscriptionSerializer,
    UserSubscriptionSerializer,
    # CreateUserSubscriptionSerializer,
    RenewSubscriptionSerializer,
)
from django.shortcuts import get_object_or_404
from django.utils import timezone


# @login_required
# def subscribe(request, subscription_id):
#     subscription = get_object_or_404(Subscription, pk=subscription_id)
#     user_subscription = UserSubscription(user=request.user, subscription=subscription)
#     user_subscription.save()
#     return redirect("subscription_success")
#
#
# @login_required
# # @subscription_required
# def subscription_success(request):
#     return render(request, "subscription_success.html")
#
#
# class SubscriptionListView(generics.ListAPIView):
#     queryset = Subscription.objects.all()
#     serializer_class = SubscriptionSerializer
#     permission_classes = [AllowAny]
#     # permission_classes = [IsAdminUser]
#
#
# class UserSubscriptionCreateView(generics.CreateAPIView):
#     serializer_class = CreateUserSubscriptionSerializer
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request, *args, **kwargs):
#         subscription_name = request.data.get("subscription_name")
#         subscription = get_object_or_404(Subscription, name=subscription_name)
#         user_subscription = UserSubscription(
#             user=request.user, subscription=subscription, start_date=timezone.now()
#         )
#         user_subscription.save()
#         return Response(
#             UserSubscriptionSerializer(user_subscription).data,
#             status=status.HTTP_201_CREATED,
#         )
#
#
# class UserSubscriptionListView(generics.ListAPIView):
#     serializer_class = UserSubscriptionSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         return UserSubscription.objects.filter(user=self.request.user)
#
#
# def subscription_required(request):
#     return render(request, "subscription_required.html")
#
#
# class RenewSubscriptionView(APIView):
#     serializer_class = RenewSubscriptionSerializer
#
#     def post(self, request, *args, **kwargs):
#         serializer = RenewSubscriptionSerializer(data=request.data)
#         if serializer.is_valid():
#             user_subscription = UserSubscription.objects.get(user=request.user)
#             # Check if the current subscription is expired
#             if user_subscription.is_active:
#                 return Response(
#                     {"message": "Your subscription is still active."},
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )
#
#             # Get new subscription ID from the validated data
#             new_subscription_id = serializer.validated_data["subscription_id"]
#             new_subscription = Subscription.objects.get(id=new_subscription_id)
#
#             # Renew the subscription
#             user_subscription.renew(new_subscription)
#
#             return Response(
#                 {"message": "Subscription renewed successfully"},
#                 status=status.HTTP_200_OK,
#             )
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         # try:
#         #     user_subscription = UserSubscription.objects.get(user=request.user)
#         # except UserSubscription.DoesNotExist:
#         #     return Response({"error": "Subscription not found"}, status=status.HTTP_404_NOT_FOUND)
#         #
#         # # Check if the current subscription is expired
#         # if user_subscription.is_active:
#         #     return Response({"message": "Your subscription is still active."}, status=status.HTTP_400_BAD_REQUEST)
#         #
#         # # Get new subscription ID from the request
#         # new_subscription_id = request.data.get('subscription_id')
#         # try:
#         #     new_subscription = Subscription.objects.get(id=new_subscription_id)
#         # except Subscription.DoesNotExist:
#         #     return Response({"error": "Invalid subscription plan"}, status=status.HTTP_400_BAD_REQUEST)
#         #
#         # # Renew the subscription
#         # user_subscription.renew(new_subscription)
#         #
#         # return Response({"message": "Subscription renewed successfully"}, status=status.HTTP_200_OK)


# Subscription List and Detail Views
class SubscriptionListView(generics.ListCreateAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]


class SubscriptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]


# User Subscription Views
class UserSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSubscriptionSerializer

    def get(self, request):
        user_subscription = UserSubscription.objects.filter(user=request.user).first()
        if not user_subscription:
            return Response(
                {"detail": "No subscription found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserSubscriptionSerializer(user_subscription)
        return Response(serializer.data)

    def post(self, request):
        user_subscription = UserSubscription.objects.filter(user=request.user).first()

        if user_subscription and user_subscription.is_active:
            serializer = UserSubscriptionSerializer(user_subscription)
            return Response(
                {
                    "detail": "You already have an active subscription. Please cancel your current subscription before subscribing to a new one.",
                    "subscription": serializer.data,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user_subscription and not user_subscription.is_active:
            user_subscription.delete()

        serializer = UserSubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RenewSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = None

    def post(self, request):
        user_subscription = UserSubscription.objects.filter(user=request.user).first()
        if not user_subscription:
            return Response(
                {"detail": "No subscription found."}, status=status.HTTP_404_NOT_FOUND
            )

        # new_subscription_id = request.data.get("subscription")
        # try:
        #     new_subscription = Subscription.objects.get(id=new_subscription_id)
        # except Subscription.DoesNotExist:
        #     return Response(
        #         {"detail": "Subscription plan not found."},
        #         status=status.HTTP_404_NOT_FOUND,
        #     )

        user_subscription.renew()
        return Response({"detail": "Subscription renewed successfully."})


class CancelSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = None

    def post(self, request):
        user_subscription = UserSubscription.objects.filter(user=request.user).first()
        print(user_subscription)
        if not user_subscription:
            return Response(
                {"detail": "No subscription found."}, status=status.HTTP_404_NOT_FOUND
            )

        user_subscription.delete()
        return Response(
            {"detail": "Subscription canceled successfully."},
            status=status.HTTP_202_ACCEPTED,
        )
