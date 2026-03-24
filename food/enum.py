from django.db import models


class OrderStatus(models.TextChoices):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
