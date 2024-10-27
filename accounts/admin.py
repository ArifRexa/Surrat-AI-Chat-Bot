from django.contrib import admin
from accounts.models import CustomUser
from bot.admin import AudioRequestInline


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    inlines = [AudioRequestInline]
    list_display = ('email',)
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'email', 'first_name', 'last_name')

