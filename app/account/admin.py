# Register your models here.
from django.contrib import admin

from app.account.models import Account, BalanceAlert


class BalanceAlertInline(admin.TabularInline):
    model = BalanceAlert
    extra = 0
    readonly_fields = ["threshold", "created_at"]


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    inlines = [
        BalanceAlertInline,
    ]
