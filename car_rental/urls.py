from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from accounts import views as account_views
from cars import views as car_views
from . import views


urlpatterns = [
    path(
        "admin/",
        admin.site.urls
    ),

    path(
        "accounts/",
        include("accounts.urls")
    ),

    path(
        "",
        views.home,
        name="home"
    ),

    path(
        "cars/",
        include("cars.urls")
    ),

    path(
        "rentals/",
        include("rentals.urls")
    ),

    path(
        "customers/",
        include("customers.urls")
    ),

    path(
        "login/",
        account_views.user_login,
        name="login"
    ),

    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout"
    ),

    path(
        "reports/",
        car_views.reports,
        name="reports"
    ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )