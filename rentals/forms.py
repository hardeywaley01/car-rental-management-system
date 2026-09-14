from django import forms

from cars.models import Car
from .models import Rental


class RentalForm(forms.ModelForm):

    class Meta:
        model = Rental

        fields = [
            "customer",
            "car",
            "rental_date",
            "expected_return_date",
            "daily_price",
            "payment_status",
            "status",
            "amount_paid",
        ]

        widgets = {
            "rental_date": forms.DateInput(
                attrs={
                    "type": "date"
                }
            ),

            "expected_return_date": forms.DateInput(
                attrs={
                    "type": "date"
                }
            ),
        }
        

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["car"].queryset = Car.objects.filter(
            status="available"
        )

        self.fields["daily_price"].required = False
        self.fields["daily_price"].widget.attrs["readonly"] = True

    def clean(self):

        cleaned_data = super().clean()

        car = cleaned_data.get("car")

        rental_date = cleaned_data.get(
            "rental_date"
        )

        expected_return_date = cleaned_data.get(
            "expected_return_date"
        )

        if car:

            if car.status != "available":

                raise forms.ValidationError(
                    "This car is not currently available for rental."
                )

            # Automatically use the car's daily price
            cleaned_data["daily_price"] = car.daily_price

        if rental_date and expected_return_date:

            if expected_return_date <= rental_date:

                raise forms.ValidationError(
                    "Expected return date must be after rental date."
                )

        return cleaned_data

def clean_amount_paid(self):

    amount_paid = self.cleaned_data.get("amount_paid")

    if amount_paid is None:
        amount_paid = 0

    if amount_paid < 0:
        raise forms.ValidationError(
            "Amount paid cannot be negative."
        )

    return amount_paid