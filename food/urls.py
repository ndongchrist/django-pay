from django.urls import path

from food.views import cart_view, checkout_view, home, process_checkout, product_detail

urlpatterns = [
    path("", home, name="home"),
    path("product/<int:pk>/", product_detail, name="product_detail"),
    path("cart/", cart_view, name="cart"),
    path("checkout/", checkout_view, name="checkout"),
    path("process-checkout/", process_checkout, name="process_checkout"),
]
