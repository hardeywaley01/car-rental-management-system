from django.contrib import admin
from .models import Car


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = (
        "brand",
        "model",
        "plate_number",
        "status",
        "daily_price",
    )

    list_filter = (
        "status",
        "brand",
        "fuel_type",
        "transmission",
    )

    search_fields = (
        "brand",
        "model",
        "plate_number",
    )
