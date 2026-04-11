# Register your models here.
from django.contrib import admin
from django.contrib.auth import get_user_model

from app.notification.models import Notification

User = get_user_model()

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


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    inlines = [NotificationInline]
