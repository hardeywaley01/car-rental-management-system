from django.urls import path
from . import views

urlpatterns = [
    path(
        "",
        views.rental_list,
        name="rental_list"
    ),

    path(
        "add/",
        views.rental_create,
        name="rental_create"
    ),
    path(
        "requests/",
        views.rental_request_list,
        name="rental_request_list"
    ),
    path(
    "<int:pk>/payment/",
    views.update_rental_payment,
    name="update_rental_payment"
    ),
    
    path(
        "<int:pk>/",
        views.rental_detail,
        name="rental_detail"
    ),

    path(
    "request/<int:car_id>/",
    views.rental_request_create,
    name="rental_request_create"
    ),

    path(
        "<int:pk>/return/",
        views.rental_return,
        name="rental_return"
    ),

    path(
        "<int:pk>/inspect/",
        views.inspect_returned_car,
        name="inspect_returned_car"
    ),

    
        path(
        "<int:pk>/receipt/",
        views.rental_receipt,
        name="rental_receipt"
    ),
    
    path(
    "requests/<int:pk>/approve/",
    views.approve_rental_request,
    name="approve_rental_request"
    ),

    path(
    "requests/<int:pk>/reject/",
    views.reject_rental_request,
    name="reject_rental_request"
    ),
]