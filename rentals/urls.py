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
        "<int:pk>/",
        views.rental_detail,
        name="rental_detail"
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
        "<int:pk>/inspect-car/",
        views.inspect_car,
        name="inspect_car"
    ),
        path(
        "<int:pk>/receipt/",
        views.rental_receipt,
        name="rental_receipt"
    ),
]