from django.contrib import admin
from django.urls import include, path
from security.views import InicioTemplate

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", InicioTemplate.as_view(), name="home"),
    path("security/", include("security.urls")),
    path("catalog/", include("catalog.urls")),
    path("customers/", include("customers.urls")),
    path("invoicing/", include("invoicing.urls")),
]