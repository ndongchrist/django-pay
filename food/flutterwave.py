# food/flutterwave.py
import requests
import uuid
from django.conf import settings


class FlutterwavePayment:
    BASE_URL = "https://api.flutterwave.com/v3"

    def initialize_payment(self, order, request):
        tx_ref = f"PLATE-{order.id}-{uuid.uuid4().hex[:12]}"

        # Update this every time ngrok restarts
        base_url = "https://8813-2605-59c0-1e9e-a908-778c-c77f-9ce0-861d.ngrok-free.app"

        redirect_url = f"{base_url}/flutterwave/success/?order_id={order.id}"

        payload = {
            "tx_ref": tx_ref,
            "amount": float(order.total_amount),
            "currency": "XAF",
            "redirect_url": redirect_url,
            "payment_options": "card,mobilemoney,ussd,banktransfer",
            "customer": {
                "email": getattr(order.user, "email", "guest@plate.studio"),
                "name": f"{getattr(order.user, 'first_name', 'Customer')} {getattr(order.user, 'last_name', 'Guest')}".strip()
                or "Platē Customer",
            },
            "customizations": {
                "title": "Platē Studio",
                "description": f"Order #{order.id} - Premium Dinnerware",
            },
            "meta": {"order_id": str(order.id), "source": "Platē Django Store"},
        }

        headers = {
            "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(f"{self.BASE_URL}/payments", headers=headers, json=payload, timeout=30)

            print(f"[Flutterwave] Status: {response.status_code}")
            print(f"[Flutterwave] Response: {response.text[:600]}...")  # Debug

            if response.status_code in (200, 201):
                data = response.json()
                if data.get("status") == "success":
                    link = data.get("data", {}).get("link")
                    if link:
                        order.payment_reference = tx_ref
                        order.save()
                        return {"success": True, "checkout_url": link, "tx_ref": tx_ref}

            return {"success": False, "error": data.get("message") if "data" in locals() else response.text}

        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Network error: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
