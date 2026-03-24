from django.shortcuts import render

from food.models import Product


def home(request):
    # Only show active products that are in stock
    products = Product.objects.filter(is_active=True, stock__gt=0).order_by("-id")[:8]

    context = {
        "products": products,
    }
    return render(request, "public/index.html", context)
