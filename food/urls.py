from django.urls import path

from food.views import cart_view, checkout_view, home, product_detail

urlpatterns = [
    path("", home, name="home"),
    path("product/<int:pk>/", product_detail, name="product_detail"),
    path("cart/", cart_view, name="cart"),
    path("checkout/", checkout_view, name="checkout"),
]
