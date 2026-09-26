from django import forms
from django.utils import timezone

from .models import Rental, RentalRequest


class RentalRequestForm(forms.ModelForm):

    class Meta:
        model = RentalRequest

        fields = [
            "rental_date",
            "expected_return_date",
        ]

        widgets = {
            "rental_date": forms.DateInput(
                attrs={"type": "date"}
            ),
            "expected_return_date": forms.DateInput(
                attrs={"type": "date"}
            ),
        }

    def __init__(self, *args, car=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.car = car

    def clean(self):
        cleaned_data = super().clean()

        rental_date = cleaned_data.get(
            "rental_date"
        )

        expected_return_date = cleaned_data.get(
            "expected_return_date"
        )

        # Prevent past rental dates
        if (
            rental_date
            and rental_date < timezone.localdate()
        ):
            self.add_error(
                "rental_date",
                "Rental date cannot be in the past."
            )

        # Return date must be after rental date
        if (
            rental_date
            and expected_return_date
            and expected_return_date <= rental_date
        ):
            self.add_error(
                "expected_return_date",
                "Return date must be after the rental date."
            )

        # Prevent overlapping bookings
        if (
            self.car
            and rental_date
            and expected_return_date
            and expected_return_date > rental_date
        ):

            overlapping_rental = Rental.objects.filter(
                car=self.car,
                status="active",
                rental_date__lt=expected_return_date,
                expected_return_date__gt=rental_date,
            ).exists()

            overlapping_request = RentalRequest.objects.filter(
                car=self.car,
                status__in=["pending", "approved"],
                rental_date__lt=expected_return_date,
                expected_return_date__gt=rental_date,
            ).exists()

            if (
                overlapping_rental
                or overlapping_request
            ):
                raise forms.ValidationError(
                    "This car is already booked or requested "
                    "for part of the selected date range. "
                    "Please choose different dates."
                )

        return cleaned_data