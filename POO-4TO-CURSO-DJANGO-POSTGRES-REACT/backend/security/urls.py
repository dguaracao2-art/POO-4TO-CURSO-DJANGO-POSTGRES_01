from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import (
    GroupCreateView,
    GroupListView,
    GroupUpdateView,
    LoginPageView,
    ProfileView,
    UserCreateView,
    UserDeactivateView,
    UserListView,
    UserUpdateView,
)

app_name = "security"

urlpatterns = [
    path("login/", LoginPageView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),

    path("users/", UserListView.as_view(), name="user_list"),
    path("users/create/", UserCreateView.as_view(), name="user_create"),
    path("users/<int:pk>/edit/", UserUpdateView.as_view(), name="user_update"),
    path("users/<int:pk>/deactivate/", UserDeactivateView.as_view(), name="user_deactivate"),

    path("groups/", GroupListView.as_view(), name="group_list"),
    path("groups/create/", GroupCreateView.as_view(), name="group_create"),
    path("groups/<int:pk>/edit/", GroupUpdateView.as_view(), name="group_update"),

    path("profile/", ProfileView.as_view(), name="profile"),
]