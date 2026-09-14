from django.contrib import admin

from .models import Rental


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):

    list_display = (
        "customer",
        "car",
        "rental_date",
        "expected_return_date",
        "actual_return_date",
        "total_cost",
        "payment_status",
        "status",
    )

    list_filter = (
        "status",
        "payment_status",
    )

    search_fields = (
        "customer__full_name",
        "customer__phone",
        "car__brand",
        "car__model",
        "car__plate_number",
    )