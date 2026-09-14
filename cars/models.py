from django.db import models

# Create your models here.
class Car(models.Model):
    STATUS_CHOICES = [
        ("available", "Available"),
        ("rented", "Rented"),
        ("returned", "Returned"),
        ("maintenance", "Maintenance"),
    ]
    TRANSMISSION_CHOICES = [
        ("automatic", "Automatic"),
        ("manual", "Manual"),
    ]

    FUEL_CHOICES = [
        ("petrol", "Petrol"),
        ("diesel", "Diesel"),
        ("electric", "Electric"),
        ("hybrid", "Hybrid"),
    ]

    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    plate_number = models.CharField(max_length=20, unique=True)

    color = models.CharField(max_length=50)

    transmission = models.CharField(
        max_length=20,
        choices=TRANSMISSION_CHOICES
    )

    fuel_type = models.CharField(
        max_length=20,
        choices=FUEL_CHOICES
    )

    seats = models.PositiveSmallIntegerField()

    daily_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    image = models.ImageField(
        upload_to="cars/",
        blank=True,
        null=True
    )

    description = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="available"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.brand} {self.model} ({self.plate_number})"
