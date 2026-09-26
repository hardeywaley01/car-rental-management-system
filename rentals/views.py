from django.contrib import messages
from django.db import transaction
from django.http import request
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from cars.models import Car
from customers.models import Customer
from .forms import RentalForm
from .models import Rental, RentalRequest
from datetime import date
from decimal import Decimal
from django.db import models            
from django.db.models import Q

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .request_forms import RentalRequestForm
from django.contrib.admin.views.decorators import staff_member_required

@login_required
@staff_member_required
def rental_create(request):

    if request.method == "POST":

        form = RentalForm(request.POST)

        if form.is_valid():

            rental = form.save(commit=False)

            car = rental.car
            start_date = rental.rental_date
            return_date = rental.expected_return_date

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

                rental.amount_paid = (
                    rental.amount_paid
                    or Decimal("0.00")
                )

                # Prevent payment above the rental cost
                if rental.amount_paid > rental.total_cost:

                    form.add_error(
                        "amount_paid",
                        "Amount paid cannot be greater than "
                        "the total rental cost."
                    )

                else:

                    if rental.amount_paid == rental.total_cost:
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
@staff_member_required
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
@staff_member_required
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
@staff_member_required
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
@staff_member_required
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
        Rental.objects.select_related(
            "customer",
            "car"
        ),
        pk=pk
    )

    # Staff can view every rental.
    # Customers can only view their own rentals.
    if not request.user.is_staff:
        if (
            rental.customer.user_id
            != request.user.id
        ):
            messages.error(
                request,
                "You are not allowed to view this rental."
            )
            return redirect("customer_dashboard")

    return render(
        request,
        "rentals/rental_detail.html",
        {
            "rental": rental
        }
    )

@login_required
def rental_receipt(request, pk):
    rental = get_object_or_404(
        Rental.objects.select_related(
            "customer",
            "car"
        ),
        pk=pk
    )

    # Staff can view every receipt.
    # Customers can only view receipts belonging to them.
    if not request.user.is_staff:
        if (
            rental.customer.user_id
            != request.user.id
        ):
            messages.error(
                request,
                "You are not allowed to view this receipt."
            )
            return redirect("customer_dashboard")

    rental_days = (
        rental.expected_return_date
        - rental.rental_date
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
@login_required
def rental_request_create(request, car_id):
    customer = Customer.objects.filter(
        user=request.user
    ).first()

    if customer is None:
        messages.error(
            request,
            "A customer profile is required to request a car."
        )
        return redirect("customer_dashboard")

    car = get_object_or_404(
        Car,
        pk=car_id,
        status="available"
    )

    existing_request = RentalRequest.objects.filter(
        customer=customer,
        car=car,
        status="pending"
    ).exists()

    if existing_request:
        messages.warning(
            request,
            "You already have a pending request for this car."
        )
        return redirect("customer_dashboard")

    if request.method == "POST":
        form = RentalRequestForm(
            request.POST,
            car=car
    )
        if form.is_valid():
            rental_request = form.save(commit=False)

            rental_request.customer = customer
            rental_request.car = car

            rental_request.save()

            messages.success(
                request,
                "Your rental request has been submitted successfully."
            )

            return redirect("customer_dashboard")

    else:
        form = RentalRequestForm(
        car=car
    )


    return render(
        request,
        "rentals/rental_request_form.html",
        {
            "form": form,
            "car": car,
        }
    )

@staff_member_required
def rental_request_list(request):
    rental_requests = RentalRequest.objects.select_related(
        "customer",
        "car"
    ).order_by("-created_at")

    return render(
        request,
        "rentals/rental_request_list.html",
        {
            "rental_requests": rental_requests
        }
    )
@staff_member_required
@require_POST
def approve_rental_request(request, pk):
    rental_request = get_object_or_404(
        RentalRequest,
        pk=pk
    )

    if rental_request.status != "pending":
        messages.error(
            request,
            "This rental request has already been processed."
        )
        return redirect("rental_request_list")

    car = rental_request.car

    if car.status != "available":
        messages.error(
            request,
            "This car is no longer available."
        )
        return redirect("rental_request_list")

    number_of_days = (
        rental_request.expected_return_date
        - rental_request.rental_date
    ).days

    with transaction.atomic():

        Rental.objects.create(
            customer=rental_request.customer,
            car=car,
            rental_date=rental_request.rental_date,
            expected_return_date=rental_request.expected_return_date,
            daily_price=car.daily_price,
            total_cost=car.daily_price * Decimal(number_of_days),
            payment_status="pending",
            status="active"
        )

        rental_request.status = "approved"
        rental_request.save(update_fields=["status"])

        car.status = "rented"
        car.save(update_fields=["status"])

    messages.success(
        request,
        "Rental request approved successfully."
    )

    return redirect("rental_request_list")

@staff_member_required
@require_POST
def reject_rental_request(request, pk):
    rental_request = get_object_or_404(
        RentalRequest,
        pk=pk
    )

    if rental_request.status != "pending":
        messages.error(
            request,
            "This rental request has already been processed."
        )
        return redirect("rental_request_list")

    rental_request.status = "rejected"
    rental_request.save(update_fields=["status"])

    messages.success(
        request,
        "Rental request rejected successfully."
    )

    return redirect("rental_request_list")

@staff_member_required
@require_POST
def update_rental_payment(request, pk):

    rental = get_object_or_404(
        Rental,
        pk=pk
    )

    amount = request.POST.get(
        "amount"
    )

    try:
        amount = Decimal(amount)

    except (TypeError, ValueError):

        messages.error(
            request,
            "Please enter a valid payment amount."
        )

        return redirect(
            "rental_detail",
            pk=rental.pk
        )

    if amount <= 0:

        messages.error(
            request,
            "Payment amount must be greater than zero."
        )

        return redirect(
            "rental_detail",
            pk=rental.pk
        )

    remaining_balance = (
        rental.total_cost
        - rental.amount_paid
    )

    if amount > remaining_balance:

        messages.error(
            request,
            "Payment cannot be greater than the remaining balance."
        )

        return redirect(
            "rental_detail",
            pk=rental.pk
        )

    rental.amount_paid += amount

    if rental.amount_paid >= rental.total_cost:
        rental.payment_status = "paid"

    elif rental.amount_paid > 0:
        rental.payment_status = "partial"

    else:
        rental.payment_status = "pending"

    rental.save(
        update_fields=[
            "amount_paid",
            "payment_status",
        ]
    )

    messages.success(
        request,
        "Payment recorded successfully."
    )

    return redirect(
        "rental_detail",
        pk=rental.pk
    )