from django.shortcuts import get_object_or_404, redirect, render

from .forms import CustomerForm
from .models import Customer
from django.db import models
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models.deletion import ProtectedError


@login_required
def customer_list(request):

    search = request.GET.get("search", "").strip()

    customers = Customer.objects.all().order_by("-created_at")

    if search:
        customers = customers.filter(
            models.Q(full_name__icontains=search)
            | models.Q(phone__icontains=search)
            | models.Q(driver_license__icontains=search)
        )

    return render(
        request,
        "customers/customer_list.html",
        {
            "customers": customers,
            "search": search,
        }
    )

@login_required
def customer_create(request):

    if request.method == "POST":

        form = CustomerForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect("customer_list")

    else:

        form = CustomerForm()

    context = {
        "form": form,
    }

    return render(
        request,
        "customers/customer_form.html",
        context
    )

@login_required
def customer_detail(request, pk):

    customer = get_object_or_404(
        Customer,
        pk=pk
    )

    rentals = customer.rentals.select_related(
        "car"
    ).all()

    context = {
        "customer": customer,
        "rentals": rentals,
    }

    return render(
        request,
        "customers/customer_detail.html",
        context
    )

@login_required
def customer_edit(request, pk):

    customer = get_object_or_404(
        Customer,
        pk=pk
    )

    if request.method == "POST":

        form = CustomerForm(
            request.POST,
            instance=customer
        )

        if form.is_valid():

            form.save()

            return redirect(
                "customer_detail",
                pk=customer.pk
            )

    else:

        form = CustomerForm(
            instance=customer
        )

    context = {
        "form": form,
        "customer": customer,
    }

    return render(
        request,
        "customers/customer_form.html",
        context
    )

@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == "POST":
        try:
            customer.delete()
            messages.success(request, "Customer deleted successfully.")
            return redirect("customer_list")

        except ProtectedError:
            messages.error(
                request,
                "This customer cannot be deleted because they have rental records."
            )
            return redirect("customer_detail", pk=customer.pk)

    return render(
        request,
        "customers/customer_confirm_delete.html",
        {"customer": customer}
    )