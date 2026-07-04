# Caso de Estudio — Implementación Django (Maestro-Detalle MVT)

Aplica las 5 clases y 8 reglas de negocio del [Análisis OO](./caso-estudio-facturacion-analisis.md) en Django puro con **CBVs, templates Bootstrap 5, SoftDelete, transacciones ACID** y `F()` atómico.

---

## Contenido

1. [Arquitectura general](#arquitectura-general)
2. [Modelos (capa datos)](#fase-1--modelos-capa-datos)
3. [Servicios (lógica transaccional)](#fase-2--servicios-lógica-transaccional)
4. [Formularios (validación)](#fase-3--formularios-validación)
5. [Vistas CBV (presentación)](#fase-4--vistas-cbv-presentación)
6. [Templates (HTML + Bootstrap 5)](#fase-5--templates-html--bootstrap-5)
7. [URLs (ruteo)](#fase-6--urls-ruteo)
8. [Transacciones ACID + F() atómico](#fase-7--transacciones-acid--f-atómico)
9. [Verificación final](#fase-8--verificación-final)

---

## Arquitectura general

```
┌─────────────────────────────────────────────────────────────┐
│                     Django MVT                                │
│                                                              │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐ │
│  │  Models   │   │ Services │   │  Forms   │   │  Views   │ │
│  │  (ORM)    │   │ (ACID)   │   │  (val.)  │   │  (CBV)   │ │
│  └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘ │
│       │              │              │              │        │
│       └──────────────┴──────────────┴──────────────┘        │
│                              │                               │
│                         ┌────▼─────┐                         │
│                         │ Templates│                         │
│                         │ (Bootstrap│                        │
│                         └──────────┘                         │
└─────────────────────────────────────────────────────────────┘
       ▲
       │ HTTP (GET/POST)
       │
   ┌───┴───┐
   │Browser│
   └───────┘
```

**Principios aplicados:**
- **SRP:** Cada app una responsabilidad; servicios separados de vistas
- **DIP:** Las vistas dependen de `FacturaService` (abstracción), no del modelo directo
- **DRY:** `BaseModel` aporta `soft_delete()`/`restore()` a todas las entidades
- **ACID:** `@transaction.atomic` + `F()` para stock sin race conditions

---

## Fase 1 — Modelos (capa datos)

Tres apps, 5 modelos de dominio + 1 abstracto (`BaseModel` de la app `core`).

### App catalog (`catalog/models.py`)

```python
from django.db import models
from core.models import BaseModel


class Categoria(BaseModel):
    nombre = models.CharField('Nombre', max_length=100, unique=True)
    descripcion = models.TextField('Descripción', blank=True)

    class Meta:
        verbose_name = 'Categoría'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(BaseModel):
    codigo = models.CharField('Código', max_length=50, unique=True)
    nombre = models.CharField('Nombre', max_length=200)
    descripcion = models.TextField('Descripción', blank=True)
    precio = models.DecimalField('Precio', max_digits=10, decimal_places=2)
    iva_porcentaje = models.DecimalField('IVA %', max_digits=4, decimal_places=2, default=15.00)
    stock = models.IntegerField('Stock', default=0)
    stock_minimo = models.IntegerField('Stock mínimo', default=0)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos')
    imagen = models.ImageField('Imagen', upload_to='productos/', blank=True, null=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'
```

### App customers (`customers/models.py`)

```python
from django.db import models
from core.models import BaseModel


class Cliente(BaseModel):
    cedula = models.CharField('Cédula/RUC', max_length=13, unique=True)
    nombre = models.CharField('Nombre', max_length=200)
    email = models.EmailField('Email', unique=True)
    telefono = models.CharField('Teléfono', max_length=20, blank=True)
    direccion = models.TextField('Dirección', blank=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.cedula})'
```

### App invoicing (`invoicing/models.py`)

```python
from django.db import models
from core.models import BaseModel
from catalog.models import Producto
from customers.models import Cliente
from security.models import User


class SecuenciaFactura(models.Model):
    """Contador secuencial sin race condition (select_for_update)."""
    year = models.IntegerField('Año', unique=True)
    correlativo = models.IntegerField('Correlativo', default=0)

    def __str__(self):
        return f'{self.year}-{self.correlativo:06d}'


class Factura(BaseModel):
    METODO_PAGO = [
        ('Efectivo', 'Efectivo'), ('Tarjeta Débito', 'Tarjeta Débito'),
        ('Tarjeta Crédito', 'Tarjeta Crédito'), ('Transferencia', 'Transferencia'),
    ]

    numero = models.CharField('Número', max_length=20, unique=True, editable=False)
    fecha_emision = models.DateTimeField('Fecha de emisión', auto_now_add=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    subtotal = models.DecimalField('Subtotal', max_digits=12, decimal_places=2, default=0)
    iva_total = models.DecimalField('IVA Total', max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField('Total', max_digits=12, decimal_places=2, default=0)
    metodo_pago = models.CharField(max_length=50, choices=METODO_PAGO, default='Efectivo')
    observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha_emision']

    def __str__(self):
        return self.numero


class DetalleFactura(BaseModel):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField('Cantidad')
    precio_unitario = models.DecimalField('Precio unitario', max_digits=10, decimal_places=2)
    descuento_pct = models.DecimalField('Descuento %', max_digits=5, decimal_places=2, default=0)
    subtotal = models.DecimalField('Subtotal', max_digits=12, decimal_places=2)
    iva_porcentaje = models.DecimalField('IVA %', max_digits=4, decimal_places=2)
    iva_valor = models.DecimalField('Valor IVA', max_digits=12, decimal_places=2)
    total = models.DecimalField('Total', max_digits=12, decimal_places=2)

    def __str__(self):
        return f'{self.producto.nombre} x{self.cantidad}'
```

**Reglas de negocio implementadas en los modelos:**

| Regla | Implementación |
|-------|---------------|
| R1 (stock) | Validación en `FacturaService.crear()` |
| R2 (descuento automático) | `F('stock') - cantidad` en `FacturaService` |
| R3-R5 (cálculos) | Campos `subtotal`, `iva_valor`, `total` en `DetalleFactura` |
| R6 (anulación) | `FacturaService.anular()` restaura stock |
| R7 (no doble anulación) | `if not factura.is_active: raise` |
| R8 (número secuencial) | `SecuenciaFactura` con `select_for_update` |

---

## Fase 2 — Servicios (lógica transaccional)

`invoicing/services.py` encapsula las reglas R1-R8 con transacciones ACID.

```python
from decimal import Decimal
from django.db import transaction
from django.db.models import F
from django.core.exceptions import ValidationError
from django.utils import timezone
from catalog.models import Producto
from .models import DetalleFactura, Factura, SecuenciaFactura


class FacturaService:
    """Lógica de negocio transaccional (SRP)."""

    @staticmethod
    @transaction.atomic
    def crear(*, cliente, usuario, productos_data, metodo_pago='Efectivo', observaciones=''):
        if not productos_data:
            raise ValidationError('Debe agregar al menos un producto.')

        # R8: Número secuencial atómico
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

            # R1: Validar stock
            if prod.stock < item['cantidad']:
                raise ValidationError(f'Stock insuficiente para {prod.nombre}')

            # R3-R5: Calcular línea
            p_unitario = prod.precio
            desc = Decimal(str(item.get('descuento_pct', 0)))
            subt = Decimal(str(item['cantidad'])) * p_unitario * (1 - desc / Decimal('100'))
            iva_p = prod.iva_porcentaje
            iva_v = subt * iva_p / Decimal('100')
            tot = subt + iva_v

            detalles_data.append({
                'producto': prod, 'cantidad': item['cantidad'],
                'precio_unitario': p_unitario, 'descuento_pct': desc,
                'subtotal': subt.quantize(Decimal('0.01')),
                'iva_porcentaje': iva_p, 'iva_valor': iva_v.quantize(Decimal('0.01')),
                'total': tot.quantize(Decimal('0.01')),
            })

            subtotal_factura += subt
            iva_factura += iva_v

            # R2: Descontar stock (atómico con F())
            rows = Producto.objects.filter(pk=prod.pk, stock__gte=item['cantidad']).update(
                stock=F('stock') - item['cantidad']
            )
            if rows == 0:
                raise ValidationError(f'Race condition en stock de {prod.nombre}')

        # Crear factura + detalles en una transacción
        factura = Factura.objects.create(
            numero=numero, cliente=cliente, usuario=usuario,
            subtotal=subtotal_factura.quantize(Decimal('0.01')),
            iva_total=iva_factura.quantize(Decimal('0.01')),
            total=(subtotal_factura + iva_factura).quantize(Decimal('0.01')),
            metodo_pago=metodo_pago, observaciones=observaciones,
        )
        DetalleFactura.objects.bulk_create([
            DetalleFactura(factura=factura, **d) for d in detalles_data
        ])
        return factura

    @staticmethod
    @transaction.atomic
    def anular(factura_id):
        # R7: Validar que no esté ya anulada
        factura = Factura.all_objects.select_for_update().get(pk=factura_id)
        if not factura.is_active:
            raise ValidationError('La factura ya está anulada.')

        # R6: Restaurar stock
        for det in factura.detalles.all():
            Producto.objects.filter(pk=det.producto_id).update(
                stock=F('stock') + det.cantidad
            )

        factura.soft_delete()
        return factura
```

**Flujo ACID completo:**

```
POST /invoicing/create/
    │
    ├─ @transaction.atomic (todo o nada)
    │     │
    │     ├─ SecuenciaFactura.select_for_update() → nº atómico
    │     ├─ loop: validar stock + calcular línea + F() update
    │     │       └─ si stock insuficiente → raise → ROLLBACK
    │     ├─ Factura.objects.create()
    │     ├─ DetalleFactura.objects.bulk_create()
    │     └─ commit implícito
    │
    └─ Éxito → redirect a detalle de factura
```

---

## Fase 3 — Formularios (validación)

Cada formulario usa `ModelForm` de Django con widgets Bootstrap 5:

```python
# catalog/forms.py
from django import forms
from .models import Categoria, Producto


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['codigo', 'nombre', 'descripcion', 'precio',
                  'iva_porcentaje', 'stock', 'stock_minimo', 'categoria', 'imagen']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
        }
```

```python
# customers/forms.py
from django import forms
from .models import Cliente


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['cedula', 'nombre', 'email', 'telefono', 'direccion']
        widgets = {
            'cedula': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '13'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_cedula(self):
        v = self.cleaned_data['cedula']
        qs = Cliente.all_objects.filter(cedula=v)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Cédula ya registrada.')
        return v
```

```python
# invoicing/forms.py
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

## Fase 4 — Vistas CBV (presentación)

Todas las vistas usan `PermissionRequiredMixin` + CBV genéricos de Django. Patrón uniforme:

```
ListView    → GET /app/modelo/          (lista paginada)
CreateView  → GET,POST /app/modelo/create/  (formulario)
UpdateView  → GET,POST /app/modelo/<pk>/edit/  (edición)
+ soft_delete vía POST /app/modelo/<pk>/deactivate/
```

### Vista genérica de ejemplo (categorías)

```python
# catalog/views.py
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView
from .forms import CategoriaForm
from .models import Categoria


class CategoriaListView(PermissionRequiredMixin, ListView):
    permission_required = 'catalog.view_categoria'
    model = Categoria
    paginate_by = 10
    template_name = 'catalog/categoria_list.html'

    def get_queryset(self):
        qs = Categoria.all_objects.all()
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))
        return qs.order_by('nombre')
```

### Vista de facturación (con servicio transaccional)

```python
# invoicing/views.py
import json
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView
from .forms import FacturaForm
from .models import Factura
from .services import FacturaService


class InvoiceCreateView(LoginRequiredMixin, View):
    """GET → formulario | POST → FacturaService.crear() + redirect"""
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
            messages.success(request, f'Factura {factura.numero} creada.')
            return redirect('invoicing:invoice_detail', pk=factura.pk)
        except Exception as e:
            messages.error(request, str(e))
            return render(request, self.template_name, {'form': form})
```

### APIs de búsqueda AJAX (para el formulario de facturación)

```python
# invoicing/views.py (adicional)
from django.http import JsonResponse
from catalog.models import Producto
from customers.models import Cliente


def api_productos(request):
    q = request.GET.get('q', '').strip()
    qs = Producto.objects.filter(is_active=True)
    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(codigo__icontains=q))
    data = list(qs.values('id', 'codigo', 'nombre', 'precio', 'iva_porcentaje', 'stock')[:20])
    return JsonResponse(data, safe=False)


def api_clientes(request):
    q = request.GET.get('q', '').strip()
    qs = Cliente.objects.filter(is_active=True)
    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(cedula__icontains=q))
    data = list(qs.values('id', 'cedula', 'nombre', 'email')[:20])
    return JsonResponse(data, safe=False)
```

---

## Fase 5 — Templates (HTML + Bootstrap 5)

Todos los templates extienden `admin/base_admin.html` que provee el sidebar con módulos permisados. Patrón uniforme:

```
{% extends "admin/base_admin.html" %}
{% block title %}...{% endblock %}
{% block page_title %}...{% endblock %}
{% block content %}
  <!-- tabla o formulario -->
{% endblock %}
```

### Listado genérico (ej: categorías)

```html
{% extends "admin/base_admin.html" %}
{% block title %}Categorías{% endblock %}
{% block page_title %}Gestión de Categorías{% endblock %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-3">
  <form method="get" class="d-flex gap-2">
    <input type="text" name="q" class="form-control form-control-sm"
           placeholder="Buscar..." value="{{ request.GET.q }}">
    <button class="btn btn-sm btn-outline-primary"><i class="bi bi-search"></i></button>
  </form>
  <a href="{% url 'catalog:categoria_create' %}" class="btn btn-primary btn-sm">
    <i class="bi bi-plus-lg"></i> Nueva Categoría
  </a>
</div>
<div class="card border-0 shadow-sm">
  <table class="table table-hover align-middle mb-0">
    <thead class="table-light">
      <tr><th>Nombre</th><th>Descripción</th><th>Estado</th><th></th></tr>
    </thead>
    <tbody>
      {% for c in categoria_list %}
      <tr>
        <td>{{ c.nombre }}</td>
        <td class="small text-muted">{{ c.descripcion|truncatewords:10 }}</td>
        <td>{% if c.is_active %}<span class="badge bg-success">Activo</span>
            {% else %}<span class="badge bg-secondary">Inactivo</span>{% endif %}</td>
        <td class="text-end">
          <a href="{% url 'catalog:categoria_update' c.pk %}" class="btn btn-sm btn-outline-secondary"><i class="bi bi-pencil"></i></a>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% endblock %}
```

### Formulario de facturación (maestro-detalle + AJAX)

El template `invoicing/invoice_form.html` incluye:
- Selector de cliente (`{{ form.cliente }}`)
- Buscador de productos con resultados en vivo (AJAX vía `api_productos`)
- Tabla de detalles editable (cantidad, descuento, subtotal en tiempo real)
- Totales automáticos (subtotal, IVA, total)
- Botón Guardar con skeleton loading

```html
{% extends "admin/base_admin.html" %}
{% load static %}
{% block title %}Nueva Factura{% endblock %}
{% block page_title %}Nueva Factura{% endblock %}

{% block content %}
<form method="post" id="invoiceForm">
  {% csrf_token %}
  <input type="hidden" name="productos_json" id="productosJson" value="[]">

  <div class="card border-0 shadow-sm mb-3">
    <div class="card-body">
      <div class="row">
        <div class="col-md-6">{{ form.cliente.label_tag }}{{ form.cliente }}</div>
        <div class="col-md-3">{{ form.metodo_pago.label_tag }}{{ form.metodo_pago }}</div>
      </div>
    </div>
  </div>

  <div class="card border-0 shadow-sm mb-3">
    <div class="card-body">
      <input type="text" id="searchProducto" class="form-control" placeholder="Buscar producto...">
      <div id="resultsProducto" class="list-group mt-2"></div>
    </div>
  </div>

  <div class="card border-0 shadow-sm mb-3">
    <div class="card-body">
      <table class="table table-sm">
        <thead><tr><th>Producto</th><th>Cant.</th><th>P/U</th><th>Desc.%</th><th class="text-end">Subtotal</th><th></th></tr></thead>
        <tbody id="detalleBody"></tbody>
      </table>
      <div class="text-end">
        <strong>Subtotal:</strong> $<span id="totalSubtotal">0.00</span><br>
        <strong>IVA:</strong> $<span id="totalIva">0.00</span><br>
        <h4><strong>TOTAL:</strong> $<span id="totalGeneral">0.00</span></h4>
      </div>
    </div>
  </div>

  {{ form.observaciones }}
  <button type="submit" id="btnSubmit" class="btn btn-primary btn-lg">
    <i class="bi bi-check-lg"></i> Guardar Factura
  </button>
</form>
{% endblock %}

{% block extra_scripts %}
<script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
<script src="{% static 'security/js/api-client.js' %}"></script>
<script src="{% static 'invoicing/js/invoice-calculator.js' %}"></script>
<script src="{% static 'invoicing/js/invoice-form.js' %}"></script>
{% endblock %}
```

---

## Fase 6 — URLs (ruteo)

Patrón consistente: `app_name` + rutas con nombre

```python
# catalog/urls.py
app_name = 'catalog'
urlpatterns = [
    path('categories/', CategoriaListView.as_view(), name='categoria_list'),
    path('categories/create/', CategoriaCreateView.as_view(), name='categoria_create'),
    path('categories/<int:pk>/edit/', CategoriaUpdateView.as_view(), name='categoria_update'),
    path('categories/<int:pk>/deactivate/', CategoriaDeactivateView.as_view(), name='categoria_deactivate'),
    path('products/', ProductoListView.as_view(), name='producto_list'),
    path('products/create/', ProductoCreateView.as_view(), name='producto_create'),
    path('products/<int:pk>/edit/', ProductoUpdateView.as_view(), name='producto_update'),
    path('products/<int:pk>/deactivate/', ProductoDeactivateView.as_view(), name='producto_deactivate'),
]
```

```python
# invoicing/urls.py
app_name = 'invoicing'
urlpatterns = [
    path('', InvoiceListView.as_view(), name='invoice_list'),
    path('create/', InvoiceCreateView.as_view(), name='invoice_create'),
    path('<int:pk>/', InvoiceDetailView.as_view(), name='invoice_detail'),
    path('<int:pk>/annul/', InvoiceAnnulView.as_view(), name='invoice_annul'),
    path('api/productos/', api_productos, name='api_productos'),
    path('api/clientes/', api_clientes, name='api_clientes'),
]
```

```python
# config/urls.py (raíz)
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", DashboardView.as_view(), name="home"),
    path("security/", include("security.urls")),
    path("catalog/", include("catalog.urls")),
    path("customers/", include("customers.urls")),
    path("invoicing/", include("invoicing.urls")),
]
```

---

## Fase 7 — Transacciones ACID + F() atómico

### El problema de concurrencia

Dos vendedores crean facturas del mismo producto simultáneamente:

```
Vendedor A: lee stock=10, vende 8, escribe stock=2
Vendedor B: lee stock=10, vende 5, escribe stock=5  ← ¡stock incorrecto!
```

### Solución con `F()` (Django)

`F('stock') - cantidad` se ejecuta en **una sola consulta SQL** dentro de la BD, sin que el valor intermedio salga de la BD:

```python
# Una sola consulta: UPDATE producto SET stock = stock - 8 WHERE id=X AND stock >= 8
rows = Producto.objects.filter(pk=prod.pk, stock__gte=item['cantidad']).update(
    stock=F('stock') - item['cantidad']
)
if rows == 0:
    raise ValidationError('Stock insuficiente')  # → ROLLBACK
```

Si `stock >= cantidad`, la actualización ocurre y `rows=1`. Si no, `rows=0` y la transacción revierte todo el bloque `@transaction.atomic` (factura, detalles, otros descuentos).

### Número secuencial sin race condition

El `select_for_update` bloquea la fila de `SecuenciaFactura` hasta que la transacción termina:

```python
seq = SecuenciaFactura.objects.select_for_update().get_or_create(year=year)
seq.correlativo = F('correlativo') + 1
seq.save()
seq.refresh_from_db()  # correlativo final (evaluado en BD)
```

---

## Fase 8 — Verificación final

### Verificación desde el navegador

| Prueba | Navegar a | Resultado |
|--------|-----------|----------|
| Login | `/security/login/` | Formulario split-screen, autenticación AJAX |
| Dashboard | `/` | Tarjetas con datos, gráfico Chart.js |
| CRUD Categorías | `/catalog/categories/` | Listar, crear, editar, desactivar |
| CRUD Productos | `/catalog/products/` | CRUD con imagen y stock |
| CRUD Clientes | `/customers/` | Búsqueda por cédula/nombre |
| Crear Factura | `/invoicing/create/` | Buscador productos, totales en vivo |
| Detalle Factura | `/invoicing/1/` | Desglose completo, botón anular |
| Anular Factura | POST a `/invoicing/1/annul/` | Stock restaurado, badge "Anulada" |

### Verificación con `check` y migraciones

```bash
python manage.py check
python manage.py showmigrations  # todos [X]
```

---

## Mapeo OO → Django

| Concepto POO | Implementación Django |
|-------------|----------------------|
| **Clase** | `models.Model` (herencia de `BaseModel`) |
| **Atributo** | `CharField`, `DecimalField`, `IntegerField`, `ImageField` |
| **Método** | Métodos de instancia (`__str__`, `soft_delete`, `restore`) |
| **Composición** | `Factura 1 → * DetalleFactura` (`on_delete=CASCADE`) |
| **Asociación** | `ForeignKey` (`Producto → Categoria`) |
| **Encapsulación** | Servicios (`FacturaService`) encapsulan lógica transaccional |
| **Abstracción** | `BaseModel` abstracto; vistas dependen de servicios no de modelos |
| **Polimorfismo** | `soft_delete() / restore()` en todas las entidades |
| **SRP** | Cada app una responsabilidad; servicios separados de vistas |
| **DIP** | `InvoiceCreateView` inyecta `FacturaService`, no lo instancia |
| **DRY** | `BaseModel` evita repetir created_at/updated_at/is_active |
