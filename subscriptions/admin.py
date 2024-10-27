from django.contrib import admin
from .models import Subscription, UserSubscription

# admin.site.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_filter = ('duration_days', 'price', 'name')
    search_fields = ('name',)

admin.site.register(Subscription, SubscriptionAdmin)

# admin.site.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'subscription', 'start_date', 'end_date')
    readonly_fields = ('end_date',)
    list_filter = ('user', 'subscription', 'start_date', 'end_date')

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields
        return self.readonly_fields


admin.site.register(UserSubscription, UserSubscriptionAdmin)
