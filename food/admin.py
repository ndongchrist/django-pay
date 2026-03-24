from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "stock", "is_active"]
    list_filter = ["is_active", "stock"]
    search_fields = ["name", "description"]

    fieldsets = (
        ("Basic Info", {"fields": ("name", "description", "price", "image")}),
        ("Inventory", {"fields": ("stock", "is_active")}),
    )
