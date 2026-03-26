# food/paypal.py
import paypalrestsdk
from django.conf import settings
import uuid


class PayPalPayment:
    def __init__(self):
        # Configure PayPal SDK
        paypalrestsdk.configure(
            {
                "mode": settings.PAYPAL_MODE,  # "sandbox" or "live"
                "client_id": settings.PAYPAL_CLIENT_ID,
                "client_secret": settings.PAYPAL_CLIENT_SECRET,
            }
        )

    def initialize_payment(self, order, request):
        """
        Create a PayPal order and return the approval URL
        """
        transaction_ref = f"PLATE-{order.id}-{uuid.uuid4().hex[:12]}"

        # For local development: Use ngrok HTTPS URL
        base_url = "https://8813-2605-59c0-1e9e-a908-778c-c77f-9ce0-861d.ngrok-free.app"  # ← Update every ngrok restart

        success_url = f"{base_url}/paypal/success/?order_id={order.id}"
        cancel_url = f"{base_url}/paypal/cancel/?order_id={order.id}"

        try:
            payment = paypalrestsdk.Payment(
                {
                    "intent": "sale",
                    "payer": {"payment_method": "paypal"},
                    "redirect_urls": {"return_url": success_url, "cancel_url": cancel_url},
                    "transactions": [
                        {
                            "item_list": {
                                "items": [
                                    {
                                        "name": item.product.name,
                                        "sku": str(item.product.id),
                                        "price": str(item.price),
                                        "currency": "USD",
                                        "quantity": item.quantity,
                                    }
                                    for item in order.items.all()
                                ]
                            },
                            "amount": {"total": str(order.total_amount), "currency": "USD"},
                            "description": f"Platē Studio Order #{order.id}",
                        }
                    ],
                }
            )

            if payment.create():
                # Find the approval URL
                for link in payment.links:
                    if link.rel == "approval_url":
                        approval_url = str(link.href)
                        break

                # Save reference
                order.payment_reference = transaction_ref
                order.save()

                return {"success": True, "approval_url": approval_url, "payment_id": payment.id}
            else:
                return {"success": False, "error": payment.error}

        except Exception as e:
            return {"success": False, "error": f"PayPal error: {str(e)}"}
