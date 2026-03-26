import json
import uuid

from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from payUnit import payUnit

from food.flutterwave import FlutterwavePayment
from food.paypal import PayPalPayment
from .models import Order, Payment
from django.conf import settings

from food.enum import OrderStatus
from .moneroo import MonerooPayment
from .stripe import StripePayment
from food.models import Order, OrderItem, Product  # noqa: F811


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


def initiate_payunit_payment(request, order_id):
    """Initiate PayUnit payment from checkout page"""
    order = get_object_or_404(Order, id=order_id)

    # Generate unique transaction_id
    transaction_id = f"PLATE-{order.id}-{uuid.uuid4().hex[:8]}"

    # For local development: Use ngrok (example below)
    # Replace with your actual ngrok URL when running
    base_url = (
        "https://8813-2605-59c0-1e9e-a908-778c-c77f-9ce0-861d.ngrok-free.app"  # ← CHANGE THIS EVERY TIME NGROK RESTARTS
    )

    success_url = base_url + reverse("payunit_success", args=[order.id])
    cancel_url = base_url + reverse("payunit_cancel", args=[order.id])  # noqa: E221 F841
    notify_url = base_url + reverse("payunit_notify")  # noqa: E221

    try:
        payment = payUnit(
            {
                "apiUsername": settings.PAYUNIT_CONFIG["apiUsername"],
                "apiPassword": settings.PAYUNIT_CONFIG["apiPassword"],
                "api_key": settings.PAYUNIT_CONFIG["api_key"],
                "return_url": success_url,  # PayUnit calls this after payment
                "notify_url": notify_url,
                "mode": settings.PAYUNIT_CONFIG["mode"],
                "name": "Platē Studio",
                "description": f"Order #{order.id} - Premium Dinnerware",
                "purchaseRef": f"ORD-{transaction_id}",
                "currency": "XAF",
                "transaction_id": transaction_id,
            }
        )

        # This will redirect the user to PayUnit payment page
        response = payment.makePayment(float(order.total_amount))

        # Save payment reference
        Payment.objects.create(
            order=order, method="payunit", amount=order.total_amount, transaction_id=transaction_id, status="pending"
        )

        # Update order with reference
        order.payment_reference = transaction_id
        order.save()

        return redirect(response)  # redirect to PayUnit hosted page

    except Exception as e:
        return HttpResponse(f"Payment initiation failed: {str(e)}", status=500)


@csrf_exempt
def payunit_success(request, order_id):
    """User lands here after successful payment"""
    order = get_object_or_404(Order, id=order_id)

    # Update status
    order.status = OrderStatus.PAID if hasattr(OrderStatus, "PAID") else "PAID"
    order.save()

    # Optional: Update Payment model
    payment = Payment.objects.filter(order=order, method="payunit").first()
    if payment:
        payment.status = "success"
        payment.save()

    context = {"order": order, "message": "Payment Successful! Thank you for your purchase.", "method": "PayUnit"}
    return render(request, "public/payment_success.html", context)


@csrf_exempt
def payunit_cancel(request, order_id):
    """User cancelled the payment"""
    order = get_object_or_404(Order, id=order_id)
    context = {"order": order, "message": "Payment was cancelled. You can try again."}
    return render(request, "public/payment_cancel.html", context)


@csrf_exempt
def payunit_notify(request):
    """Webhook from PayUnit (recommended to verify status)"""
    # PayUnit will POST here with payment result
    # For now, just log it. You can improve later to verify via status API.
    print("PayUnit Webhook received:", request.POST)
    return HttpResponse("OK", status=200)


def initiate_moneroo_payment(request, order_id):
    """Initialize Moneroo payment"""
    order = get_object_or_404(Order, id=order_id)

    moneroo = MonerooPayment()
    result = moneroo.initialize_payment(order, request)

    if result["success"]:
        return redirect(result["checkout_url"])
    else:
        return HttpResponse(f"Payment initialization failed: {result['error']}", status=400)


def moneroo_success(request):
    """Handle return from Moneroo after payment"""
    order_id = request.GET.get("order_id")
    payment_status = request.GET.get("paymentStatus")  # Moneroo usually sends this
    payment_id = request.GET.get("paymentId")

    order = get_object_or_404(Order, id=order_id)

    # You should verify the payment status properly (via webhook or retrieve API)
    # For now, we mark as paid if they returned from success flow
    if payment_status and payment_status.lower() == "success":
        order.status = OrderStatus.PAID if hasattr(OrderStatus, "PAID") else "PAID"
        order.save()

        Payment.objects.create(
            order=order,
            method="moneroo",
            amount=order.total_amount,
            status="success",
            transaction_id=payment_id or order.payment_reference,
        )

        return render(request, "public/payment_success.html", {"order": order, "method": "Moneroo"})

    # If status is not clearly success, show cancel/failed page
    return render(request, "public/payment_cancel.html", {"order": order})


def initiate_stripe_payment(request, order_id):
    """Initialize Stripe Checkout Session"""
    order = get_object_or_404(Order, id=order_id)

    stripe_payment = StripePayment()
    result = stripe_payment.initialize_payment(order, request)

    if result["success"]:
        return redirect(result["checkout_url"])
    else:
        return HttpResponse(f"Stripe payment initialization failed: {result['error']}", status=400)


def stripe_success(request):
    """Handle return from Stripe after successful payment"""
    order_id = request.GET.get("order_id")
    session_id = request.GET.get("session_id")

    order = get_object_or_404(Order, id=order_id)

    # In production, you should verify the session with Stripe API
    # For now, we optimistically mark as paid (improve later with webhook)
    order.status = OrderStatus.PAID if hasattr(OrderStatus, "PAID") else "PAID"
    order.save()

    Payment.objects.create(
        order=order, method="stripe", amount=order.total_amount, status="success", transaction_id=session_id
    )

    return render(request, "public/payment_success.html", {"order": order, "method": "Stripe"})


def stripe_cancel(request):
    """Handle cancelled Stripe payment"""
    order_id = request.GET.get("order_id")
    order = get_object_or_404(Order, id=order_id)

    return render(request, "public/payment_cancel.html", {"order": order})


def initiate_paypal_payment(request, order_id):
    """Initialize PayPal payment"""
    order = get_object_or_404(Order, id=order_id)

    paypal_payment = PayPalPayment()
    result = paypal_payment.initialize_payment(order, request)

    if result["success"]:
        return redirect(result["approval_url"])
    else:
        return HttpResponse(f"PayPal payment initialization failed: {result.get('error')}", status=400)


def paypal_success(request):
    """Handle return from PayPal after approval"""
    order_id = request.GET.get("order_id")
    payment_id = request.GET.get("paymentId")
    # payer_id = request.GET.get('PayerID')

    order = get_object_or_404(Order, id=order_id)

    # In a real implementation, you should execute the payment here
    # For simplicity now, we mark as paid (improve with execute() later)
    order.status = OrderStatus.PAID if hasattr(OrderStatus, "PAID") else "PAID"
    order.save()

    # Create Payment record
    Payment.objects.create(
        order=order, method="paypal", amount=order.total_amount, status="success", transaction_id=payment_id
    )

    return render(request, "public/payment_success.html", {"order": order, "method": "PayPal"})


def paypal_cancel(request):
    """Handle cancelled PayPal payment"""
    order_id = request.GET.get("order_id")
    order = get_object_or_404(Order, id=order_id)

    return render(request, "public/payment_cancel.html", {"order": order})


def initiate_flutterwave_payment(request, order_id):
    """Initialize Flutterwave payment"""
    order = get_object_or_404(Order, id=order_id)

    flutterwave = FlutterwavePayment()
    result = flutterwave.initialize_payment(order, request)

    if result["success"]:
        return redirect(result["checkout_url"])
    else:
        return HttpResponse(f"Flutterwave payment initialization failed: {result.get('error')}", status=400)


def flutterwave_success(request):
    """Handle return from Flutterwave after payment"""
    order_id = request.GET.get("order_id")
    # Flutterwave also sends tx_ref, status, etc. in query params

    order = get_object_or_404(Order, id=order_id)

    # For better security, you should verify the transaction using Flutterwave's verify endpoint
    # For now, we mark as paid (improve with verification later)
    order.status = OrderStatus.PAID if hasattr(OrderStatus, "PAID") else "PAID"
    order.save()

    Payment.objects.create(
        order=order,
        method="flutterwave",
        amount=order.total_amount,
        status=OrderStatus.PAID if hasattr(OrderStatus, "PAID") else "PAID",
        transaction_id=order.payment_reference,
    )

    return render(request, "public/payment_success.html", {"order": order, "method": "Flutterwave"})


def flutterwave_cancel(request):
    """Handle cancelled Flutterwave payment"""
    order_id = request.GET.get("order_id")
    order = get_object_or_404(Order, id=order_id)

    return render(request, "public/payment_cancel.html", {"order": order})
