from django.urls import path

from . import views


urlpatterns = [

    path(
        "",
        views.car_list,
        name="car_list"
    ),

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard"
    ),

    path(
        "add/",
        views.car_create,
        name="car_create"
    ),

    path(
        "status/<str:status>/",
        views.car_status,
        name="car_status"
    ),

    path(
        "<int:pk>/",
        views.car_detail,
        name="car_detail"
    ),

    path(
        "<int:pk>/edit/",
        views.car_edit,
        name="car_edit"
    ),

]