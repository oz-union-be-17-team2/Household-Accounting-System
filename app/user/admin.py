from django.contrib import admin

from app.user.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("email", "nickname", "is_active", "is_staff", "is_delete")
    search_fields = ("email", "nickname")
    list_filter = ("is_active", "is_staff", "is_delete")
