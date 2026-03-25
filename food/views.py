import json
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from food.enum import OrderStatus
from food.models import Order, OrderItem, Product


def home(request):
    # Only show active products that are in stock
    products = Product.objects.filter(is_active=True, stock__gt=0).order_by("-id")[:8]

    context = {
        "products": products,
    }
    return render(request, "public/index.html", context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)

    # Related products (same style as homepage)
    related_products = Product.objects.filter(is_active=True, stock__gt=0).exclude(id=product.id)[:4]

    context = {
        "product": product,
        "related_products": related_products,
    }
    return render(request, "public/product_detail.html", context)


def cart_view(request):
    return render(request, "public/cart.html")


def checkout_view(request):
    """Display the checkout / order confirmation page"""
    order = None
    order_items = []

    # Try to get the most recent order for this user (or latest order)
    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user).order_by("-created_at").first()
    else:
        # For guest users - get the very latest order (you can improve this later with session)
        order = Order.objects.order_by("-created_at").first()

    if order:
        order_items = order.items.all()  # using related_name="items"

    context = {
        "order": order,
        "order_items": order_items,
        "total": order.total_amount if order else 0,
    }
    return render(request, "public/checkout.html", context)


@csrf_exempt  # We'll use CSRF token from JS for safety
def process_checkout(request):
    """Create Order + OrderItems from frontend cart JSON"""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid method"}, status=405)

    try:
        data = json.loads(request.body)
        cart_items = data.get("cart", [])

        if not cart_items:
            return JsonResponse({"success": False, "error": "Cart is empty"}, status=400)

        # Calculate total
        total_amount = 0
        order_items_to_create = []

        for item in cart_items:
            product = get_object_or_404(Product, id=item["id"], is_active=True)

            if product.stock < item["quantity"]:
                return JsonResponse({"success": False, "error": f"Not enough stock for {product.name}"}, status=400)

            subtotal = product.price * item["quantity"]
            total_amount += subtotal

            order_items_to_create.append(
                {
                    "product": product,
                    "quantity": item["quantity"],
                    "price": product.price,  # snapshot price at time of order
                }
            )

        # Create Order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            total_amount=total_amount,
            status=OrderStatus.PENDING,
            # payment_reference will be filled after successful payment
        )

        # Create OrderItems
        for item_data in order_items_to_create:
            OrderItem.objects.create(
                order=order, product=item_data["product"], quantity=item_data["quantity"], price=item_data["price"]
            )

        # Optional: reduce stock (uncomment when ready)
        # for item_data in order_items_to_create:
        #     item_data['product'].stock -= item_data['quantity']
        #     item_data['product'].save()

        # Clear frontend cart after successful order creation
        # (we'll tell JS to do it)

        return JsonResponse({"success": True, "order_id": order.id, "total": str(total_amount)})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
