from django.shortcuts import get_object_or_404, redirect, render

from .forms import CarForm
from .models import Car
from django.db.models import Count
from rentals.models import Rental
from customers.models import Customer
from django.db import models
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models import Q

@login_required
def car_list(request):

    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()

    cars = Car.objects.all().order_by("-created_at")

    if search:
        cars = cars.filter(
            models.Q(brand__icontains=search)
            | models.Q(model__icontains=search)
            | models.Q(plate_number__icontains=search)
        )
    if status:
        cars = cars.filter(status=status)

    return render(
        request,
        "cars/car_list.html",
        {
            "cars": cars,
            "search": search,
            "status": status,
        }
    )


@login_required
def car_create(request):
    if request.method == "POST":
        form = CarForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect("car_list")

    else:
        form = CarForm()

    return render(
        request,
        "cars/car_form.html",
        {"form": form}
    )
@login_required
def car_update(request, pk):

    car = get_object_or_404(Car, pk=pk)

    if request.method == "POST":
        form = CarForm(
            request.POST,
            request.FILES,
            instance=car
        )

        if form.is_valid():
            form.save()
            return redirect("car_list")

    else:
        form = CarForm(instance=car)

    context = {
        "form": form,
        "car": car,
    }

    return render(
        request,
        "cars/car_form.html",
        context
    )
def car_update(request, pk):

    car = get_object_or_404(Car, pk=pk)

    if request.method == "POST":
        form = CarForm(
            request.POST,
            request.FILES,
            instance=car
        )

        if form.is_valid():
            form.save()
            return redirect("car_list")

    else:
        form = CarForm(instance=car)

    context = {
        "form": form,
        "car": car,
    }

    return render(
        request,
        "cars/car_form.html",
        context
    )

@login_required
def car_delete(request, pk):

    car = get_object_or_404(Car, pk=pk)

    if request.method == "POST":
        car.delete()
        return redirect("car_list")

    context = {
        "car": car,
    }

    return render(
        request,
        "cars/car_confirm_delete.html",
        context
    )
def car_status(request, status):

    valid_statuses = {
        "available",
        "rented",
        "returned",
        "maintenance",
    }

    if status not in valid_statuses:
        return redirect("car_list")

    cars = Car.objects.filter(status=status)

    context = {
        "cars": cars,
        "current_status": status,
    }

    return render(
        request,
        "cars/car_list.html",
        context
    )

@login_required
def dashboard(request):

    available_cars = Car.objects.filter(
        status="available"
    ).count()

    rented_cars = Car.objects.filter(
        status="rented"
    ).count()

    returned_cars = Car.objects.filter(
        status="returned"
    ).count()
    returned_rentals = Rental.objects.filter(
    status="returned"
    ).count()

    maintenance_cars = Car.objects.filter(
        status="maintenance"
    ).count()

    active_rentals = Rental.objects.filter(
        status="active"
    ).count()

    total_cars = Car.objects.count()

    recent_rentals = Rental.objects.select_related(
        "customer",
        "car"
    ).order_by(
        "-id"
    )[:5]

    context = {
        "available_cars": available_cars,
        "rented_cars": rented_cars,
        "returned_cars": returned_cars,
        "maintenance_cars": maintenance_cars,
        "active_rentals": active_rentals,
        "total_cars": total_cars,
        "recent_rentals": recent_rentals,
        "returned_rentals": returned_rentals,
    }

    return render(
        request,
        "dashboard.html",
        context
    )

@login_required
def car_list(request):

    cars = Car.objects.all().order_by(
        "brand",
        "model"
    )

    search = request.GET.get(
        "search",
        ""
    ).strip()

    status = request.GET.get(
        "status",
        ""
    ).strip()

    if search:

        cars = cars.filter(
            brand__icontains=search
        ) | cars.filter(
            model__icontains=search
        ) | cars.filter(
            plate_number__icontains=search
        )

    if status:

        cars = cars.filter(
            status=status
        )

    context = {
        "cars": cars,
        "search": search,
        "selected_status": status,
        "status_choices": Car.STATUS_CHOICES,
    }

    return render(
        request,
        "cars/car_list.html",
        context
    )


def car_create(request):

    if request.method == "POST":

        form = CarForm(request.POST, request.FILES)

        if form.is_valid():

            form.save()

            return redirect("car_list")

    else:

        form = CarForm()

    return render(
        request,
        "cars/car_form.html",
        {
            "form": form
        }
    )


def car_detail(request, pk):

    car = get_object_or_404(
        Car,
        pk=pk
    )

    return render(
        request,
        "cars/car_detail.html",
        {
            "car": car
        }
    )

@login_required
def car_edit(request, pk):

    car = get_object_or_404(
        Car,
        pk=pk
    )

    if request.method == "POST":

        form = CarForm(
            request.POST,
            request.FILES,
            instance=car
        )

        if form.is_valid():

            form.save()

            return redirect(
                "car_detail",
                pk=car.pk
            )

    else:

        form = CarForm(
            instance=car
        )

    return render(
        request,
        "cars/car_form.html",
        {
            "form": form,
            "car": car
        }
    )

@login_required
def car_status(request, status):

    valid_statuses = {
        choice[0]
        for choice in Car.STATUS_CHOICES
    }

    if status not in valid_statuses:

        return redirect("car_list")

    cars = Car.objects.filter(
        status=status
    ).order_by(
        "brand",
        "model"
    )

    return render(
        request,
        "cars/car_list.html",
        {
            "cars": cars,
            "selected_status": status,
            "status_choices": Car.STATUS_CHOICES,
            "search": "",
        }
    )
@login_required
def reports(request):

    total_cars = Car.objects.count()

    available_cars = Car.objects.filter(
        status="available"
    ).count()

    rented_cars = Car.objects.filter(
        status="rented"
    ).count()

    maintenance_cars = Car.objects.filter(
        status="maintenance"
    ).count()

    returned_cars = Car.objects.filter(
        status="returned"
    ).count()

    total_customers = Customer.objects.count()

    active_rentals = Rental.objects.filter(
        status="active"
    ).count()

    returned_rentals = Rental.objects.filter(
        status="returned"
    ).count()

    total_revenue = Rental.objects.filter(
        payment_status="paid"
    ).aggregate(
        total=Sum("total_cost")
    )["total"] or 0

    outstanding = Rental.objects.exclude(
        payment_status="paid"
    ).aggregate(
        total=Sum("total_cost")
    )["total"] or 0

    context = {
        "total_cars": total_cars,
        "available_cars": available_cars,
        "rented_cars": rented_cars,
        "maintenance_cars": maintenance_cars,
        "returned_cars": returned_cars,
        "total_customers": total_customers,
        "active_rentals": active_rentals,
        "returned_rentals": returned_rentals,
        "total_revenue": total_revenue,
        "outstanding": outstanding,
    }

    return render(
        request,
        "reports.html",
        context
    )