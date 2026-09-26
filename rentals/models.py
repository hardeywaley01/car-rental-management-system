from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from cars.models import Car
from customers.models import Customer


class Rental(models.Model):

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="rentals"
    )

    car = models.ForeignKey(
        Car,
        on_delete=models.PROTECT,
        related_name="rentals"
    )

    rental_date = models.DateField()

    expected_return_date = models.DateField()

    actual_return_date = models.DateField(
        blank=True,
        null=True
    )

    daily_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    payment_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("partial", "Partial"),
            ("paid", "Paid"),
        ],
        default="pending"
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("active", "Active"),
            ("returned", "Returned"),
        ],
        default="active"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def clean(self):
        if self.status == "active":
            if self.car.status != "available":
                raise ValidationError(
                    f"{self.car} is not available for rental."
                )

    @property
    def balance(self):
        balance = self.total_cost - self.amount_paid
        return max(balance, Decimal("0.00"))

    def __str__(self):
        return f"{self.customer} - {self.car}"


class RentalRequest(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="rental_requests"
    )

    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name="rental_requests"
    )

    rental_date = models.DateField()

    expected_return_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.customer} - "
            f"{self.car} - "
            f"{self.status}"
        )