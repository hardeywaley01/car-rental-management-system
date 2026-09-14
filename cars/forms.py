from django import forms

from .models import Car


class CarForm(forms.ModelForm):

    class Meta:
        model = Car

        fields = [
            "brand",
            "model",
            "year",
            "plate_number",
            "daily_price",
            "status",
            "description",
            "image",
            "seats",
            "color",
            "transmission",
            "fuel_type",
            

        ]

        widgets = {

            "brand": forms.TextInput(
                attrs={
                    "placeholder": "e.g. Toyota"
                }
            ),

            "model": forms.TextInput(
                attrs={
                    "placeholder": "e.g. Corolla"
                }
            ),

            "year": forms.NumberInput(
                attrs={
                    "placeholder": "e.g. 2024"
                }
            ),

            "plate_number": forms.TextInput(
                attrs={
                    "placeholder": "e.g. ABC-123-XY"
                }
            ),

            "daily_price": forms.NumberInput(
                attrs={
                    "placeholder": "e.g. 30000",
                    "min": "0"
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Describe the vehicle..."
                }
            ),
        }