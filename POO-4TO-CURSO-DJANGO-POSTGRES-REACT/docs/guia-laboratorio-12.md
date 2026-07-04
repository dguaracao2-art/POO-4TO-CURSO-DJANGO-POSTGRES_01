# Guía de Laboratorio 12 — Reportes Profesionales PDF

## Objetivo

Implementar la generación de reportes profesionales en PDF utilizando xhtml2pdf, incluyendo cierre diario, listado de facturas por periodo y descarga de factura individual.

## Duración estimada

2 horas (presencial) + 1 hora (trabajo autónomo)

## Prerrequisitos

- Lab 09 completado (Facturación ACID con datos históricos)
- Lab 10 completado (Dashboard funcional)
- Python 3.12, Django 6.0.6, MySQL configurado

## User Stories

| ID | Historia | Pts |
|----|----------|:---:|
| HU-46 | Como **administrador** quiero generar un reporte PDF de cierre diario con totales, métodos de pago y detalle de facturas | 3 |
| HU-47 | Como **administrador** quiero generar un listado PDF de facturas por período con resumen de totales | 2 |
| HU-48 | Como **vendedor** quiero descargar una factura en PDF desde su detalle para entregarla al cliente | 2 |

---

## Estructura de archivos

```
backend/
├── invoicing/
│   ├── report_views.py                (NUEVO)
│   ├── urls.py                        (MODIFICAR)
│   ├── static/invoicing/css/
│   │   └── invoice-pdf.css            (NUEVO)
│   └── templates/invoicing/reports/
│       ├── index.html                 (NUEVO)
│       ├── daily_close_pdf.html       (NUEVO)
│       └── invoice_list_pdf.html      (NUEVO)
└── templates/invoicing/
    └── invoice_detail.html            (MODIFICAR)
```

---

## Fase 1 — Instalar dependencia

```bash
cd backend
source .venv/Scripts/activate
pip install xhtml2pdf
pip freeze > requirements.txt
```

**xhtml2pdf** es una librería pure Python que convierte HTML + CSS a PDF. No requiere dependencias del sistema operativo.

---

## Fase 2 — Crear directorios

```bash
mkdir -p invoicing/static/invoicing/css
mkdir -p invoicing/templates/invoicing/reports
```

---

## Fase 3 — CSS para PDF

**Paso 3.1:** Crea `invoicing/static/invoicing/css/invoice-pdf.css`:

```css
@page {
  size: A4;
  margin: 2cm 1.5cm;
  @bottom-center {
    content: "Pagina " counter(page) " de " counter(pages);
    font-size: 8px;
    color: #94a3b8;
    font-family: 'Segoe UI', Arial, sans-serif;
  }
}

body {
  font-family: 'Segoe UI', Arial, Helvetica, sans-serif;
  font-size: 10px;
  color: #1e293b;
  line-height: 1.8;
  margin: 0;
  padding: 0;
}

.brand-header {
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  color: #fff;
  padding: 18px 24px;
  margin-bottom: 16px;
}

.brand-header h1 {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 2px 0;
}

.brand-header .brand-sub {
  font-size: 10px;
  opacity: 0.75;
  font-weight: 300;
  letter-spacing: 1px;
}

.brand-header .brand-meta {
  font-size: 8px;
  opacity: 0.6;
  margin-top: 3px;
}

.report-title {
  text-align: center;
  margin: 0 0 14px 0;
  padding-bottom: 10px;
  border-bottom: 2px solid #e2e8f0;
}

.report-title h2 {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 3px 0;
}

.report-title .period {
  font-size: 10px;
  color: #64748b;
  margin: 0;
}

.summary-grid {
  margin-bottom: 14px;
}

.summary-grid table.nogrid {
  width: 100%;
  border: none;
  border-collapse: collapse;
}

.summary-grid table.nogrid td {
  border: none;
  padding: 4px;
  vertical-align: top;
  width: 25%;
}

.summary-card {
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 10px 6px;
  text-align: center;
  background: #fafbfc;
}

.summary-card .label {
  font-size: 7.5px;
  text-transform: uppercase;
  color: #64748b;
  letter-spacing: 0.8px;
  font-weight: 600;
}

.summary-card .value {
  font-size: 16px;
  font-weight: 700;
  margin-top: 2px;
  color: #1e293b;
}

.summary-card.card-primary .value { color: #4e73df; }
.summary-card.card-success .value { color: #059669; }
.summary-card.card-warning .value { color: #d97706; }
.summary-card.card-danger .value { color: #dc2626; }

.section-title {
  font-size: 11px;
  font-weight: 700;
  color: #1e293b;
  margin: 14px 0 6px 0;
  padding-bottom: 4px;
  border-bottom: 1px solid #e2e8f0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

table.data {
  width: 100%;
  margin: 6px 0 10px 0;
  border: 1px solid #94a3b8;
}

table.data thead th {
  background: #1e293b;
  color: #ffffff;
  font-size: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
  border: 1px solid #334155;
  border-bottom: 2px solid #4e73df;
}

table.data tbody td {
  border: 1px solid #cbd5e1;
  font-size: 9px;
}

table.data tbody tr:nth-child(even) {
  background: #f8fafc;
}

.text-end { text-align: right; }
.text-center { text-align: center; }
.fw-bold { font-weight: 700; }

.badge {
  display: inline-block;
  padding: 2px 8px;
  font-size: 7px;
  border-radius: 3px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.badge-success {
  background: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.badge-danger {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.totals-box {
  margin: 12px 0 0 0;
  padding: 10px 16px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  text-align: right;
}

.totals-box .line {
  padding: 3px 0;
  font-size: 10px;
  color: #475569;
  line-height: 1.8;
}

.totals-box .line.total {
  font-size: 14px;
  font-weight: 700;
  color: #1e293b;
  border-top: 2px solid #4e73df;
  padding-top: 6px;
  margin-top: 4px;
}

.totals-box .line.total span:last-child {
  color: #059669;
}

.report-footer {
  margin-top: 20px;
  padding-top: 8px;
  border-top: 1px solid #e2e8f0;
  text-align: center;
}

.report-footer p {
  font-size: 7.5px;
  color: #94a3b8;
  margin: 1px 0;
}

.report-footer .footer-brand {
  font-size: 9px;
  font-weight: 600;
  color: #4e73df;
}
```

---

## Fase 4 — Vistas PDF

**Paso 4.1:** Crea `invoicing/report_views.py`:

```python
from io import BytesIO
from datetime import datetime, timedelta
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView
from xhtml2pdf import pisa
from .models import Factura


class PDFMixin:
    pdf_template = None
    pdf_filename = 'reporte.pdf'

    def render_pdf(self, context):
        html_str = self.render_to_string(self.pdf_template, context)
        result = BytesIO()
        pdf = pisa.pisaDocument(
            BytesIO(html_str.encode('UTF-8')),
            dest=result,
            encoding='UTF-8',
            link_callback=self._link_callback,
        )
        if pdf.err:
            return HttpResponse('Error al generar PDF', status=500)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{self.pdf_filename}"'
        response.write(result.getvalue())
        return response

    def _link_callback(self, uri, rel):
        import os
        from django.conf import settings
        if uri.startswith(settings.STATIC_URL):
            path = os.path.join(settings.BASE_DIR, uri.replace(settings.STATIC_URL, '').lstrip('/'))
            if not os.path.exists(path):
                path = os.path.join(
                    settings.STATICFILES_DIRS[0],
                    uri.replace(settings.STATIC_URL, '').lstrip('/')
                )
            return path
        return uri

    def render_to_string(self, template, context):
        from django.template.loader import render_to_string
        return render_to_string(template, context, request=self.request)


class ReportsIndexView(LoginRequiredMixin, TemplateView):
    template_name = 'invoicing/reports/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['today'] = timezone.now()
        return ctx


class DailyClosePDFView(LoginRequiredMixin, PermissionRequiredMixin, View, PDFMixin):
    permission_required = 'invoicing.view_factura'
    pdf_template = 'invoicing/reports/daily_close_pdf.html'

    def get(self, request):
        hoy = timezone.now().date()
        inicio = timezone.make_aware(datetime.combine(hoy, datetime.min.time()))
        fin = inicio + timedelta(days=1)
        self.pdf_filename = f'cierre_diario_{hoy.strftime("%Y%m%d")}.pdf'

        facturas = Factura.all_objects.filter(
            fecha_emision__gte=inicio, fecha_emision__lt=fin
        ).select_related('cliente').order_by('fecha_emision')

        activas = facturas.filter(is_active=True)
        resumen = activas.aggregate(
            total=Sum('total'), subtotal=Sum('subtotal'),
            iva=Sum('iva_total'), cantidad=Count('id'),
        )
        por_metodo = list(activas.values('metodo_pago').annotate(
            total=Sum('total'), cantidad=Count('id')
        ).order_by('metodo_pago'))

        return self.render_pdf({
            'fecha': hoy,
            'facturas': facturas,
            'activas': activas,
            'resumen': resumen,
            'por_metodo': por_metodo,
            'anuladas': facturas.filter(is_active=False).count(),
        })


class InvoiceListPDFView(LoginRequiredMixin, PermissionRequiredMixin, View, PDFMixin):
    permission_required = 'invoicing.view_factura'
    pdf_template = 'invoicing/reports/invoice_list_pdf.html'

    def get(self, request):
        desde = request.GET.get('desde')
        hasta = request.GET.get('hasta')
        hoy = timezone.now().date()

        if desde:
            inicio = timezone.make_aware(datetime.combine(
                datetime.strptime(desde, '%Y-%m-%d').date(), datetime.min.time()))
        else:
            inicio = timezone.make_aware(datetime.combine(hoy.replace(day=1), datetime.min.time()))

        if hasta:
            fin = timezone.make_aware(datetime.combine(
                datetime.strptime(hasta, '%Y-%m-%d').date(), datetime.min.time())) + timedelta(days=1)
        else:
            fin = timezone.make_aware(datetime.combine(hoy, datetime.min.time())) + timedelta(days=1)

        facturas = Factura.all_objects.filter(
            fecha_emision__gte=inicio, fecha_emision__lt=fin
        ).select_related('cliente').order_by('-fecha_emision')

        activas = facturas.filter(is_active=True)
        resumen = activas.aggregate(
            total=Sum('total'), subtotal=Sum('subtotal'),
            iva=Sum('iva_total'), cantidad=Count('id'),
        )

        self.pdf_filename = f'facturas_{inicio.strftime("%Y%m%d")}_al_{fin.strftime("%Y%m%d")}.pdf'

        return self.render_pdf({
            'facturas': facturas,
            'activas': activas,
            'resumen': resumen,
            'anuladas': facturas.filter(is_active=False).count(),
            'desde': inicio.date(),
            'hasta': (fin - timedelta(days=1)).date(),
        })
```

---

## Fase 5 — Templates PDF

**Paso 5.1:** Crea `invoicing/templates/invoicing/reports/index.html`:

```html
{% extends "admin/base_admin.html" %}
{% load static %}
{% block title %}Reportes{% endblock %}
{% block page_title %}Reportes{% endblock %}

{% block content %}
<div class="row g-4">
  <div class="col-12">
    <p class="text-muted">Genere reportes profesionales en PDF con los datos del sistema.</p>
  </div>

  <div class="col-12 col-md-6">
    <div class="card border-0 shadow-sm h-100">
      <div class="card-body text-center p-4">
        <i class="bi bi-file-earmark-pdf display-5 text-danger d-block mb-3"></i>
        <h5 class="fw-bold">Cierre del Dia</h5>
        <p class="small text-muted mb-3">Resumen completo de ventas del dia actual: totales, metodos de pago, detalle de cada factura emitida y anulada.</p>
        <a href="{% url 'invoicing:daily_close_pdf' %}" class="btn btn-danger" target="_blank">
          <i class="bi bi-download me-1"></i> Generar PDF
        </a>
      </div>
    </div>
  </div>

  <div class="col-12 col-md-6">
    <div class="card border-0 shadow-sm h-100">
      <div class="card-body text-center p-4">
        <i class="bi bi-list-check display-5 text-success d-block mb-3"></i>
        <h5 class="fw-bold">Listado de Facturas</h5>
        <p class="small text-muted mb-3">Exporte el listado completo de facturas de un periodo especifico con totales, subtotales, IVA y resumen general.</p>
        <form method="get" action="{% url 'invoicing:invoice_list_pdf' %}" target="_blank">
          <div class="row g-2 mb-3">
            <div class="col-6">
              <label class="form-label small text-muted mb-1">Desde</label>
              <input type="date" name="desde" class="form-control form-control-sm" value="{{ today|date:'Y-m-01' }}">
            </div>
            <div class="col-6">
              <label class="form-label small text-muted mb-1">Hasta</label>
              <input type="date" name="hasta" class="form-control form-control-sm" value="{{ today|date:'Y-m-d' }}">
            </div>
          </div>
          <button type="submit" class="btn btn-success w-100">
            <i class="bi bi-download me-1"></i> Generar PDF
          </button>
        </form>
      </div>
    </div>
  </div>
</div>
{% endblock %}
```

**Paso 5.2:** Crea `invoicing/templates/invoicing/reports/daily_close_pdf.html`:

```html
{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Cierre Diario {{ fecha|date:'d/m/Y' }}</title>
  <link href="{% static 'invoicing/css/invoice-pdf.css' %}" rel="stylesheet">
</head>
<body>
  <div class="brand-header">
    <h1>Comercial "El Porvenir"</h1>
    <div class="brand-sub">SISTEMA DE FACTURACION</div>
    <div class="brand-meta">RUC: 1799999999001 | Av. Principal s/n | Tel: 0999999999</div>
  </div>

  <div class="report-title">
    <h2>Reporte de Cierre Diario</h2>
    <p class="period">{{ fecha|date:'l, d \d\e F \d\e Y' }}</p>
  </div>

  <div class="summary-grid">
    <table class="nogrid">
      <tr>
        <td><div class="summary-card card-primary"><div class="label">Facturas Emitidas</div><div class="value">{{ resumen.cantidad|default:0 }}</div></div></td>
        <td><div class="summary-card card-success"><div class="label">Subtotal</div><div class="value">${{ resumen.subtotal|default:0|floatformat:2 }}</div></div></td>
        <td><div class="summary-card card-warning"><div class="label">IVA Total</div><div class="value">${{ resumen.iva|default:0|floatformat:2 }}</div></div></td>
        <td><div class="summary-card card-danger"><div class="label">Total Ventas</div><div class="value">${{ resumen.total|default:0|floatformat:2 }}</div></div></td>
      </tr>
    </table>
  </div>

  {% if por_metodo %}
  <div class="section-title">Totales por Metodo de Pago</div>
  <table class="data" border="1">
    <thead>
      <tr>
        <th style="padding:5px 10px 5px 10px;">Metodo</th>
        <th style="padding:5px 10px 5px 10px;text-align:center;">Cant</th>
        <th style="padding:5px 10px 5px 10px;text-align:right;">Total</th>
        <th style="padding:5px 10px 5px 10px;">Distribucion</th>
      </tr>
    </thead>
    <tbody>
      {% for m in por_metodo %}
      {% widthratio m.total resumen.total|default:1 100 as porcentaje %}
      <tr>
        <td style="padding:4px 10px 4px 10px;"><span class="fw-bold">{{ m.metodo_pago }}</span></td>
        <td style="padding:4px 10px 4px 10px;text-align:center;">{{ m.cantidad }}</td>
        <td style="padding:4px 10px 4px 10px;text-align:right;">${{ m.total|floatformat:2 }}</td>
        <td style="padding:4px 10px 4px 10px;">
          <div style="background:#e2e8f0;border-radius:4px;height:8px;width:100%;overflow:hidden;">
            <div style="background:#4e73df;height:8px;width:{{ porcentaje }}%;border-radius:4px;"></div>
          </div>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  {% endif %}

  <div class="section-title">Detalle de Facturas</div>
  <table class="data" border="1">
    <thead>
      <tr>
        <th style="padding:5px 10px 5px 10px;">N° Factura</th>
        <th style="padding:5px 10px 5px 10px;">Cliente</th>
        <th style="padding:5px 10px 5px 10px;text-align:center;">Hora</th>
        <th style="padding:5px 10px 5px 10px;">Metodo</th>
        <th style="padding:5px 10px 5px 10px;text-align:right;">Subtotal</th>
        <th style="padding:5px 10px 5px 10px;text-align:right;">IVA</th>
        <th style="padding:5px 10px 5px 10px;text-align:right;">Total</th>
        <th style="padding:5px 10px 5px 10px;text-align:center;">Estado</th>
      </tr>
    </thead>
    <tbody>
      {% for f in facturas %}
      <tr>
        <td style="padding:4px 10px 4px 10px;"><span class="fw-bold">{{ f.numero }}</span></td>
        <td style="padding:4px 10px 4px 10px;">{{ f.cliente.nombre }}</td>
        <td style="padding:4px 10px 4px 10px;text-align:center;">{{ f.fecha_emision|date:'H:i' }}</td>
        <td style="padding:4px 10px 4px 10px;">{{ f.metodo_pago }}</td>
        <td style="padding:4px 10px 4px 10px;text-align:right;">${{ f.subtotal|floatformat:2 }}</td>
        <td style="padding:4px 10px 4px 10px;text-align:right;">${{ f.iva_total|floatformat:2 }}</td>
        <td style="padding:4px 10px 4px 10px;text-align:right;font-weight:700;">${{ f.total|floatformat:2 }}</td>
        <td style="padding:4px 10px 4px 10px;text-align:center;">
          {% if f.is_active %}<span class="badge badge-success">ACTIVA</span>{% else %}<span class="badge badge-danger">ANULADA</span>{% endif %}
        </td>
      </tr>
      {% empty %}
      <tr><td colspan="8" style="padding:20px;text-align:center;color:#94a3b8;">No se registraron facturas en este dia.</td></tr>
      {% endfor %}
    </tbody>
  </table>

  <div class="totals-box">
    <div class="line">Facturas: {{ facturas.count }} | Activas: {{ resumen.cantidad|default:0 }} | Anuladas: {{ anuladas }}</div>
    <div class="line">Subtotal: ${{ resumen.subtotal|default:0|floatformat:2 }}</div>
    <div class="line">IVA 15%: ${{ resumen.iva|default:0|floatformat:2 }}</div>
    <div class="line total">TOTAL VENTAS DEL DIA: ${{ resumen.total|default:0|floatformat:2 }}</div>
  </div>

  <div class="report-footer">
    <p class="footer-brand">SIF — Sistema de Facturacion</p>
    <p>Documento generado el {% now "d/m/Y \a \l\a\s H:i" %}</p>
    <p>Este documento es un reporte interno de uso administrativo.</p>
  </div>
</body>
</html>
```

**Paso 5.3:** Crea `invoicing/templates/invoicing/reports/invoice_list_pdf.html`:

```html
{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Listado de Facturas {{ desde|date:'d/m/Y' }} - {{ hasta|date:'d/m/Y' }}</title>
  <link href="{% static 'invoicing/css/invoice-pdf.css' %}" rel="stylesheet">
</head>
<body>
  <div class="brand-header">
    <h1>Comercial "El Porvenir"</h1>
    <div class="brand-sub">SISTEMA DE FACTURACION</div>
    <div class="brand-meta">RUC: 1799999999001 | Av. Principal s/n | Tel: 0999999999</div>
  </div>

  <div class="report-title">
    <h2>Listado de Facturas</h2>
    <p class="period">Del {{ desde|date:'d/m/Y' }} al {{ hasta|date:'d/m/Y' }}</p>
  </div>

  <div class="summary-grid">
    <table class="nogrid">
      <tr>
        <td><div class="summary-card card-primary"><div class="label">Total Facturas</div><div class="value">{{ facturas.count }}</div></div></td>
        <td><div class="summary-card card-success"><div class="label">Activas</div><div class="value">{{ resumen.cantidad|default:0 }}</div></div></td>
        <td><div class="summary-card card-warning"><div class="label">Anuladas</div><div class="value">{{ anuladas }}</div></div></td>
        <td><div class="summary-card card-danger"><div class="label">Total Vendido</div><div class="value">${{ resumen.total|default:0|floatformat:0 }}</div></div></td>
      </tr>
    </table>
  </div>

  <div class="section-title">Detalle de Facturas del Periodo</div>
  <table class="data" border="1">
    <thead>
      <tr>
        <th style="padding:5px 10px 5px 10px;">N° Factura</th>
        <th style="padding:5px 10px 5px 10px;">Fecha</th>
        <th style="padding:5px 10px 5px 10px;">Cliente</th>
        <th style="padding:5px 10px 5px 10px;">Metodo</th>
        <th style="padding:5px 10px 5px 10px;text-align:right;">Subtotal</th>
        <th style="padding:5px 10px 5px 10px;text-align:right;">IVA</th>
        <th style="padding:5px 10px 5px 10px;text-align:right;">Total</th>
        <th style="padding:5px 10px 5px 10px;text-align:center;">Estado</th>
      </tr>
    </thead>
    <tbody>
      {% for f in facturas %}
      <tr>
        <td style="padding:4px 10px 4px 10px;"><span class="fw-bold">{{ f.numero }}</span></td>
        <td style="padding:4px 10px 4px 10px;">{{ f.fecha_emision|date:'d/m/Y' }}</td>
        <td style="padding:4px 10px 4px 10px;">{{ f.cliente.nombre }}</td>
        <td style="padding:4px 10px 4px 10px;">{{ f.metodo_pago }}</td>
        <td style="padding:4px 10px 4px 10px;text-align:right;">${{ f.subtotal|floatformat:2 }}</td>
        <td style="padding:4px 10px 4px 10px;text-align:right;">${{ f.iva_total|floatformat:2 }}</td>
        <td style="padding:4px 10px 4px 10px;text-align:right;font-weight:700;">${{ f.total|floatformat:2 }}</td>
        <td style="padding:4px 10px 4px 10px;text-align:center;">
          {% if f.is_active %}<span class="badge badge-success">ACTIVA</span>{% else %}<span class="badge badge-danger">ANULADA</span>{% endif %}
        </td>
      </tr>
      {% empty %}
      <tr><td colspan="8" style="padding:20px;text-align:center;color:#94a3b8;">No se encontraron facturas en el periodo.</td></tr>
      {% endfor %}
    </tbody>
  </table>

  {% if facturas %}
  <div class="totals-box">
    <div class="line">Facturas: {{ facturas.count }} | Activas: {{ resumen.cantidad|default:0 }} | Anuladas: {{ anuladas }}</div>
    <div class="line">Subtotal: ${{ resumen.subtotal|default:0|floatformat:2 }}</div>
    <div class="line">IVA: ${{ resumen.iva|default:0|floatformat:2 }}</div>
    <div class="line total">TOTAL DEL PERIODO: ${{ resumen.total|default:0|floatformat:2 }}</div>
  </div>
  {% endif %}

  <div class="report-footer">
    <p class="footer-brand">SIF — Sistema de Facturacion</p>
    <p>Documento generado el {% now "d/m/Y \a \l\a\s H:i" %}</p>
    <p>Este documento es un reporte interno de uso administrativo.</p>
  </div>
</body>
</html>
```

---

## Fase 6 — Agregar rutas

**Paso 6.1:** Abre `invoicing/urls.py` y agrega los imports y rutas de los reportes:

```python
from .report_views import (
    DailyClosePDFView, InvoiceListPDFView, ReportsIndexView,
)

# Al final de urlpatterns, agrega:
path('reports/', ReportsIndexView.as_view(), name='reports_index'),
path('reports/daily-close/', DailyClosePDFView.as_view(), name='daily_close_pdf'),
path('reports/invoice-list/', InvoiceListPDFView.as_view(), name='invoice_list_pdf'),
```

---

## Fase 7 — Botón PDF en detalle de factura

**Paso 7.1:** Abre `templates/invoicing/invoice_detail.html` y agrega el botón antes de las acciones:

```html
<a href="{% url 'invoicing:invoice_pdf' factura.pk %}" class="btn btn-primary w-100 mb-2" target="_blank">
  <i class="bi bi-file-earmark-pdf"></i> Descargar PDF
</a>
```

---

## Fase 8 — Actualizar menú

```bash
python manage.py shell
```

```python
from core.models import MenuItem
MenuItem.all_objects.filter(name='Reportes').update(url_name='invoicing:reports_index')
exit()
```

---

## Fase 9 — Verificar

```bash
python manage.py check
python manage.py runserver
```

| # | Prueba | Resultado esperado |
|---|--------|-------------------|
| 1 | `/invoicing/reports/` | Página con 2 tarjetas de reportes |
| 2 | "Cierre del Día" | Descarga PDF con datos del día |
| 3 | "Listado de Facturas" con fechas | Descarga PDF filtrado por período |
| 4 | PDF tiene header con gradiente oscuro | ✅ |
| 5 | Tablas con bordes y cabecera oscura | ✅ |
| 6 | Totales correctos en caja resumen | ✅ |
| 7 | Botón PDF en detalle de factura | ✅ |
| 8 | Menú "Reportes" → `/invoicing/reports/` | ✅ |

---

## Cierre

| Lab | Tema |
|-----|------|
| Lab 12 | Reportes Profesionales PDF |

**Siguiente:** Proyecto completado — revisar [Verificación Final](./guia-laboratorio-11.md)
