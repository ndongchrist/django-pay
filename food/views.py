from django.shortcuts import render
from django.shortcuts import get_object_or_404

from food.models import Product


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
    return render(request, "public/checkout.html")
