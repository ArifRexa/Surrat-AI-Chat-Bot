from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import ChatHistory

User = get_user_model()


class UserEmailFilter(admin.SimpleListFilter):
    title = "User Email"
    parameter_name = "user_email"

    def lookups(self, request, model_admin):
        users = set(chat.user for chat in model_admin.model.objects.all())
        return [(user.email, user.email) for user in users]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user__email=self.value())
        return queryset


class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ("user", "user_message", "bot_reply", "created_at")
    list_filter = (UserEmailFilter,)
    ordering = ("-created_at",)
    search_fields = ("user__email", "user_message", "bot_reply")


admin.site.register(ChatHistory, ChatHistoryAdmin)


# class ChatHistoryInline(admin.TabularInline):
#     model = ChatHistory
#     extra = 0
#     readonly_fields = ('user_message', 'bot_reply', 'created_at')
#
#
# class CustomUserAdmin(admin.ModelAdmin):
#     inlines = [ChatHistoryInline]
#
#
# # Re-register the User model with the custom admin
# admin.site.unregister(User)
# admin.site.register(User, CustomUserAdmin)
