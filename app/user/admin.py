from django.contrib import admin

from app.notification.models import Notification
from app.user.models import CustomUser

admin.site.register(Notification)


class NotificationInline(admin.TabularInline):
    model = Notification
    fields = [
        "message",
        "is_read",
        "created_at",
    ]
    readonly_fields = [
        "created_at",
    ]
    extra = 1


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("email", "nickname", "is_active", "is_staff", "is_delete")
    search_fields = ("email", "nickname")
    list_filter = ("is_active", "is_staff", "is_delete")

    inlines = [NotificationInline]
