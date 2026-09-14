from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from cars.models import Car
from .forms import RentalForm
from .models import Rental
from datetime import date
from decimal import Decimal
from django.db import models
from django.db.models import Q

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

@login_required
def rental_create(request):

    if request.method == "POST":

        form = RentalForm(request.POST)

        if form.is_valid():

            rental = form.save(commit=False)

            car = rental.car

            start_date = rental.rental_date

            return_date = (
                rental.expected_return_date
            )

            number_of_days = (
                return_date - start_date
            ).days

            if number_of_days <= 0:

                form.add_error(
                    "expected_return_date",
                    "Return date must be after rental date."
                )

            elif car.status != "available":

                form.add_error(
                    "car",
                    "This car is no longer available."
                )

            else:

                rental.daily_price = car.daily_price

                rental.total_cost = (
                    car.daily_price
                    * Decimal(number_of_days)
                )
                rental.amount_paid = rental.amount_paid or Decimal("0.00")

                if rental.amount_paid >= rental.total_cost:
                    rental.payment_status = "paid"

                elif rental.amount_paid > 0:
                    rental.payment_status = "partial"

                else:
                    rental.payment_status = "pending"

                with transaction.atomic():

                    rental.save()

                    car.status = "rented"

                    car.save(
                        update_fields=["status"]
                    )

                return redirect(
                    "rental_list"
                )

    else:

        form = RentalForm()

    return render(
        request,
        "rentals/rental_form.html",
        {
            "form": form
        }
    )
@login_required
def rental_list(request):

    search = request.GET.get("search", "").strip()

    rentals = Rental.objects.select_related(
        "customer",
        "car"
    ).all().order_by("-created_at")

    status = request.GET.get("status", "").strip()

    if search:
        rentals = rentals.filter(
            models.Q(customer__full_name__icontains=search)
            | models.Q(car__brand__icontains=search)
            | models.Q(car__model__icontains=search)
            | models.Q(car__plate_number__icontains=search)
        )

    rentals = rentals.order_by("-rental_date")
    if status:
        rentals = rentals.filter(
            status=status
        )
    return render(
        request,
        "rentals/rental_list.html",
        {
            "rentals": rentals,
            "search": search,
            "status": status,
        }
    )
@login_required
def rental_return(request, pk):

    rental = get_object_or_404(
        Rental,
        pk=pk
    )

    if request.method != "POST":
        return redirect(
            "rental_list"
        )

    if rental.status != "active":

        messages.error(
            request,
            "This rental has already been returned."
        )

        return redirect(
            "rental_detail",
            pk=rental.pk
        )

    return_date = timezone.now().date()

    with transaction.atomic():

        rental.actual_return_date = return_date
        rental.status = "returned"

        rental.save(
            update_fields=[
                "actual_return_date",
                "status",
            ]
        )

        car = rental.car

        car.status = "returned"

        car.save(
            update_fields=["status"]
        )

    messages.success(
        request,
        "Car returned successfully and is awaiting inspection."
    )

    return redirect(
        "rental_detail",
        pk=rental.pk
    )
@login_required
def inspect_car(request, pk):

    rental = get_object_or_404(
        Rental,
        pk=pk
    )

    if rental.status != "returned":
        messages.error(
            request,
            "Only returned cars can be inspected."
        )
        return redirect("rental_list")

    if request.method == "POST":

        inspection_result = request.POST.get(
            "inspection_result"
        )

        with transaction.atomic():

            if inspection_result == "available":

                rental.car.status = "available"

                rental.car.save(
                    update_fields=["status"]
                )

                messages.success(
                    request,
                    "Car passed inspection and is now available for rental."
                )

            elif inspection_result == "maintenance":

                rental.car.status = "maintenance"

                rental.car.save(
                    update_fields=["status"]
                )

                messages.warning(
                    request,
                    "Car has been sent for maintenance."
                )

        return redirect("car_list")

    context = {
        "rental": rental,
    }

    return render(
        request,
        "rentals/inspect_car.html",
        context
    )
@login_required
@require_POST
def inspect_returned_car(request, pk):

    rental = get_object_or_404(
        Rental,
        pk=pk
    )

    if rental.status != "returned":

        messages.error(
            request,
            "Only returned cars can be inspected."
        )

        return redirect(
            "rental_detail",
            pk=rental.pk
        )

    decision = request.POST.get("decision")

    if decision == "available":

        rental.car.status = "available"

        rental.car.save(
            update_fields=["status"]
        )

        messages.success(
            request,
            "Car inspected and marked available for rental."
        )

    elif decision == "maintenance":

        rental.car.status = "maintenance"

        rental.car.save(
            update_fields=["status"]
        )

        messages.warning(
            request,
            "Car has been sent to maintenance."
        )

    else:

        messages.error(
            request,
            "Invalid inspection decision."
        )

    return redirect(
        "rental_detail",
        pk=rental.pk
    )

@login_required
def rental_detail(request, pk):
    rental = get_object_or_404(
        Rental,
        pk=pk
    )

    return render(
        request,
        "rentals/rental_detail.html",
        {
            "rental": rental
        }
    )

def rental_receipt(request, pk):
    rental = get_object_or_404(
        Rental.objects.select_related(
            "customer",
            "car"
        ),
        pk=pk
    )

    rental_days = (
        rental.expected_return_date - rental.rental_date
    ).days

    context = {
        "rental": rental,
        "rental_days": rental_days,
    }

    return render(
        request,
        "rentals/rental_receipt.html",
        context
    )

