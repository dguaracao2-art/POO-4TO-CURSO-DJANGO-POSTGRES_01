from django.contrib import admin
from .models import DetalleFactura, Factura, SecuenciaFactura

@admin.register(SecuenciaFactura)
class SecuenciaFacturaAdmin(admin.ModelAdmin):
    list_display = ['year', 'correlativo']