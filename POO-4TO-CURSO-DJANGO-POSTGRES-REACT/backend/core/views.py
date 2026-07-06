from datetime import date, timedelta
from django.db.models import Count, F, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.views.generic import TemplateView
from catalog.models import Producto
from customers.models import Cliente
from invoicing.models import Factura


class DashboardView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        hoy = timezone.now().date()
        inicio_mes = hoy.replace(day=1)

        ctx['facturas_hoy'] = Factura.objects.filter(
            fecha_emision__date=hoy, is_active=True
        ).count()

        ventas_mes = Factura.objects.filter(
            fecha_emision__date__gte=inicio_mes, is_active=True
        ).aggregate(total=Sum('total'))
        ctx['ventas_mes'] = ventas_mes['total'] or 0

        ctx['total_clientes'] = Cliente.objects.count()
        ctx['stock_bajo'] = Producto.objects.filter(stock__lt=F('stock_minimo')).count()

        ctx['ultimas_facturas'] = Factura.objects.select_related('cliente').filter(
            is_active=True
        ).order_by('-fecha_emision')[:5]

        desde = hoy - timedelta(days=6)
        ventas_por_dia = Factura.objects.filter(
            fecha_emision__date__gte=desde, is_active=True
        ).annotate(
            dia=TruncDate('fecha_emision')
        ).values('dia').annotate(
            total=Sum('total')
        ).order_by('dia')

        dias = {str(v['dia']): float(v['total']) for v in ventas_por_dia}
        labels = [(desde + timedelta(days=i)).strftime('%d/%m') for i in range(7)]
        data = [dias.get((desde + timedelta(days=i)).strftime('%Y-%m-%d'), 0) for i in range(7)]

        ctx['chart_labels'] = labels
        ctx['chart_data'] = data
        return ctx