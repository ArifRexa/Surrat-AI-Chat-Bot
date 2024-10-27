from django.contrib import admin
from .models import audio_to_text
# Register your models here.

@admin.register(audio_to_text)
class AudioToTextAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'transcribed_text')
    search_fields = ('user__email', 'transcribed_text')
    list_filter = ('created_at', 'user')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'user')

    def get_readonly_fields(self, request, obj=None):
        """Make the 'transcribed_text' field read-only if the object exists."""
        if obj:
            return self.readonly_fields + ('transcribed_text',)
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        """Automatically set the logged-in user as the 'user' and save the model."""
        if not obj.pk:  # Only set the user if this is a new object
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def get_fields(self, request, obj=None):
        """Remove the 'user' field from the admin form."""
        fields = super().get_fields(request, obj)
        if not obj:
            fields.remove('user')  # Remove 'user' field when adding a new object
        return fields

    def get_queryset(self, request):
        """Limit the queryset to only show the logged-in user's content."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # Allow superusers to see all content
        return qs.filter(user=request.user)

    def has_change_permission(self, request, obj=None):
        """Restrict the change permission to the object's owner."""
        if obj and obj.user != request.user:
            return False  # Prevent users from editing others' content
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        """Restrict the delete permission to the object's owner."""
        if obj and obj.user != request.user:
            return False  # Prevent users from deleting others' content
        return super().has_delete_permission(request, obj)
