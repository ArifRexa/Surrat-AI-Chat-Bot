from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from .models import Subscription, UserSubscription


# class SubscriptionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Subscription
#         fields = ["id", "name", "duration_days", "price"]
#
#
# # class UserSubscriptionSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = UserSubscription
# #         fields = ['id', 'user', 'subscription', 'start_date', 'end_date']
#
# # class UserSubscriptionSerializer(serializers.ModelSerializer):
# #     email = serializers.EmailField(source='user.email', read_only=True)
# #     subscription_name = serializers.CharField(source='subscription.name', read_only=True)
# #     duration = serializers.IntegerField(source='subscription.duration_days', read_only=True)
# #     price = serializers.DecimalField(source='subscription.price', max_digits=10, decimal_places=2, read_only=True)
# #
# #     class Meta:
# #         model = UserSubscription
# #         fields = ['email', 'subscription_name', 'duration', 'price', 'start_date', 'end_date']
#
#
# class CreateUserSubscriptionSerializer(serializers.ModelSerializer):
#     subscription_name = serializers.CharField(source="subscription.name")
#
#     class Meta:
#         model = UserSubscription
#         fields = ["subscription_name"]
#
#     def create(self, validated_data):
#         subscription_name = validated_data.pop("subscription")["name"]
#         subscription = get_object_or_404(Subscription, name=subscription_name)
#         user_subscription = UserSubscription.objects.create(
#             subscription=subscription, **validated_data
#         )
#         return user_subscription
#
#
# class UserSubscriptionSerializer(serializers.ModelSerializer):
#     email = serializers.EmailField(source="user.email", read_only=True)
#     subscription_name = serializers.CharField(source="subscription.name")
#     duration = serializers.IntegerField(
#         source="subscription.duration_days", read_only=True
#     )
#     price = serializers.DecimalField(
#         source="subscription.price", max_digits=10, decimal_places=2, read_only=True
#     )
#
#     class Meta:
#         model = UserSubscription
#         fields = [
#             "email",
#             "subscription_name",
#             "duration",
#             "price",
#             "start_date",
#             "end_date",
#         ]
#
#     # def create(self, validated_data):
#     #     subscription_name = validated_data.pop('subscription')['name']
#     #     subscription = get_object_or_404(Subscription, name=subscription_name)
#     #     user_subscription = UserSubscription.objects.create(subscription=subscription, **validated_data)
#     #     return user_subscription
#
#
class RenewSubscriptionSerializer(serializers.Serializer):
    subscription_id = serializers.IntegerField()

    def validate_subscription_id(self, value):
        """
        Check if the provided subscription_id exists in the Subscription model.
        """
        if not Subscription.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid subscription plan.")
        return value


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ["id", "name", "duration_days", "price"]


class UserSubscriptionSerializer(serializers.ModelSerializer):
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = UserSubscription
        fields = ["id", "user", "subscription", "start_date", "end_date", "is_active"]
        read_only_fields = ["user", "start_date", "end_date", "is_active"]

    def get_is_active(self, obj) -> bool:
        return obj.is_active

    def create(self, validated_data):
        subscription = validated_data["subscription"]
        user_subscription = UserSubscription.objects.create(**validated_data)
        user_subscription.save()
        return user_subscription
