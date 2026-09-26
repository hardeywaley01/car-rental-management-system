from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from customers.models import Customer


class CustomerRegistrationForm(UserCreationForm):
    full_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    phone = forms.CharField(max_length=20)
    address = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3})
    )
    driver_license = forms.CharField(
        max_length=50,
        label="Driver's License Number"
    )

    class Meta:
        model = User

        fields = [
            "full_name",
            "email",
            "phone",
            "address",
            "driver_license",
            "username",
            "password1",
            "password2",
        ]

    def clean_driver_license(self):
        driver_license = self.cleaned_data["driver_license"].strip()
    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(
            email__iexact=email
        ).exists():
            raise forms.ValidationError(
                "An account with this email address already exists."
            )

        return email
    
        if Customer.objects.filter(
            driver_license__iexact=driver_license
        ).exists():
            raise forms.ValidationError(
                "A customer with this driver's license number already exists."
            )

        return driver_license