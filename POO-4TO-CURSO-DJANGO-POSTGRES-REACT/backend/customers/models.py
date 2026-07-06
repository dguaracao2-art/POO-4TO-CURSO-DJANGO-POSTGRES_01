from django.db import models
from core.models import BaseModel


class Cliente(BaseModel):
    cedula = models.CharField('Cédula/RUC', max_length=13, unique=True)
    nombre = models.CharField('Nombre', max_length=200)
    email = models.EmailField('Email', unique=True)
    telefono = models.CharField('Teléfono', max_length=20, blank=True)
    direccion = models.TextField('Dirección', blank=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.cedula})'