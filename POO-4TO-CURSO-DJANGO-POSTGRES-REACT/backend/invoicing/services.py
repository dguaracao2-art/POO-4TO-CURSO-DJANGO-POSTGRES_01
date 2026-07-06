from decimal import Decimal
from django.db import transaction
from django.db.models import F
from django.core.exceptions import ValidationError
from django.utils import timezone
from catalog.models import Producto
from .models import DetalleFactura, Factura, SecuenciaFactura


class FacturaService:
    """Lógica de negocio transaccional (SRP: facturación)."""

    @staticmethod
    @transaction.atomic
    def crear(*, cliente, usuario, productos_data, metodo_pago='Efectivo', observaciones=''):
        """
        productos_data: list[dict] = [
            {'producto_id': 1, 'cantidad': 2, 'descuento_pct': 0},
        ]
        """
        if not productos_data:
            raise ValidationError('Debe agregar al menos un producto.')

        # Número secuencial atómico (sin race condition)
        year = timezone.now().year
        seq, _ = SecuenciaFactura.objects.select_for_update().get_or_create(year=year)
        seq.correlativo = F('correlativo') + 1
        seq.save()
        seq.refresh_from_db()
        numero = f"FAC-{seq.year}-{seq.correlativo:06d}"

        detalles_data = []
        subtotal_factura = Decimal('0.00')
        iva_factura = Decimal('0.00')

        for item in productos_data:
            prod = Producto.objects.get(pk=item['producto_id'])

            if item['cantidad'] <= 0:
                raise ValidationError(f'Cantidad inválida para {prod.nombre}')

            if prod.stock < item['cantidad']:
                raise ValidationError(f'Stock insuficiente para {prod.nombre} ( disponible: {prod.stock} )')

            # Calcular línea
            p_unitario = prod.precio
            desc = Decimal(str(item.get('descuento_pct', 0)))
            subt = Decimal(str(item['cantidad'])) * p_unitario * (1 - desc / Decimal('100'))
            iva_p = prod.iva_porcentaje
            iva_v = subt * iva_p / Decimal('100')
            tot = subt + iva_v

            detalles_data.append({
                'producto': prod,
                'cantidad': item['cantidad'],
                'precio_unitario': p_unitario,
                'descuento_pct': desc,
                'subtotal': subt.quantize(Decimal('0.01')),
                'iva_porcentaje': iva_p,
                'iva_valor': iva_v.quantize(Decimal('0.01')),
                'total': tot.quantize(Decimal('0.01')),
            })

            subtotal_factura += subt
            iva_factura += iva_v

            # 4. Descontar stock (atómico con F())
            rows = Producto.objects.filter(pk=prod.pk, stock__gte=item['cantidad']).update(
                stock=F('stock') - item['cantidad']
            )
            if rows == 0:
                raise ValidationError(f'Error al descontar stock de {prod.nombre} (posible race condition)')

        # 5. Crear factura
        factura = Factura.objects.create(
            numero=numero,
            cliente=cliente,
            usuario=usuario,
            subtotal=subtotal_factura.quantize(Decimal('0.01')),
            iva_total=iva_factura.quantize(Decimal('0.01')),
            total=(subtotal_factura + iva_factura).quantize(Decimal('0.01')),
            metodo_pago=metodo_pago,
            observaciones=observaciones,
        )

        # 6. Crear detalles en bulk
        DetalleFactura.objects.bulk_create([
            DetalleFactura(factura=factura, **d) for d in detalles_data
        ])

        return factura

    @staticmethod
    @transaction.atomic
    def anular(factura_id):
        factura = Factura.all_objects.select_for_update().get(pk=factura_id)

        if not factura.is_active:
            raise ValidationError('La factura ya está anulada.')

        # Restaurar stock por cada detalle
        for det in factura.detalles.all():
            from catalog.models import Producto
            Producto.objects.filter(pk=det.producto_id).update(
                stock=F('stock') + det.cantidad
            )

        factura.soft_delete()
        return factura