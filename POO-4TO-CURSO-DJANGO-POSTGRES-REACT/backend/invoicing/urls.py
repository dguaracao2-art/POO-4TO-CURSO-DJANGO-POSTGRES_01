from django.urls import path
from .views import (
    InvoiceAnnulView,
    InvoiceCreateView,
    InvoiceDetailView,
    InvoiceListView,
    api_productos,
    api_clientes,
)
app_name = 'invoicing'
urlpatterns = [
    path('', InvoiceListView.as_view(), name='invoice_list'),
    path('create/', InvoiceCreateView.as_view(), name='invoice_create'),
    path('<int:pk>/', InvoiceDetailView.as_view(), name='invoice_detail'),
    path('<int:pk>/annul/', InvoiceAnnulView.as_view(), name='invoice_annul'),
        path('api/productos/', api_productos, name='api_productos'),
    path('api/clientes/', api_clientes, name='api_clientes'),
]