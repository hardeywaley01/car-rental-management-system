from django import forms

from .models import Customer


class CustomerForm(forms.ModelForm):

    class Meta:
        model = Customer

        fields = [
            "full_name",
            "phone",
            "email",
            "address",
            "driver_license",
        ]

        widgets = {
            "full_name": forms.TextInput(
                attrs={
                    "placeholder": "Full name"
                }
            ),

            "phone": forms.TextInput(
                attrs={
                    "placeholder": "Phone number"
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "placeholder": "Email address"
                }
            ),

            "address": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Address"
                }
            ),

            "driver_license": forms.TextInput(
                attrs={
                    "placeholder": "Driver's license number"
                }
            ),
        }