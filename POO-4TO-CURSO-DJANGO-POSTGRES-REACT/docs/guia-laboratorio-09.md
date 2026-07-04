# Guía de Laboratorio 09 — Facturación Transaccional (ACID)

## Objetivo

Crear la app `invoicing` con modelos Factura (maestro) y DetalleFactura (detalle), servicio transaccional con `@transaction.atomic` y `F()` para descuento atómico de stock, cálculo automático de IVA, y anulación con restauración de stock.

## Duración estimada

3 horas (presencial) + 1.5 horas (trabajo autónomo)

## Prerrequisitos

- Lab 08 completado (Clientes CRUD)
- Lab 07 completado (Productos CRUD con stock)
- Lab 05 completado (sidebar + admin layout)
- Lab 04 completado (BaseModel + SoftDeleteManager)

## User Stories

| ID | Historia | Pts |
|----|----------|:---:|
| HU-34 | Como **vendedor** quiero crear factura con cliente, productos y cantidades | 5 |
| HU-35 | Stock se descuenta automáticamente con `F()` sin condiciones de carrera | 3 |
| HU-36 | IVA y subtotales se calculan automáticamente | 2 |
| HU-37 | Como **admin** quiero anular factura y restaurar stock atómicamente | 5 |
| HU-38 | Como **usuario** quiero historial de facturas con filtros | 3 |
| HU-38b | Interfaz profesional con tabla de detalles editable en vivo | 3 |

---

## Contenido

1. [Arquitectura del módulo](#arquitectura-del-módulo)
2. [Fase 1 — Modelos](#fase-1--modelos)
3. [Fase 2 — Servicio Transaccional](#fase-2--servicio-transaccional-acid)
4. [Fase 3 — Formularios](#fase-3--formularios)
5. [Fase 4 — Vistas CBV](#fase-4--vistas-cbv)
6. [Fase 5 — URLs](#fase-5--urls)
7. [Fase 6 — JavaScript SOLID](#fase-6--javascript-solid)
8. [Fase 7 — Templates](#fase-7--templates)
9. [Fase 8 — API Búsqueda AJAX](#fase-8--api-simple-para-búsqueda-ajax)
10. [Fase 9 — Migrar y Verificar](#fase-9--migrar--menú--verificar)

---

## Arquitectura del módulo

```
invoicing/
├── models.py           → Factura, DetalleFactura
├── services.py         → FacturaService.crear(), .anular() (ACID)
├── forms.py            → FacturaForm (cliente + método pago)
├── views.py            → InvoiceListView, InvoiceCreateView, InvoiceDetailView, InvoiceAnnulView
├── urls.py             → rutas RESTful
├── templates/invoicing/
│   ├── invoice_list.html
│   ├── invoice_form.html
│   └── invoice_detail.html
└── static/invoicing/js/
    ├── invoice-service.js      (lógica de negocio — SRP)
    ├── invoice-calculator.js   (cálculos financieros — SRP)
    └── invoice-form.js         (controlador DOM — SRP)
```

---

## Fase 1 — Modelos

**Paso 1.1:** Crea la app:

```bash
python manage.py startapp invoicing
```

```python
# settings.py
LOCAL_APPS = [
    "core", "security", "catalog", "customers", "invoicing",
]
```

**Paso 1.2:** `invoicing/models.py`:

```python
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
```

> **Nota:** `SecuenciaFactura` no hereda de `BaseModel` porque es un contador interno que no necesita auditoría ni soft delete.

**Paso 1.3:** Agrega el modelo a `invoicing/admin.py`:

```python
from .models import DetalleFactura, Factura, SecuenciaFactura

@admin.register(SecuenciaFactura)
class SecuenciaFacturaAdmin(admin.ModelAdmin):
    list_display = ['year', 'correlativo']
```

---

## Fase 2 — Servicio Transaccional (ACID)

**Paso 2.1:** `invoicing/services.py`:

```python
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
```

---

## Fase 3 — Formularios

**Paso 3.1:** `invoicing/forms.py`:

```python
from django import forms
from .models import Factura


class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = ['cliente', 'metodo_pago', 'observaciones']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'metodo_pago': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
```

---

## Fase 4 — Vistas CBV

**Paso 4.1:** `invoicing/views.py`:

```python
import json
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView
from .forms import FacturaForm
from .models import Factura
from .services import FacturaService


class InvoiceListView(PermissionRequiredMixin, ListView):
    permission_required = 'invoicing.view_factura'
    model = Factura
    paginate_by = 10
    template_name = 'invoicing/invoice_list.html'

    def get_queryset(self):
        qs = Factura.all_objects.select_related('cliente', 'usuario').all()
        fdesde = self.request.GET.get('desde', '').strip()
        fhasta = self.request.GET.get('hasta', '').strip()
        cliente_id = self.request.GET.get('cliente', '').strip()
        if fdesde:
            qs = qs.filter(fecha_emision__gte=fdesde)
        if fhasta:
            qs = qs.filter(fecha_emision__lte=fhasta)
        if cliente_id:
            qs = qs.filter(cliente_id=cliente_id)
        return qs.order_by('-fecha_emision')


class InvoiceCreateView(LoginRequiredMixin, View):
    template_name = 'invoicing/invoice_form.html'

    def get(self, request):
        form = FacturaForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = FacturaForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {'form': form})

        try:
            productos_data = json.loads(request.POST.get('productos_json', '[]'))
            factura = FacturaService.crear(
                cliente=form.cleaned_data['cliente'],
                usuario=request.user,
                productos_data=productos_data,
                metodo_pago=form.cleaned_data['metodo_pago'],
                observaciones=form.cleaned_data['observaciones'],
            )
            messages.success(request, f'Factura {factura.numero} creada correctamente.')
            return redirect('invoicing:invoice_detail', pk=factura.pk)
        except Exception as e:
            messages.error(request, str(e))
            return render(request, self.template_name, {'form': form})


class InvoiceDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'invoicing.view_factura'
    model = Factura
    template_name = 'invoicing/invoice_detail.html'
    context_object_name = 'factura'

    def get_queryset(self):
        return Factura.all_objects.select_related('cliente', 'usuario').all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['detalles'] = self.object.detalles.select_related('producto').all()
        return ctx


class InvoiceAnnulView(PermissionRequiredMixin, View):
    permission_required = 'invoicing.delete_factura'

    def post(self, request, pk):
        try:
            factura = FacturaService.anular(pk)
            messages.success(request, f'Factura {factura.numero} anulada. Stock restaurado.')
        except Exception as e:
            messages.error(request, str(e))
        return redirect('invoicing:invoice_list')
```

---

## Fase 5 — URLs

**Paso 5.1:** `invoicing/urls.py`:

```python
from django.urls import path
from .views import InvoiceAnnulView, InvoiceCreateView, InvoiceDetailView, InvoiceListView

app_name = 'invoicing'
urlpatterns = [
    path('', InvoiceListView.as_view(), name='invoice_list'),
    path('create/', InvoiceCreateView.as_view(), name='invoice_create'),
    path('<int:pk>/', InvoiceDetailView.as_view(), name='invoice_detail'),
    path('<int:pk>/annul/', InvoiceAnnulView.as_view(), name='invoice_annul'),
]
```

**Paso 5.2:** En `config/urls.py`:

```python
path("invoicing/", include("invoicing.urls")),
```

---

## Fase 6 — JavaScript SOLID

**Paso 6.1:** Crea `invoicing/static/invoicing/js/invoice-calculator.js`:

```javascript
class InvoiceCalculator {
  static calcLine(cantidad, precio, descuentoPct, ivaPct) {
    const subtotal = cantidad * precio * (1 - descuentoPct / 100);
    const ivaValor = subtotal * ivaPct / 100;
    const total = subtotal + ivaValor;
    return {
      subtotal: Math.round(subtotal * 100) / 100,
      ivaValor: Math.round(ivaValor * 100) / 100,
      total: Math.round(total * 100) / 100,
    };
  }

  static calcTotals(lines) {
    let subtotal = 0, iva = 0, total = 0;
    lines.forEach(l => {
      subtotal += l.subtotal;
      iva += l.ivaValor;
      total += l.total;
    });
    return {
      subtotal: Math.round(subtotal * 100) / 100,
      iva: Math.round(iva * 100) / 100,
      total: Math.round(total * 100) / 100,
    };
  }
}
```

**Paso 6.2:** Crea `invoicing/static/invoicing/js/invoice-service.js`:

```javascript
class InvoiceService {
  constructor(api) { this.api = api; }

  async buscarProductos(q) {
    return this.api.get('/invoicing/api/productos/', { q });
  }

  async buscarClientes(q) {
    return this.api.get('/invoicing/api/clientes/', { q });
  }
}
```

**Paso 6.3:** Crea `invoicing/static/invoicing/js/invoice-form.js`:

```javascript
(function () {
  const api = new ApiClient();
  const svc = new InvoiceService(api);

  // Elementos del DOM
  const els = {
    productosBody: document.getElementById('detalleBody'),
    totalSubtotal: document.getElementById('totalSubtotal'),
    totalIva: document.getElementById('totalIva'),
    totalGeneral: document.getElementById('totalGeneral'),
    productosJson: document.getElementById('productosJson'),
    searchProducto: document.getElementById('searchProducto'),
    resultsProducto: document.getElementById('resultsProducto'),
  };

  let lines = [];

  function actualizarTotales() {
    const t = InvoiceCalculator.calcTotals(lines);
    if (els.totalSubtotal) els.totalSubtotal.textContent = '$' + t.subtotal.toFixed(2);
    if (els.totalIva) els.totalIva.textContent = '$' + t.iva.toFixed(2);
    if (els.totalGeneral) els.totalGeneral.textContent = '$' + t.total.toFixed(2);
    if (els.productosJson) els.productosJson.value = JSON.stringify(
      lines.map(l => ({ producto_id: l.id, cantidad: l.cantidad, descuento_pct: l.descuentoPct }))
    );
  }

  function renderLine(index) {
    const l = lines[index];
    const calc = InvoiceCalculator.calcLine(l.cantidad, l.precio, l.descuentoPct, l.ivaPct);
    l.subtotal = calc.subtotal;
    l.ivaValor = calc.ivaValor;
    l.total = calc.total;

    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${l.codigo}</td>
      <td>${l.nombre}</td>
      <td><input type="number" class="form-control form-control-sm qty" value="${l.cantidad}" min="1" style="width:70px"></td>
      <td>$${l.precio.toFixed(2)}</td>
      <td><input type="number" class="form-control form-control-sm desc" value="${l.descuentoPct}" min="0" max="100" step="0.01" style="width:70px"></td>
      <td class="text-end">$${calc.subtotal.toFixed(2)}</td>
      <td><button type="button" class="btn btn-sm btn-outline-danger remove-line"><i class="bi bi-x"></i></button></td>
    `;
    row.dataset.index = index;

    row.querySelector('.qty').addEventListener('change', function () {
      lines[index].cantidad = parseInt(this.value) || 0;
      if (lines[index].cantidad > l.stockDisponible) this.classList.add('is-invalid');
      else this.classList.remove('is-invalid');
      renderLine(index);
      actualizarTotales();
    });
    row.querySelector('.desc').addEventListener('change', function () {
      lines[index].descuentoPct = parseFloat(this.value) || 0;
      renderLine(index);
      actualizarTotales();
    });
    row.querySelector('.remove-line').addEventListener('click', function () {
      lines.splice(index, 1);
      renderAllLines();
      actualizarTotales();
    });

    const existing = els.productosBody.children[index];
    if (existing) existing.replaceWith(row);
    else els.productosBody.appendChild(row);
  }

  function renderAllLines() {
    els.productosBody.innerHTML = '';
    lines.forEach((_, i) => renderLine(i));
  }

  function addProduct(prod) {
    if (lines.some(l => l.id === prod.id)) return;
    lines.push({
      id: prod.id, codigo: prod.codigo, nombre: prod.nombre,
      precio: parseFloat(prod.precio), ivaPct: parseFloat(prod.iva_porcentaje),
      stockDisponible: prod.stock, cantidad: 1, descuentoPct: 0,
      subtotal: 0, ivaValor: 0, total: 0,
    });
    const idx = lines.length - 1;
    renderLine(idx);
    actualizarTotales();
    if (els.resultsProducto) els.resultsProducto.innerHTML = '';
    if (els.searchProducto) els.searchProducto.value = '';
  }

  if (els.searchProducto) {
    let timeout;
    els.searchProducto.addEventListener('input', function () {
      clearTimeout(timeout);
      const q = this.value.trim();
      if (q.length < 2) { els.resultsProducto.innerHTML = ''; return; }
      timeout = setTimeout(async () => {
        const data = await svc.buscarProductos(q);
        els.resultsProducto.innerHTML = data.map(p =>
          `<a href="#" class="list-group-item list-group-item-action" data-id="${p.id}">
            <strong>${p.codigo}</strong> — ${p.nombre}
            <span class="float-end">$${parseFloat(p.precio).toFixed(2)} | Stock: ${p.stock}</span>
          </a>`
        ).join('');
        els.resultsProducto.querySelectorAll('a').forEach(a => {
          a.addEventListener('click', function (e) {
            e.preventDefault();
            const prod = data.find(p => p.id == this.dataset.id);
            if (prod) addProduct(prod);
          });
        });
      }, 300);
    });
  }

  // Si existe el formulario, inicializar
  if (els.productosBody) actualizarTotales();
})();
```

---

## Fase 7 — Templates

**Paso 7.1:** `invoicing/templates/invoicing/invoice_list.html`:

```html
{% extends "admin/base_admin.html" %}
{% block title %}Facturas{% endblock %}
{% block page_title %}Historial de Facturas{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-3">
  <form method="get" class="d-flex gap-2 flex-wrap">
    <input type="date" name="desde" class="form-control form-control-sm" style="width:auto" value="{{ request.GET.desde }}">
    <input type="date" name="hasta" class="form-control form-control-sm" style="width:auto" value="{{ request.GET.hasta }}">
    <button class="btn btn-sm btn-outline-primary"><i class="bi bi-funnel"></i> Filtrar</button>
  </form>
  <a href="{% url 'invoicing:invoice_create' %}" class="btn btn-primary btn-sm"><i class="bi bi-plus-lg"></i> Nueva Factura</a>
</div>

<div class="card border-0 shadow-sm">
  <table class="table table-hover align-middle mb-0">
    <thead class="table-light">
      <tr><th>N°</th><th>Fecha</th><th>Cliente</th><th>Subtotal</th><th>IVA</th><th>Total</th><th>Estado</th><th></th></tr>
    </thead>
    <tbody>
      {% for f in factura_list %}
      <tr>
        <td class="small">{{ f.numero }}</td>
        <td class="small">{{ f.fecha_emision|date:'d/m/Y H:i' }}</td>
        <td>{{ f.cliente.nombre }}</td>
        <td>${{ f.subtotal|floatformat:2 }}</td>
        <td>${{ f.iva_total|floatformat:2 }}</td>
        <td><strong>${{ f.total|floatformat:2 }}</strong></td>
        <td>{% if f.is_active %}<span class="badge bg-success">Activa</span>{% else %}<span class="badge bg-danger">Anulada</span>{% endif %}</td>
        <td class="text-end">
          <a href="{% url 'invoicing:invoice_detail' f.pk %}" class="btn btn-sm btn-outline-secondary"><i class="bi bi-eye"></i></a>
        </td>
      </tr>
      {% empty %}<tr><td colspan="8" class="text-center text-muted py-4">No hay facturas.</td></tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% include 'catalog/_pagination.html' %}
{% endblock %}
```

**Paso 7.2:** `invoicing/templates/invoicing/invoice_form.html` (maestro-detalle):

```html
{% extends "admin/base_admin.html" %}
{% load static %}
{% block title %}Nueva Factura{% endblock %}
{% block page_title %}Nueva Factura{% endblock %}

{% block content %}
<div class="row g-4">
  <div class="col-12 col-lg-8">
    <form method="post" id="invoiceForm">
      {% csrf_token %}
      <input type="hidden" name="productos_json" id="productosJson" value="[]">

      <div class="card border-0 shadow-sm mb-3">
        <div class="card-body p-4">
          <h6 class="fw-bold mb-3"><i class="bi bi-person me-2"></i>Datos de Factura</h6>
          <div class="row g-3">
            <div class="col-md-6">{{ form.cliente.label_tag }}{{ form.cliente }}</div>
            <div class="col-md-3">{{ form.metodo_pago.label_tag }}{{ form.metodo_pago }}</div>
            <div class="col-md-3"><label class="form-label fw-semibold">Vendedor</label><input class="form-control" value="{{ request.user.get_full_name }}" disabled></div>
          </div>
        </div>
      </div>

      <div class="card border-0 shadow-sm mb-3">
        <div class="card-body p-4">
          <h6 class="fw-bold mb-3"><i class="bi bi-box me-2"></i>Agregar Producto</h6>
          <input type="text" id="searchProducto" class="form-control" placeholder="Buscar producto por nombre o código...">
          <div id="resultsProducto" class="list-group mt-2" style="max-height:200px;overflow-y:auto">
            <div class="skeleton-text mb-2"></div>
            <div class="skeleton-text mb-2"></div>
            <div class="skeleton-text mb-2"></div>
          </div>
        </div>
      </div>

      <div class="card border-0 shadow-sm mb-3">
        <div class="card-body p-4">
          <h6 class="fw-bold mb-3"><i class="bi bi-list me-2"></i>Detalle de Factura</h6>
          <div class="table-responsive">
            <table class="table table-sm">
              <thead><tr><th>Código</th><th>Producto</th><th>Cant.</th><th>P/U</th><th>Desc.%</th><th class="text-end">Subtotal</th><th></th></tr></thead>
              <tbody id="detalleBody"></tbody>
            </table>
          </div>
          <div id="emptyDetalle" class="text-center text-muted py-3">Agregue productos usando el buscador.</div>
        </div>
      </div>

      <div class="text-end">
        {{ form.observaciones.label_tag }}{{ form.observaciones }}
      </div>
      <div class="d-flex gap-2 mt-3">
        <button type="submit" id="btnSubmit" class="btn btn-primary btn-lg"><i class="bi bi-check-lg"></i> Guardar Factura</button>
        <a href="{% url 'invoicing:invoice_list' %}" class="btn btn-outline-secondary">Cancelar</a>
      </div>
    </form>
  </div>

  <div class="col-12 col-lg-4">
    <div class="card border-0 shadow-sm sticky-top" style="top:1rem">
      <div class="card-body p-4">
        <h6 class="fw-bold mb-3">Totales</h6>
        <div class="d-flex justify-content-between mb-2"><span>Subtotal:</span><span id="totalSubtotal">$0.00</span></div>
        <div class="d-flex justify-content-between mb-2"><span>IVA 15%:</span><span id="totalIva">$0.00</span></div>
        <hr>
        <div class="d-flex justify-content-between fs-5 fw-bold"><span>TOTAL:</span><span id="totalGeneral">$0.00</span></div>
      </div>
    </div>
  </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
<script src="{% static 'security/js/api-client.js' %}"></script>
<script src="{% static 'invoicing/js/invoice-calculator.js' %}"></script>
<script src="{% static 'invoicing/js/invoice-service.js' %}"></script>
<script src="{% static 'invoicing/js/invoice-form.js' %}"></script>
<script>
document.getElementById('btnSubmit')?.addEventListener('click', function() {
  this.classList.add('skeleton-btn');
});
</script>
{% endblock %}
```

**Paso 7.3:** `invoicing/templates/invoicing/invoice_detail.html`:

```html
{% extends "admin/base_admin.html" %}
{% block title %}Factura {{ factura.numero }}{% endblock %}
{% block page_title %}Factura {{ factura.numero }}{% endblock %}

{% block content %}
<div class="row g-4">
  <div class="col-12 col-lg-8">
    <div class="card border-0 shadow-sm">
      <div class="card-body p-4">
        <div class="d-flex justify-content-between mb-4">
          <div>
            <h5 class="fw-bold mb-1">Sistema de Facturación</h5>
            <p class="text-muted small mb-0">Factura {{ factura.numero }}</p>
          </div>
          <div class="text-end">
            <p class="mb-0 small">Fecha: {{ factura.fecha_emision|date:'d/m/Y H:i' }}</p>
            <p class="mb-0 small">Vendedor: {{ factura.usuario.get_full_name }}</p>
          </div>
        </div>
        <hr>
        <p><strong>Cliente:</strong> {{ factura.cliente.nombre }}<br>
        <span class="small text-muted">{{ factura.cliente.cedula }} | {{ factura.cliente.email }}</span></p>
        <hr>
        <table class="table table-sm">
          <thead><tr><th>Producto</th><th>Cant.</th><th>P/U</th><th>Desc.%</th><th>Subtotal</th><th>IVA</th><th>Total</th></tr></thead>
          <tbody>
            {% for d in detalles %}
            <tr>
              <td>{{ d.producto.nombre }}</td>
              <td>{{ d.cantidad }}</td>
              <td>${{ d.precio_unitario|floatformat:2 }}</td>
              <td>{{ d.descuento_pct|floatformat:1 }}%</td>
              <td>${{ d.subtotal|floatformat:2 }}</td>
              <td>${{ d.iva_valor|floatformat:2 }}</td>
              <td>${{ d.total|floatformat:2 }}</td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
        <hr>
        <div class="text-end">
          <p>Subtotal: ${{ factura.subtotal|floatformat:2 }}</p>
          <p>IVA {{ factura.iva_total|floatformat:2 }}</p>
          <h4 class="fw-bold">TOTAL: ${{ factura.total|floatformat:2 }}</h4>
        </div>
        {% if factura.observaciones %}<hr><p class="small text-muted">{{ factura.observaciones }}</p>{% endif %}
      </div>
    </div>
  </div>
  <div class="col-12 col-lg-4">
    <div class="card border-0 shadow-sm">
      <div class="card-body p-4">
        <h6 class="fw-bold mb-3">Acciones</h6>
        {% if factura.is_active %}
        <form method="post" action="{% url 'invoicing:invoice_annul' factura.pk %}">
          {% csrf_token %}
          <button type="submit" id="btnSubmit" class="btn btn-danger w-100" onclick="return confirm('¿Anular esta factura? El stock se restaurará.')">
            <i class="bi bi-x-circle"></i> Anular Factura
          </button>
        </form>
        {% else %}
        <span class="badge bg-danger d-block p-2 text-center">Factura Anulada</span>
        {% endif %}
        <a href="{% url 'invoicing:invoice_list' %}" class="btn btn-outline-secondary w-100 mt-2">Volver al listado</a>
      </div>
    </div>
  </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script>
document.getElementById('btnSubmit')?.addEventListener('click', function() {
  this.classList.add('skeleton-btn');
});
</script>
{% endblock %}
```

---

## Fase 8 — API simple para búsqueda AJAX

Agrega estas vistas auxiliares en `invoicing/views.py` para el autocompletado:

```python
from django.db import models
from django.http import JsonResponse
from catalog.models import Producto
from customers.models import Cliente


def api_productos(request):
    q = request.GET.get('q', '').strip()
    qs = Producto.objects.filter(is_active=True)
    if q:
        qs = qs.filter(models.Q(nombre__icontains=q) | models.Q(codigo__icontains=q))
    data = list(qs.values('id', 'codigo', 'nombre', 'precio', 'iva_porcentaje', 'stock')[:20])
    return JsonResponse(data, safe=False)


def api_clientes(request):
    q = request.GET.get('q', '').strip()
    qs = Cliente.objects.filter(is_active=True)
    if q:
        qs = qs.filter(models.Q(nombre__icontains=q) | models.Q(cedula__icontains=q) | models.Q(email__icontains=q))
    data = list(qs.values('id', 'cedula', 'nombre', 'email')[:20])
    return JsonResponse(data, safe=False)
```

Agrega las rutas API al final de `invoicing/urls.py`:

```python
    path('api/productos/', api_productos, name='api_productos'),
    path('api/clientes/', api_clientes, name='api_clientes'),
```

Y agrega los imports necesarios al inicio del mismo archivo:

```python
from .views import (
    ..., api_clientes, api_productos,
)
```

---

## Fase 9 — Migrar + menú + verificar

```bash
python manage.py makemigrations invoicing
python manage.py migrate
python manage.py check
```

Debe mostrar: `System check identified no issues (0 silenced).`

Actualiza el menú:

```bash
python manage.py shell
```

```python
from core.models import MenuItem
MenuItem.all_objects.filter(name='Facturas').update(url_name='invoicing:invoice_list')
MenuItem.all_objects.filter(name='Reportes').update(url_name='invoicing:invoice_list')
exit()
```

```bash
python manage.py runserver
```

| # | Prueba | Resultado |
|---|--------|-----------|
| 1 | `/invoicing/create/` muestra formulario con buscador de productos | ✅ |
| 2 | Buscar producto por nombre retorna resultados en vivo | ✅ |
| 3 | Agregar producto a la tabla actualiza totales | ✅ |
| 4 | Cambiar cantidad o descuento recalcula en vivo | ✅ |
| 5 | Guardar factura descuenta stock atómicamente | ✅ |
| 6 | Stock insuficiente muestra error y no guarda | ✅ |
| 7 | Factura creada muestra número secuencial FAC-000001 | ✅ |
| 8 | `/invoicing/` lista facturas con filtros de fecha | ✅ |
| 9 | Detalle de factura muestra cálculos correctos | ✅ |
| 10 | Anular factura restaura stock y marca como anulada | ✅ |

---

## Próximo laboratorio

[**Lab 10 — Dashboard + Reportes**](./guia-laboratorio-10.md) con Chart.js, tarjetas de resumen y accesos rápidos.
