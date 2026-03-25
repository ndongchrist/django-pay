from django.contrib import admin
from .models import Product, Order, OrderItem, Payment


class OrderItemInline(admin.TabularInline):
    """Inline for Order Items – clean tabular view inside Order admin"""

    model = OrderItem
    extra = 0  # Don't show empty extra rows by default
    readonly_fields = ("price",)  # Price should not be editable after order is placed
    raw_id_fields = ("product",)  # Better UX when you have many products


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total_amount", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("id", "user__username", "user__email")
    readonly_fields = ("total_amount", "created_at")
    ordering = ("-created_at",)

    # Show OrderItems inline
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product", "quantity", "price", "get_subtotal")
    list_filter = ("order__status",)
    search_fields = ("order__id", "product__name")
    readonly_fields = ("price",)

    def get_subtotal(self, obj):
        return obj.quantity * obj.price

    get_subtotal.short_description = "Subtotal"
    get_subtotal.admin_order_field = "price"  # Allows sorting


# Optional: Register Product and Payment too for completeness
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "stock", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "method", "amount", "status", "created_at")
    list_filter = ("method", "status")
    search_fields = ("order__id", "transaction_id")
