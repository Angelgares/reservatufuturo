from django.urls import path
from . import views
from .views import CustomLoginView, register
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", register, name="register"),
]
