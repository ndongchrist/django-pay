from django.urls import path

from food.views import (
    cart_view,
    checkout_view,
    home,
    initiate_moneroo_payment,
    initiate_payunit_payment,
    moneroo_success,
    payunit_cancel,
    payunit_notify,
    payunit_success,
    process_checkout,
    product_detail,
)

urlpatterns = [
    path("", home, name="home"),
    path("product/<int:pk>/", product_detail, name="product_detail"),
    path("cart/", cart_view, name="cart"),
    path("checkout/", checkout_view, name="checkout"),
    path("process-checkout/", process_checkout, name="process_checkout"),
    # payment(payunit) related URLs
    path("payunit/initiate/<int:order_id>/", initiate_payunit_payment, name="payunit_initiate"),
    path("payunit/success/<int:order_id>/", payunit_success, name="payunit_success"),
    path("payunit/cancel/<int:order_id>/", payunit_cancel, name="payunit_cancel"),
    path("payunit/notify/", payunit_notify, name="payunit_notify"),
    # moneroo related URLs
    path("moneroo/initiate/<int:order_id>/", initiate_moneroo_payment, name="moneroo_initiate"),
    path("moneroo/success/", moneroo_success, name="moneroo_success"),
]
