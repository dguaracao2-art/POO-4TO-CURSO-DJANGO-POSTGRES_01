# Guía de Laboratorio 07 — CRUD Catálogo (Categorías + Productos)

## Objetivo

Crear la app `catalog` con modelos Categoria y Producto (heredando de BaseModel), CRUD completo con CBVs, búsqueda, paginación, carga de imágenes y control de stock.

## Duración estimada

2 horas (presencial) + 1 hora (trabajo autónomo)

## Prerrequisitos

- Lab 06 completado (CRUD Usuarios + Roles con CBVs)
- Lab 05 completado (sidebar con base_admin.html)
- Lab 04 completado (BaseModel, SoftDeleteManager)

## User Stories

| ID | Historia | Pts |
|----|----------|:---:|
| HU-26 | Como **administrador** quiero gestionar categorías (crear, editar, listar, desactivar) | 3 |
| HU-27 | Como **administrador** quiero gestionar productos con nombre, precio, stock, categoría y foto | 5 |
| HU-28 | Como **vendedor** quiero buscar productos por nombre o categoría | 3 |
| HU-29 | Como **vendedor** quiero ver el stock disponible | 1 |

---

## Estructura de archivos

```
backend/
├── catalog/
│   ├── __init__.py
│   ├── apps.py                      (AUTO — startapp)
│   ├── models.py                    (NUEVO) — Categoria, Producto
│   ├── admin.py                     (NUEVO) — registros admin
│   ├── forms.py                     (NUEVO) — CategoriaForm, ProductoForm
│   ├── views.py                     (NUEVO) — CBVs con search + pagination
│   ├── urls.py                      (NUEVO) — rutas CRUD
│   ├── templates/catalog/
│   │   ├── categoria_list.html      (NUEVO)
│   │   ├── categoria_form.html      (NUEVO)
│   │   ├── producto_list.html       (NUEVO)
│   │   └── producto_form.html       (NUEVO)
│   └── static/catalog/js/
│       └── catalog-admin.js         (NUEVO)
└── config/
    ├── settings.py                  (MODIFICAR) — + 'catalog' en LOCAL_APPS
    └── urls.py                      (MODIFICAR) — + include('catalog.urls')
```

---

## Fase 1 — Crear la app y modelos

**Paso 1.1:** Crea la app:

```bash
python manage.py startapp catalog
```

**Paso 1.2:** Registra en `config/settings.py`:

```python
LOCAL_APPS = [
    "core",
    "security",
    "catalog",
]
```

**Paso 1.3:** Crea `catalog/models.py`:

```python
from django.db import models
from core.models import BaseModel


class Categoria(BaseModel):
    nombre = models.CharField('Nombre', max_length=100, unique=True)
    descripcion = models.TextField('Descripción', blank=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
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
    stock_minimo = models.IntegerField('Stock mínimo', default=0, help_text='Alertar cuando el stock baje de esta cantidad')
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos', verbose_name='Categoría')
    imagen = models.ImageField('Imagen', upload_to='productos/', blank=True, null=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'
```

**Paso 1.4:** Crea `catalog/admin.py`:

```python
from django.contrib import admin
from .models import Categoria, Producto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'is_active']
    search_fields = ['nombre']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'precio', 'stock', 'categoria', 'is_active']
    list_filter = ['categoria', 'is_active']
    search_fields = ['codigo', 'nombre']
```

---

## Fase 2 — Formularios

**Paso 2.1:** Crea `catalog/forms.py`:

```python
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
        fields = ['codigo', 'nombre', 'descripcion', 'precio', 'iva_porcentaje',
                  'stock', 'stock_minimo', 'categoria', 'imagen']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'iva_porcentaje': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
        }
```

---

## Fase 3 — Vistas CBV

**Paso 3.1:** Crea `catalog/views.py`:

```python
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView
from .forms import CategoriaForm, ProductoForm
from .models import Categoria, Producto


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


class CategoriaCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.add_categoria'
    model = Categoria
    form_class = CategoriaForm
    template_name = 'catalog/categoria_form.html'
    success_url = reverse_lazy('catalog:categoria_list')

    def form_valid(self, form):
        messages.success(self.request, 'Categoría creada correctamente.')
        return super().form_valid(form)


class CategoriaUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.change_categoria'
    model = Categoria
    form_class = CategoriaForm
    template_name = 'catalog/categoria_form.html'
    success_url = reverse_lazy('catalog:categoria_list')

    def form_valid(self, form):
        messages.success(self.request, 'Categoría actualizada correctamente.')
        return super().form_valid(form)


class CategoriaDeactivateView(PermissionRequiredMixin, View):
    permission_required = 'catalog.delete_categoria'

    def post(self, request, pk):
        cat = Categoria.all_objects.get(pk=pk)
        if cat.productos.filter(is_active=True).exists():
            messages.error(request, 'No se puede desactivar: tiene productos activos.')
        else:
            cat.soft_delete()
            messages.success(request, f'Categoría "{cat.nombre}" desactivada.')
        return redirect('catalog:categoria_list')


class ProductoListView(PermissionRequiredMixin, ListView):
    permission_required = 'catalog.view_producto'
    model = Producto
    paginate_by = 10
    template_name = 'catalog/producto_list.html'

    def get_queryset(self):
        qs = Producto.all_objects.select_related('categoria').all()
        q = self.request.GET.get('q', '').strip()
        cat = self.request.GET.get('categoria', '').strip()
        if q:
            qs = qs.filter(Q(nombre__icontains=q) | Q(codigo__icontains=q))
        if cat:
            qs = qs.filter(categoria_id=cat)
        return qs.order_by('nombre')


class ProductoCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.add_producto'
    model = Producto
    form_class = ProductoForm
    template_name = 'catalog/producto_form.html'
    success_url = reverse_lazy('catalog:producto_list')

    def form_valid(self, form):
        messages.success(self.request, 'Producto creado correctamente.')
        return super().form_valid(form)


class ProductoUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.change_producto'
    model = Producto
    form_class = ProductoForm
    template_name = 'catalog/producto_form.html'
    success_url = reverse_lazy('catalog:producto_list')

    def form_valid(self, form):
        messages.success(self.request, 'Producto actualizado correctamente.')
        return super().form_valid(form)


class ProductoDeactivateView(PermissionRequiredMixin, View):
    permission_required = 'catalog.delete_producto'

    def post(self, request, pk):
        prod = Producto.all_objects.get(pk=pk)
        prod.soft_delete()
        messages.success(request, f'Producto "{prod.nombre}" desactivado.')
        return redirect('catalog:producto_list')
```

---

## Fase 4 — URLs

**Paso 4.1:** Crea `catalog/urls.py`:

```python
from django.urls import path
from .views import (
    CategoriaCreateView, CategoriaDeactivateView, CategoriaListView, CategoriaUpdateView,
    ProductoCreateView, ProductoDeactivateView, ProductoListView, ProductoUpdateView,
)

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

**Paso 4.2:** En `config/urls.py`, agrega:

```python
from django.urls import include, path

urlpatterns = [
    ...
    path("catalog/", include("catalog.urls")),
]
```

---

## Fase 5 — Templates

**Paso 5.1:** Crea `catalog/templates/catalog/categoria_list.html`:

```html
{% extends "admin/base_admin.html" %}
{% load static %}
{% block title %}Categorías{% endblock %}
{% block page_title %}Gestión de Categorías{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-3">
  <form method="get" class="d-flex gap-2">
    <input type="text" name="q" class="form-control form-control-sm" style="width:300px"
           placeholder="Buscar categoría..." value="{{ request.GET.q }}">
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
        <td class="small text-muted">{{ c.descripcion|truncatewords:10|default:'—' }}</td>
        <td>{% if c.is_active %}<span class="badge bg-success">Activo</span>{% else %}<span class="badge bg-secondary">Inactivo</span>{% endif %}</td>
        <td class="text-end">
          <a href="{% url 'catalog:categoria_update' c.pk %}" class="btn btn-sm btn-outline-secondary"><i class="bi bi-pencil"></i></a>
          {% if c.is_active %}
          <form method="post" action="{% url 'catalog:categoria_deactivate' c.pk %}" class="d-inline">
            {% csrf_token %}
            <button class="btn btn-sm btn-outline-danger" onclick="return confirm('Desactivar {{ c.nombre }}?')"><i class="bi bi-x-circle"></i></button>
          </form>
          {% endif %}
        </td>
      </tr>
      {% empty %}<tr><td colspan="4" class="text-center text-muted py-4">No hay categorías.</td></tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% include 'catalog/_pagination.html' %}
{% endblock %}
```

**Paso 5.2:** Crea `catalog/templates/catalog/_pagination.html` (reutilizable):

```html
{% if page_obj.paginator.num_pages > 1 %}
<nav class="mt-3"><ul class="pagination pagination-sm justify-content-center">
  {% if page_obj.has_previous %}
  <li class="page-item"><a class="page-link" href="?page={{ page_obj.previous_page_number }}{% if request.GET.q %}&q={{ request.GET.q }}{% endif %}">Anterior</a></li>
  {% endif %}
  <li class="page-item disabled"><span class="page-link">Pág. {{ page_obj.number }} de {{ page_obj.paginator.num_pages }}</span></li>
  {% if page_obj.has_next %}
  <li class="page-item"><a class="page-link" href="?page={{ page_obj.next_page_number }}{% if request.GET.q %}&q={{ request.GET.q }}{% endif %}">Siguiente</a></li>
  {% endif %}
</ul></nav>
{% endif %}
```

**Paso 5.3:** Crea `catalog/templates/catalog/categoria_form.html`:

```html
{% extends "admin/base_admin.html" %}
{% block title %}{% if object %}Editar{% else %}Nueva{% endif %} Categoría{% endblock %}
{% block page_title %}{% if object %}Editar{% else %}Nueva{% endif %} Categoría{% endblock %}
{% block content %}
<div class="card border-0 shadow-sm" style="max-width:600px">
  <div class="card-body p-4">
    <form method="post">{% csrf_token %}
      {% for f in form %}<div class="mb-3"><label class="form-label fw-semibold">{{ f.label }}</label>{{ f }}{% for e in f.errors %}<div class="text-danger small">{{ e }}</div>{% endfor %}</div>{% endfor %}
      <button type="submit" id="btnSubmit" class="btn btn-primary"><i class="bi bi-check-lg"></i> Guardar</button>
      <a href="{% url 'catalog:categoria_list' %}" class="btn btn-outline-secondary">Cancelar</a>
    </form>
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

**Paso 5.4:** Crea `catalog/templates/catalog/producto_list.html`:

```html
{% extends "admin/base_admin.html" %}
{% load static %}
{% block title %}Productos{% endblock %}
{% block page_title %}Gestión de Productos{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-3">
  <form method="get" class="d-flex gap-2 flex-wrap">
    <input type="text" name="q" class="form-control form-control-sm" style="width:200px" placeholder="Buscar..." value="{{ request.GET.q }}">
    <select name="categoria" class="form-select form-select-sm" style="width:auto" onchange="this.form.submit()">
      <option value="">Todas las categorías</option>
      {% for c in categorias %}<option value="{{ c.pk }}" {% if request.GET.categoria == c.pk|stringformat:'s' %}selected{% endif %}>{{ c.nombre }}</option>{% endfor %}
    </select>
    <button class="btn btn-sm btn-outline-primary"><i class="bi bi-search"></i></button>
  </form>
  <a href="{% url 'catalog:producto_create' %}" class="btn btn-primary btn-sm"><i class="bi bi-plus-lg"></i> Nuevo Producto</a>
</div>

<div class="card border-0 shadow-sm">
  <table class="table table-hover align-middle mb-0">
    <thead class="table-light">
      <tr><th>Código</th><th>Nombre</th><th>Precio</th><th>Stock</th><th>Categoría</th><th>Estado</th><th></th></tr>
    </thead>
    <tbody>
      <tr class="skeleton-row d-none" id="loadingRows">
        <td></td><td></td><td></td><td></td><td></td><td></td><td></td>
      </tr>
      {% for p in producto_list %}
      <tr>
        <td class="small">{{ p.codigo }}</td>
        <td>
          {% if p.imagen %}<img src="{{ p.imagen.url }}" width="30" height="30" class="rounded me-1" style="object-fit:cover">{% endif %}
          {{ p.nombre }}
        </td>
        <td>${{ p.precio|floatformat:2 }}</td>
        <td>
          <span class="badge {% if p.stock == 0 %}bg-danger{% elif p.stock < p.stock_minimo %}bg-warning text-dark{% else %}bg-success{% endif %}">
            {{ p.stock }}
          </span>
        </td>
        <td class="small">{{ p.categoria.nombre }}</td>
        <td>{% if p.is_active %}<span class="badge bg-success">Activo</span>{% else %}<span class="badge bg-secondary">Inactivo</span>{% endif %}</td>
        <td class="text-end">
          <a href="{% url 'catalog:producto_update' p.pk %}" class="btn btn-sm btn-outline-secondary"><i class="bi bi-pencil"></i></a>
          {% if p.is_active %}
          <form method="post" action="{% url 'catalog:producto_deactivate' p.pk %}" class="d-inline">
            {% csrf_token %}<button class="btn btn-sm btn-outline-danger" onclick="return confirm('Desactivar {{ p.nombre }}?')"><i class="bi bi-x-circle"></i></button>
          </form>
          {% endif %}
        </td>
      </tr>
      {% empty %}<tr><td colspan="7" class="text-center text-muted py-4">No hay productos.</td></tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% include 'catalog/_pagination.html' %}
{% endblock %}
```

**Paso 5.5:** Crea `catalog/templates/catalog/producto_form.html`:

```html
{% extends "admin/base_admin.html" %}
{% block title %}{% if object %}Editar{% else %}Nuevo{% endif %} Producto{% endblock %}
{% block page_title %}{% if object %}Editar{% else %}Nuevo{% endif %} Producto{% endblock %}
{% block content %}
<div class="card border-0 shadow-sm" style="max-width:700px">
  <div class="card-body p-4">
    <form method="post" enctype="multipart/form-data">{% csrf_token %}
      {% for f in form %}<div class="mb-3"><label class="form-label fw-semibold">{{ f.label }}</label>{{ f }}{% for e in f.errors %}<div class="text-danger small">{{ e }}</div>{% endfor %}</div>{% endfor %}
      <button type="submit" id="btnSubmit" class="btn btn-primary"><i class="bi bi-check-lg"></i> Guardar</button>
      <a href="{% url 'catalog:producto_list' %}" class="btn btn-outline-secondary">Cancelar</a>
    </form>
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

## Fase 6 — Actualizar el menú

Agrega las URL de catálogo a los MenuItem:

```bash
python manage.py shell
```

```python
from core.models import MenuItem
MenuItem.all_objects.filter(name='Categorías').update(url_name='catalog:categoria_list')
MenuItem.all_objects.filter(name='Productos').update(url_name='catalog:producto_list')
exit()
```

---

## Fase 7 — Migrar, verificar y probar

```bash
python manage.py makemigrations catalog
python manage.py migrate
python manage.py check
```

Debe mostrar: `System check identified no issues (0 silenced).`

```bash
python manage.py runserver
```

| # | Prueba | Resultado |
|---|--------|-----------|
| 1 | `/catalog/categories/` lista categorías paginadas | ✅ |
| 2 | Crear categoría funciona con validación | ✅ |
| 3 | Desactivar categoría con productos activos da error | ✅ |
| 4 | `/catalog/products/` lista con búsqueda y filtro | ✅ |
| 5 | Crear producto con imagen se guarda correctamente | ✅ |
| 6 | Stock bajo (rojo 0, amarillo < mínimo, verde normal) | ✅ |
| 7 | Productos aparecen en el sidebar del menú | ✅ |

---

## Próximo laboratorio

[**Lab 08 — CRUD Clientes**](./guia-laboratorio-08.md) con búsqueda por cédula, validación de único, y soft delete.
