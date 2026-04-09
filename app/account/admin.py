# Register your models here.
from django.contrib import admin

from app.account.models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin): ...
