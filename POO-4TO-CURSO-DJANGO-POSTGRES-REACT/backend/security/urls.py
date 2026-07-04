from django.contrib.auth.views import LogoutView
from django.urls import path
from .views import InicioTemplate, LoginPageView

app_name = "security"
urlpatterns = [
    path("login/", LoginPageView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
