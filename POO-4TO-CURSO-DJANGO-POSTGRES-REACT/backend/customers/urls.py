from django.urls import path
from .views import (
    ClienteCreateView, ClienteDeactivateView, ClienteListView, ClienteUpdateView,
)

app_name = 'customers'
urlpatterns = [
    path('', ClienteListView.as_view(), name='cliente_list'),
    path('create/', ClienteCreateView.as_view(), name='cliente_create'),
    path('<int:pk>/edit/', ClienteUpdateView.as_view(), name='cliente_update'),
    path('<int:pk>/deactivate/', ClienteDeactivateView.as_view(), name='cliente_deactivate'),
]