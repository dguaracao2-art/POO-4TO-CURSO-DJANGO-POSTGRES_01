from django.db import models
from core.models import BaseModel
from catalog.models import Producto
from customers.models import Cliente
from security.models import User


class Factura(BaseModel):
    METODO_PAGO = [
        ('Efectivo', 'Efectivo'),
        ('Tarjeta Débito', 'Tarjeta Débito'),
        ('Tarjeta Crédito', 'Tarjeta Crédito'),
        ('Transferencia', 'Transferencia'),
        ('Crédito', 'Crédito'),
    ]

    numero = models.CharField('Número', max_length=20, unique=True, editable=False)
    fecha_emision = models.DateTimeField('Fecha de emisión', auto_now_add=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, verbose_name='Cliente')
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Vendedor')
    subtotal = models.DecimalField('Subtotal', max_digits=12, decimal_places=2, default=0)
    iva_total = models.DecimalField('IVA Total', max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField('Total', max_digits=12, decimal_places=2, default=0)
    metodo_pago = models.CharField('Método de pago', max_length=50, choices=METODO_PAGO, default='Efectivo')
    observaciones = models.TextField('Observaciones', blank=True)

    class Meta:
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'
        ordering = ['-fecha_emision']

    def __str__(self):
        return self.numero


class DetalleFactura(BaseModel):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='detalles', verbose_name='Factura')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, verbose_name='Producto')
    cantidad = models.IntegerField('Cantidad')
    precio_unitario = models.DecimalField('Precio unitario', max_digits=10, decimal_places=2)
    descuento_pct = models.DecimalField('Descuento %', max_digits=5, decimal_places=2, default=0)
    subtotal = models.DecimalField('Subtotal', max_digits=12, decimal_places=2)
    iva_porcentaje = models.DecimalField('IVA %', max_digits=4, decimal_places=2)
    iva_valor = models.DecimalField('Valor IVA', max_digits=12, decimal_places=2)
    total = models.DecimalField('Total', max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = 'Detalle de factura'
        verbose_name_plural = 'Detalles de factura'

    def __str__(self):
        return f'{self.producto.nombre} x{self.cantidad}'


class SecuenciaFactura(models.Model):
    """Contador secuencial para números de factura (evita race conditions)."""
    year = models.IntegerField('Año', unique=True)
    correlativo = models.IntegerField('Correlativo', default=0)

    class Meta:
        verbose_name = 'Secuencia de factura'
        verbose_name_plural = 'Secuencias de factura'

    def __str__(self):
        return f'{self.year}-{self.correlativo:06d}'