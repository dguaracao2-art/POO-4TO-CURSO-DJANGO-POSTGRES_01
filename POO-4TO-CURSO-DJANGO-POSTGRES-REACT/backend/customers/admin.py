from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['cedula', 'nombre', 'email', 'telefono', 'is_active']
    search_fields = ['cedula', 'nombre', 'email']