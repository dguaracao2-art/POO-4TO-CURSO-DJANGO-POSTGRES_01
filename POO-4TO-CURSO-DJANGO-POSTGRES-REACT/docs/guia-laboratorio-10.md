# Guía de Laboratorio 10 — Dashboard con Chart.js

## Objetivo

Crear un dashboard profesional con tarjetas de resumen, gráfico de ventas (Chart.js), últimas facturas y accesos directos a los módulos principales.

## Duración estimada

1.5 horas (presencial) + 1 hora (trabajo autónomo)

## Prerrequisitos

- Lab 09 completado (facturación con datos históricos)
- Lab 05 completado (admin layout con sidebar)

## User Stories

| ID | Historia | Pts |
|----|----------|:---:|
| HU-39 | Como **usuario** quiero tarjetas de resumen (facturas hoy, ventas mes, clientes, stock bajo) | 3 |
| HU-40 | Como **admin** quiero gráfico de ventas por día con Chart.js | 3 |
| HU-41 | Como **usuario** quiero ver últimas 5 facturas | 2 |
| HU-42 | Como **vendedor** quiero accesos directos a Nueva Factura y Buscar Cliente | 1 |

---

## Estructura

```
backend/
├── templates/
│   └── index.html                    (MODIFICAR) — dashboard completo
└── core/
    └── views.py                      (NUEVO) — DashboardView con datos agregados
```

---

## Fase 1 — Vista del Dashboard

**Paso 1.1:** Crea `core/views.py`:

```python
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
```

---

## Fase 2 — Actualizar URL

En `config/urls.py`, cambia la ruta home para que use `DashboardView`:

```python
from core.views import DashboardView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", DashboardView.as_view(), name="home"),
    path("security/", include("security.urls")),
    ...
]
```

---

## Fase 3 — Template del Dashboard

**Paso 3.1:** Reemplaza `templates/index.html`:

```html
{% extends "admin/base_admin.html" %}
{% load static %}
{% block title %}Dashboard{% endblock %}
{% block page_title %}Panel Principal{% endblock %}
{% block page_subtitle %}{% now "d/m/Y" %}{% endblock %}

{% block content %}
<!-- Accesos rápidos -->
<div class="d-flex gap-2 mb-4 flex-wrap">
  <a href="{% url 'invoicing:invoice_create' %}" class="btn btn-primary">
    <i class="bi bi-plus-circle"></i> Nueva Factura
  </a>
  <a href="{% url 'catalog:producto_list' %}" class="btn btn-outline-primary">
    <i class="bi bi-box"></i> Catálogo
  </a>
  <a href="{% url 'customers:cliente_list' %}" class="btn btn-outline-primary">
    <i class="bi bi-people"></i> Clientes
  </a>
</div>

<!-- Tarjetas de resumen -->
<div class="row g-3 mb-4">
  <div class="col-6 col-md-3">
    <div class="card border-0 shadow-sm text-center p-3 h-100 skeleton-card">
      <i class="bi bi-receipt fs-2 text-primary d-block"></i>
      <div class="fw-bold fs-4 mt-1">{{ facturas_hoy }}</div>
      <small class="text-muted">Facturas Hoy</small>
    </div>
  </div>
  <div class="col-6 col-md-3">
    <div class="card border-0 shadow-sm text-center p-3 h-100 skeleton-card">
      <i class="bi bi-currency-dollar fs-2 text-success d-block"></i>
      <div class="fw-bold fs-4 mt-1">${{ ventas_mes|floatformat:0 }}</div>
      <small class="text-muted">Ventas del Mes</small>
    </div>
  </div>
  <div class="col-6 col-md-3">
    <div class="card border-0 shadow-sm text-center p-3 h-100 skeleton-card">
      <i class="bi bi-people fs-2 text-info d-block"></i>
      <div class="fw-bold fs-4 mt-1">{{ total_clientes }}</div>
      <small class="text-muted">Clientes</small>
    </div>
  </div>
  <div class="col-6 col-md-3">
    <div class="card border-0 shadow-sm text-center p-3 h-100 skeleton-card">
      <i class="bi bi-exclamation-triangle fs-2 text-warning d-block"></i>
      <div class="fw-bold fs-4 mt-1">{{ stock_bajo }}</div>
      <small class="text-muted">Stock Bajo</small>
    </div>
  </div>
</div>

<div class="row g-4">
  <!-- Gráfico de ventas -->
  <div class="col-12 col-lg-8">
    <div class="card border-0 shadow-sm">
      <div class="card-body p-4">
        <h6 class="fw-bold mb-3"><i class="bi bi-graph-up me-2"></i>Ventas Últimos 7 Días</h6>
        <canvas id="ventasChart" height="200"></canvas>
      </div>
    </div>
  </div>

  <!-- Últimas facturas -->
  <div class="col-12 col-lg-4">
    <div class="card border-0 shadow-sm">
      <div class="card-body p-4">
        <h6 class="fw-bold mb-3"><i class="bi bi-clock-history me-2"></i>Últimas Facturas</h6>
        {% for f in ultimas_facturas %}
        <div class="d-flex justify-content-between align-items-center mb-2 pb-2 border-bottom">
          <div>
            <a href="{% url 'invoicing:invoice_detail' f.pk %}" class="text-decoration-none fw-semibold small">{{ f.numero }}</a>
            <div class="small text-muted">{{ f.cliente.nombre }}</div>
          </div>
          <div class="text-end">
            <span class="fw-bold small">${{ f.total|floatformat:2 }}</span>
            <div class="small text-muted">{{ f.fecha_emision|date:'d/m' }}</div>
          </div>
        </div>
        {% empty %}
        <p class="text-muted small text-center py-3">No hay facturas recientes.</p>
        {% endfor %}
      </div>
    </div>
  </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
const ctx = document.getElementById('ventasChart').getContext('2d');
new Chart(ctx, {
  type: 'bar',
  data: {
    labels: {{ chart_labels|safe }},
    datasets: [{
      label: 'Ventas ($)',
      data: {{ chart_data|safe }},
      backgroundColor: 'rgba(78, 115, 223, 0.5)',
      borderColor: '#4e73df',
      borderWidth: 2,
      borderRadius: 4,
    }]
  },
  options: {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: {
      y: { beginAtZero: true, ticks: { callback: v => '$' + v } }
    }
  }
});
</script>
{% endblock %}
```

---

## Fase 4 — Verificar

```bash
python manage.py check
```

Debe mostrar: `System check identified no issues (0 silenced).`

```bash
python manage.py runserver
```

| # | Prueba | Resultado |
|---|--------|-----------|
| 1 | Dashboard muestra 4 tarjetas con datos reales | ✅ |
| 2 | "Facturas Hoy" muestra el número correcto | ✅ |
| 3 | "Ventas del Mes" suma correctamente | ✅ |
| 4 | Gráfico Chart.js se renderiza con datos de 7 días | ✅ |
| 5 | Últimas 5 facturas aparecen con enlace al detalle | ✅ |
| 6 | Botones de acceso rápido navegan a módulos | ✅ |
| 7 | Stock bajo muestra productos con stock < mínimo | ✅ |

---

## Próximo laboratorio

[**Lab 11 — Verificación Final + Despliegue**](./guia-laboratorio-11.md) con checklist de aceptación y documentación de despliegue.
