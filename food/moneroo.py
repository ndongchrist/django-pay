# food/moneroo.py
import requests
import json
from django.conf import settings
import uuid


class MonerooPayment:
    BASE_URL = "https://api.moneroo.io/v1"

    def __init__(self):
        self.secret_key = getattr(settings, "MONEROO_SECRET_KEY", None)
        if not self.secret_key:
            raise ValueError("MONEROO_SECRET_KEY is not set in settings.py")

    def initialize_payment(self, order, request):
        """
        Initialize Moneroo payment and return the checkout URL
        """
        transaction_ref = f"PLATE-{order.id}-{uuid.uuid4().hex[:10]}"

        # For local development, use ngrok HTTPS URL
        base_url = (
            "https://8813-2605-59c0-1e9e-a908-778c-c77f-9ce0-861d.ngrok-free.app"  # ← Update this every ngrok restart
        )

        return_url = f"{base_url}/moneroo/success/?order_id={order.id}"

        payload = {
            "amount": float(order.total_amount),
            "currency": "USD",  # Change if you use another currency
            "description": f"Platē Studio Order #{order.id} - Premium Dinnerware",
            "return_url": return_url,
            "customer": {
                "email": getattr(order.user, "email", "guest@plate.studio"),
                "first_name": getattr(order.user, "first_name", "Customer") or "Customer",
                "last_name": getattr(order.user, "last_name", "") or "Guest",
            },
            "metadata": {"order_id": str(order.id), "transaction_ref": transaction_ref, "platform": "Platē Studio"},
            # Optional: restrict methods if needed
            # "methods": ["mtn_cm"]
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.secret_key}",
            "Accept": "application/json",
        }

        try:
            response = requests.post(
                f"{self.BASE_URL}/payments/initialize", headers=headers, data=json.dumps(payload), timeout=30
            )

            if response.status_code in (200, 201):
                data = response.json()
                checkout_url = data.get("data", {}).get("checkout_url")
                if checkout_url:
                    # Save reference to Order
                    order.payment_reference = transaction_ref
                    order.save()
                    return {"success": True, "checkout_url": checkout_url}
                else:
                    return {"success": False, "error": "No checkout URL received"}
            else:
                error_msg = response.json().get("message", response.text)
                return {"success": False, "error": f"Moneroo API error: {error_msg}"}

        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Network error: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
