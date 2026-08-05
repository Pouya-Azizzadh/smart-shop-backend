from django.contrib import admin

from .models import NFCTag


@admin.register(NFCTag)
class NFCTagAdmin(admin.ModelAdmin):
    list_display = ("uuid", "basket_id", "assigned_product", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("basket_id", "uuid")
