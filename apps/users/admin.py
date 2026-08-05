from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "wallet_balance", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("username", "email")
