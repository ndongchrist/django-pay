# food/stripe.py
import stripe
from django.conf import settings
import uuid


class StripePayment:
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.currency = "XAF"  # Change if you want to support USD/EUR etc.

    def initialize_payment(self, order, request):
        """
        Create a Stripe Checkout Session and return the session URL
        """
        transaction_ref = f"PLATE-{order.id}-{uuid.uuid4().hex[:12]}"

        # For local development: Use your ngrok HTTPS URL
        base_url = "https://8813-2605-59c0-1e9e-a908-778c-c77f-9ce0-861d.ngrok-free.app"  # ← Update every ngrok restart

        success_url = f"{base_url}/stripe/success/?order_id={order.id}&session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{base_url}/stripe/cancel/?order_id={order.id}"

        try:
            # Create line items from OrderItems
            line_items = []
            for item in order.items.all():
                line_items.append(
                    {
                        "price_data": {
                            "currency": self.currency.lower(),
                            "product_data": {
                                "name": item.product.name,
                                "description": item.product.description[:255],  # Stripe limit
                                "images": [request.build_absolute_uri(item.product.image.url)]
                                if item.product.image
                                else [],
                            },
                            "unit_amount": int(
                                item.price * 100
                            ),  # Stripe expects amount in smallest unit (e.g. centimes)
                        },
                        "quantity": item.quantity,
                    }
                )

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=line_items,
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    "order_id": str(order.id),
                    "transaction_ref": transaction_ref,
                },
                customer_email=getattr(order.user, "email", None) if order.user else None,
            )

            # Save reference
            order.payment_reference = transaction_ref
            order.save()

            return {"success": True, "checkout_url": checkout_session.url, "session_id": checkout_session.id}

        except stripe.error.StripeError as e:
            return {"success": False, "error": f"Stripe error: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
