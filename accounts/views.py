from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render

from cars.models import Car
from customers.models import Customer
from rentals.models import Rental, RentalRequest

from .forms import CustomerRegistrationForm


# =========================================================
# CUSTOMER REGISTRATION
# =========================================================

def register(request):

    if request.user.is_authenticated:

        if request.user.is_staff:
            return redirect("dashboard")

        customer = Customer.objects.filter(
            user=request.user
        ).first()

        if customer is not None:
            return redirect(
                "customer_dashboard"
            )

        # The user account exists but has no Customer profile.
        # Log out so the user can create a complete customer account.
        logout(request)

        messages.info(
            request,
            "Your existing account does not have a customer profile. "
            "Please complete a new customer registration."
        )

    if request.method == "POST":

        form = CustomerRegistrationForm(
            request.POST
        )

        if form.is_valid():

            with transaction.atomic():

                user = form.save()

                Customer.objects.create(
                    user=user,
                    full_name=form.cleaned_data["full_name"],
                    email=form.cleaned_data["email"],
                    phone=form.cleaned_data["phone"],
                    address=form.cleaned_data["address"],
                    driver_license=form.cleaned_data["driver_license"],
                )

            login(
                request,
                user
            )

            return redirect(
                "customer_dashboard"
            )

    else:

        form = CustomerRegistrationForm()

    return render(
        request,
        "registration/register.html",
        {
            "form": form
        }
    )


# =========================================================
# CUSTOMER DASHBOARD
# =========================================================

@login_required
def customer_dashboard(request):

    # Staff should use the staff dashboard
    if request.user.is_staff:

        return redirect(
            "dashboard"
        )

    customer = Customer.objects.filter(
        user=request.user
    ).first()

    # Handle old user accounts that have no Customer profile
    if customer is None:

        logout(request)

        messages.info(
            request,
            "Your account does not have a customer profile. "
            "Please complete customer registration."
        )

        return redirect(
            "register"
        )

    available_cars = Car.objects.filter(
        status="available"
    )

    rental_requests = RentalRequest.objects.filter(
        customer=customer
    ).select_related(
        "car"
    ).order_by(
        "-created_at"
    )

    active_rentals = Rental.objects.filter(
        customer=customer,
        status="active"
    ).select_related(
        "car"
    ).order_by(
        "-created_at"
    )

    returned_rentals = Rental.objects.filter(
        customer=customer,
        status="returned"
    ).select_related(
        "car"
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "accounts/customer_dashboard.html",
        {
            "customer": customer,
            "available_cars": available_cars,
            "rental_requests": rental_requests,
            "active_rentals": active_rentals,
            "returned_rentals": returned_rentals,
        }
    )


# =========================================================
# LOGIN
# =========================================================

def user_login(request):

    if request.user.is_authenticated:

        if request.user.is_staff:

            return redirect(
                "dashboard"
            )

        customer = Customer.objects.filter(
            user=request.user
        ).first()

        if customer is not None:

            return redirect(
                "customer_dashboard"
            )

        logout(request)

    if request.method == "POST":

        username = request.POST.get(
            "username"
        )

        password = request.POST.get(
            "password"
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            if user.is_staff:

                login(
                    request,
                    user
                )

                return redirect(
                    "dashboard"
                )

            customer = Customer.objects.filter(
                user=user
            ).first()

            if customer is None:

                return render(
                    request,
                    "registration/login.html",
                    {
                        "error": (
                            "This account does not have a customer profile. "
                            "Please create a customer account using Register."
                        )
                    }
                )

            login(
                request,
                user
            )

            return redirect(
                "customer_dashboard"
            )

        return render(
            request,
            "registration/login.html",
            {
                "error": "Invalid username or password."
            }
        )

    return render(
        request,
        "registration/login.html"
    )