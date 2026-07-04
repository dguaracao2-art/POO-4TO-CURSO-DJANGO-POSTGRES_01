# Guía de Laboratorio 08 — CRUD Clientes

## Objetivo

Crear la app `customers` con el modelo Cliente, CRUD completo con CBVs, búsqueda por cédula/nombre, validación de unicidad, y soft delete.

## Duración estimada

1.5 horas (presencial) + 1 hora (trabajo autónomo)

## Prerrequisitos

- Lab 07 completado (CRUD Catálogo con CBVs + búsqueda)
- Lab 04 completado (BaseModel, SoftDeleteManager)

## User Stories

| ID | Historia | Pts |
|----|----------|:---:|
| HU-30 | Como **vendedor** quiero registrar clientes con nombre, cédula, email, teléfono y dirección | 3 |
| HU-31 | Como **vendedor** quiero buscar clientes por cédula o nombre | 2 |
| HU-32 | Como **administrador** quiero editar y desactivar clientes | 2 |
| HU-33 | Como **vendedor** quiero validar que email y cédula sean únicos | 1 |

---

## Estructura de archivos

```
backend/
├── customers/
│   ├── __init__.py
│   ├── apps.py                      (AUTO — startapp)
│   ├── models.py                    (NUEVO) — Cliente
│   ├── admin.py                     (NUEVO)
│   ├── forms.py                     (NUEVO) — ClienteForm
│   ├── views.py                     (NUEVO) — CBVs
│   ├── urls.py                      (NUEVO)
│   └── templates/customers/
│       ├── cliente_list.html        (NUEVO)
│       └── cliente_form.html        (NUEVO)
├── config/
│   ├── settings.py                  (MODIFICAR) — + 'customers'
│   └── urls.py                      (MODIFICAR) — + include
```

---

## Fase 1 — Modelo

**Paso 1.1:** Crea la app y regístrala:

```bash
python manage.py startapp customers
```

```python
# settings.py
LOCAL_APPS = [
    "core", "security", "catalog", "customers",
]
```

**Paso 1.2:** `customers/models.py`:

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
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.cedula})'
```

**Paso 1.3:** `customers/admin.py`:

```python
from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['cedula', 'nombre', 'email', 'telefono', 'is_active']
    search_fields = ['cedula', 'nombre', 'email']
```

---

## Fase 2 — Formulario

**Paso 2.1:** `customers/forms.py`:

```python
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
            raise forms.ValidationError('Esta cédula ya está registrada.')
        return v

    def clean_email(self):
        v = self.cleaned_data['email']
        qs = Cliente.all_objects.filter(email=v)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Este email ya está registrado.')
        return v
```

---

## Fase 3 — Vistas CBV

**Paso 3.1:** `customers/views.py`:

```python
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView
from .forms import ClienteForm
from .models import Cliente


class ClienteListView(PermissionRequiredMixin, ListView):
    permission_required = 'customers.view_cliente'
    model = Cliente
    paginate_by = 10
    template_name = 'customers/cliente_list.html'

    def get_queryset(self):
        qs = Cliente.all_objects.all()
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(Q(cedula__icontains=q) | Q(nombre__icontains=q) | Q(email__icontains=q))
        return qs.order_by('nombre')


class ClienteCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'customers.add_cliente'
    model = Cliente
    form_class = ClienteForm
    template_name = 'customers/cliente_form.html'
    success_url = reverse_lazy('customers:cliente_list')

    def form_valid(self, form):
        messages.success(self.request, 'Cliente registrado correctamente.')
        return super().form_valid(form)


class ClienteUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'customers.change_cliente'
    model = Cliente
    form_class = ClienteForm
    template_name = 'customers/cliente_form.html'
    success_url = reverse_lazy('customers:cliente_list')

    def form_valid(self, form):
        messages.success(self.request, 'Cliente actualizado correctamente.')
        return super().form_valid(form)


class ClienteDeactivateView(PermissionRequiredMixin, View):
    permission_required = 'customers.delete_cliente'

    def post(self, request, pk):
        c = Cliente.all_objects.get(pk=pk)
        c.soft_delete()
        messages.success(request, f'Cliente "{c.nombre}" desactivado.')
        return redirect('customers:cliente_list')
```

---

## Fase 4 — URLs

**Paso 4.1:** `customers/urls.py`:

```python
from django.urls import path
from .views import (
    ClienteCreateView, ClienteDeactivateView, ClienteListView, ClienteUpdateView,
)

app_name = 'customers'
urlpatterns = [
    path('', ClienteListView.as_view(), name='cliente_list'),
    path('create/', ClienteCreateView.as_view(), name='cliente_create'),
    path('<int:pk>/edit/', ClienteUpdateView.as_view(), name='cliente_update'),
    path('<int:pk>/deactivate/', ClienteDeactivateView.as_view(), name='cliente_deactivate'),
]
```

**Paso 4.2:** En `config/urls.py`:

```python
path("customers/", include("customers.urls")),
```

---

## Fase 5 — Templates

**Paso 5.1:** `customers/templates/customers/cliente_list.html`:

```html
{% extends "admin/base_admin.html" %}
{% block title %}Clientes{% endblock %}
{% block page_title %}Gestión de Clientes{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-3">
  <form method="get" class="d-flex gap-2">
    <input type="text" name="q" class="form-control form-control-sm" style="width:300px"
           placeholder="Buscar por cédula, nombre o email..." value="{{ request.GET.q }}">
    <button class="btn btn-sm btn-outline-primary"><i class="bi bi-search"></i></button>
  </form>
  <a href="{% url 'customers:cliente_create' %}" class="btn btn-primary btn-sm"><i class="bi bi-plus-lg"></i> Nuevo Cliente</a>
</div>

<div class="card border-0 shadow-sm">
  <table class="table table-hover align-middle mb-0">
    <thead class="table-light">
      <tr><th>Cédula</th><th>Nombre</th><th>Email</th><th>Teléfono</th><th>Estado</th><th></th></tr>
    </thead>
    <tbody>
      {% for c in cliente_list %}
      <tr>
        <td>{{ c.cedula }}</td><td>{{ c.nombre }}</td>
        <td class="small">{{ c.email }}</td><td>{{ c.telefono|default:'—' }}</td>
        <td>{% if c.is_active %}<span class="badge bg-success">Activo</span>{% else %}<span class="badge bg-secondary">Inactivo</span>{% endif %}</td>
        <td class="text-end">
          <a href="{% url 'customers:cliente_update' c.pk %}" class="btn btn-sm btn-outline-secondary"><i class="bi bi-pencil"></i></a>
          {% if c.is_active %}
          <form method="post" action="{% url 'customers:cliente_deactivate' c.pk %}" class="d-inline">
            {% csrf_token %}<button class="btn btn-sm btn-outline-danger" onclick="return confirm('Desactivar {{ c.nombre }}?')"><i class="bi bi-x-circle"></i></button>
          </form>
          {% endif %}
        </td>
      </tr>
      {% empty %}<tr><td colspan="6" class="text-center text-muted py-4">No hay clientes.</td></tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% include 'catalog/_pagination.html' %}
{% endblock %}
```

**Paso 5.2:** `customers/templates/customers/cliente_form.html`:

```html
{% extends "admin/base_admin.html" %}
{% block title %}{% if object %}Editar{% else %}Nuevo{% endif %} Cliente{% endblock %}
{% block page_title %}{% if object %}Editar{% else %}Nuevo{% endif %} Cliente{% endblock %}
{% block content %}
<div class="card border-0 shadow-sm" style="max-width:600px">
  <div class="card-body p-4">
    <form method="post">{% csrf_token %}
      {% for f in form %}<div class="mb-3"><label class="form-label fw-semibold">{{ f.label }}</label>{{ f }}{% for e in f.errors %}<div class="text-danger small">{{ e }}</div>{% endfor %}</div>{% endfor %}
      <button type="submit" id="btnSubmit" class="btn btn-primary"><i class="bi bi-check-lg"></i> Guardar</button>
      <a href="{% url 'customers:cliente_list' %}" class="btn btn-outline-secondary">Cancelar</a>
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

## Fase 6 — Migrar + menú + verificar

```bash
python manage.py makemigrations customers
python manage.py migrate
```

Actualiza el MenuItem:

```bash
python manage.py shell
```

```python
from core.models import MenuItem
MenuItem.all_objects.filter(name='Listado de Clientes').update(url_name='customers:cliente_list')
exit()
```

```bash
python manage.py check
```

Debe mostrar: `System check identified no issues (0 silenced).`

```bash
python manage.py runserver
```

| # | Prueba | Resultado |
|---|--------|-----------|
| 1 | `/customers/` lista clientes con búsqueda | ✅ |
| 2 | Crear cliente con cédula única funciona | ✅ |
| 3 | Cédula duplicada muestra error de validación | ✅ |
| 4 | Email duplicado muestra error de validación | ✅ |
| 5 | Editar cliente guarda cambios | ✅ |
| 6 | Desactivar cliente lo oculta de listado activo | ✅ |

---

## Próximo laboratorio

[**Lab 09 — Facturación Transaccional (ACID)**](./guia-laboratorio-09.md) con maestro-detalle, `F()` para stock, IVA y anulación.
