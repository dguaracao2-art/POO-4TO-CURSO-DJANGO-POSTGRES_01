# Guía de Laboratorio 06 — CRUD Usuarios + Roles y Permisos

## Objetivo

Crear vistas de listado, creación, edición y desactivación de usuarios y roles (grupos) usando Class-Based Views (CBVs), búsqueda, paginación y asignación de permisos.

## Duración estimada

2 horas (presencial) + 1 hora (trabajo autónomo)

## Prerrequisitos

- Lab 05 completado (panel administrativo con sidebar + base_admin.html)
- Lab 04 completado (app core con BaseModel y SoftDeleteManager)
- `{% load menu_tags %}`, `{% load static %}` funcionales en templates

## User Stories

| ID | Historia | Pts |
|----|----------|:---:|
| HU-22 | Como **administrador** quiero listar, crear, editar y desactivar usuarios | 5 |
| HU-23 | Como **administrador** quiero crear roles con permisos específicos | 3 |
| HU-24 | Como **administrador** quiero asignar usuarios a roles | 2 |
| HU-25 | Como **usuario** quiero ver y editar mi perfil | 3 |

---

## Estructura de archivos

```
backend/
├── security/
│   ├── views.py                    (MODIFICAR) — + UserCRUD + GroupCRUD + ProfileView
│   ├── urls.py                     (MODIFICAR) — + rutas CRUD
│   ├── forms.py                    (NUEVO) — UserForm, GroupForm, ProfileForm
│   ├── templates/security/
│   │   ├── user_list.html          (NUEVO) — tabla paginada + búsqueda
│   │   ├── user_form.html          (NUEVO) — crear/editar usuario
│   │   ├── group_list.html         (NUEVO) — lista de roles
│   │   ├── group_form.html         (NUEVO) — crear/editar rol + permisos
│   │   └── profile.html            (NUEVO) — perfil del usuario
│   └── static/security/js/
│       └── security-admin.js       (NUEVO) — CRUD asíncrono
```

---

## Fase 1 — Formularios

**Paso 1.1:** Crea `security/forms.py`:

```python
from django import forms
from django.contrib.auth.models import Group, Permission
from .models import User


class UserForm(forms.ModelForm):
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(render_value=True, attrs={'class': 'form-control'}),
        required=False,
        help_text='Dejar vacío para mantener la actual al editar',
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class GroupForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.select_related('content_type').order_by('content_type__app_label', 'codename'),
        widget=forms.SelectMultiple(attrs={'size': 20, 'class': 'form-select'}),
        required=False,
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ProfileForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Nueva contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'foto']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.all_objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Este email ya está registrado.')
        return email

    def clean(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p1 != p2:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return self.cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        p1 = self.cleaned_data.get('password1')
        if p1:
            user.set_password(p1)
        if commit:
            user.save()
        return user
```

---

## Fase 2 — Vistas CBV

**Paso 2.1:** Agrega al final de `security/views.py`:

```python
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, View
from django.views.generic.edit import DeleteView
from django.contrib import messages
from django.shortcuts import redirect, render
from django.db.models import Q
from .forms import GroupForm, ProfileForm, UserForm
from .models import User


class UserListView(PermissionRequiredMixin, ListView):
    permission_required = 'security.view_user'
    model = User
    paginate_by = 10
    template_name = 'security/user_list.html'

    def get_queryset(self):
        qs = User.all_objects.all()
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q) |
                Q(email__icontains=q)
            )
        return qs.order_by('-date_joined')


class UserCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'security.add_user'
    model = User
    form_class = UserForm
    template_name = 'security/user_form.html'
    success_url = reverse_lazy('security:user_list')

    def form_valid(self, form):
        messages.success(self.request, 'Usuario creado correctamente.')
        return super().form_valid(form)


class UserUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'security.change_user'
    model = User
    form_class = UserForm
    template_name = 'security/user_form.html'
    success_url = reverse_lazy('security:user_list')
    context_object_name = 'user_obj'

    def form_valid(self, form):
        messages.success(self.request, 'Usuario actualizado correctamente.')
        return super().form_valid(form)


class UserDeactivateView(PermissionRequiredMixin, View):
    permission_required = 'security.delete_user'

    def post(self, request, pk):
        user = User.all_objects.get(pk=pk)
        if user == request.user:
            messages.error(request, 'No puedes desactivarte a ti mismo.')
            return redirect('security:user_list')
        user.soft_delete()
        messages.success(request, f'Usuario {user.email} desactivado.')
        return redirect('security:user_list')


class GroupListView(PermissionRequiredMixin, ListView):
    permission_required = 'auth.view_group'
    model = Group
    paginate_by = 10
    template_name = 'security/group_list.html'


class GroupCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'auth.add_group'
    model = Group
    form_class = GroupForm
    template_name = 'security/group_form.html'
    success_url = reverse_lazy('security:group_list')

    def form_valid(self, form):
        messages.success(self.request, 'Rol creado correctamente.')
        return super().form_valid(form)


class GroupUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'auth.change_group'
    model = Group
    form_class = GroupForm
    template_name = 'security/group_form.html'
    success_url = reverse_lazy('security:group_list')

    def form_valid(self, form):
        messages.success(self.request, 'Rol actualizado correctamente.')
        return super().form_valid(form)


class ProfileView(View):
    template_name = 'security/profile.html'

    def get(self, request):
        form = ProfileForm(instance=request.user)
        groups = request.user.groups.all()
        return render(request, self.template_name, {'form': form, 'groups': groups})

    def post(self, request):
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('security:profile')
        groups = request.user.groups.all()
        return render(request, self.template_name, {'form': form, 'groups': groups})
```

---

## Fase 3 — URLs

**Paso 3.1:** Actualiza `security/urls.py`:

```python
from django.contrib.auth.views import LogoutView
from django.urls import path
from .views import (
    GroupCreateView, GroupListView, GroupUpdateView,
    InicioTemplate, LoginPageView, ProfileView,
    UserCreateView, UserDeactivateView, UserListView, UserUpdateView,
)

app_name = 'security'
urlpatterns = [
    path('login/', LoginPageView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('users/', UserListView.as_view(), name='user_list'),
    path('users/create/', UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user_update'),
    path('users/<int:pk>/deactivate/', UserDeactivateView.as_view(), name='user_deactivate'),

    path('groups/', GroupListView.as_view(), name='group_list'),
    path('groups/create/', GroupCreateView.as_view(), name='group_create'),
    path('groups/<int:pk>/edit/', GroupUpdateView.as_view(), name='group_update'),

    path('profile/', ProfileView.as_view(), name='profile'),
]
```

---

## Fase 4 — Templates

**Paso 4.1:** Crea `security/templates/security/user_list.html`:

```html
{% extends "admin/base_admin.html" %}
{% load static %}
{% block title %}Usuarios{% endblock %}
{% block page_title %}Gestión de Usuarios{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-3">
  <form method="get" class="d-flex gap-2">
    <input type="text" name="q" class="form-control form-control-sm" style="width:300px"
           placeholder="Buscar por nombre o email..." value="{{ request.GET.q }}">
    <button class="btn btn-sm btn-outline-primary" type="submit"><i class="bi bi-search"></i></button>
  </form>
  <a href="{% url 'security:user_create' %}" class="btn btn-primary btn-sm">
    <i class="bi bi-plus-lg"></i> Nuevo Usuario
  </a>
</div>

<div class="card border-0 shadow-sm">
  <div class="table-responsive">
    <table class="table table-hover align-middle mb-0">
      <thead class="table-light">
        <tr>
          <th>Email</th><th>Nombre</th><th>Estado</th><th>Última conexión</th><th></th>
        </tr>
      </thead>
      <tbody>
        {% for u in user_list %}
        <tr>
          <td>{{ u.email }}</td>
          <td>{{ u.get_full_name|default:'—' }}</td>
          <td>
            {% if u.is_active %}
              <span class="badge bg-success">Activo</span>
            {% else %}
              <span class="badge bg-secondary">Inactivo</span>
            {% endif %}
          </td>
          <td class="small text-muted">{{ u.last_login|date:'d/m/Y H:i'|default:'Nunca' }}</td>
          <td class="text-end">
            <a href="{% url 'security:user_update' u.pk %}" class="btn btn-sm btn-outline-secondary" title="Editar">
              <i class="bi bi-pencil"></i>
            </a>
            {% if u.is_active and u != request.user %}
            <form method="post" action="{% url 'security:user_deactivate' u.pk %}" class="d-inline">
              {% csrf_token %}
              <button class="btn btn-sm btn-outline-danger" title="Desactivar"
                      onclick="return confirm('Desactivar a {{ u.email }}?')">
                <i class="bi bi-person-x"></i>
              </button>
            </form>
            {% endif %}
          </td>
        </tr>
        {% empty %}
        <tr><td colspan="5" class="text-center text-muted py-4">No hay usuarios.</td></tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</div>

{% if page_obj.paginator.num_pages > 1 %}
<nav class="mt-3">
  <ul class="pagination pagination-sm justify-content-center">
    {% if page_obj.has_previous %}
      <li class="page-item"><a class="page-link" href="?page={{ page_obj.previous_page_number }}{% if request.GET.q %}&q={{ request.GET.q }}{% endif %}">Anterior</a></li>
    {% endif %}
    <li class="page-item disabled"><span class="page-link">Página {{ page_obj.number }} de {{ page_obj.paginator.num_pages }}</span></li>
    {% if page_obj.has_next %}
      <li class="page-item"><a class="page-link" href="?page={{ page_obj.next_page_number }}{% if request.GET.q %}&q={{ request.GET.q }}{% endif %}">Siguiente</a></li>
    {% endif %}
  </ul>
</nav>
{% endif %}
{% endblock %}
```

**Paso 4.2:** Crea `security/templates/security/user_form.html`:

```html
{% extends "admin/base_admin.html" %}
{% load static %}
{% block title %}{% if user_obj %}Editar{% else %}Nuevo{% endif %} Usuario{% endblock %}
{% block page_title %}{% if user_obj %}Editar{% else %}Nuevo{% endif %} Usuario{% endblock %}

{% block content %}
<div class="card border-0 shadow-sm" style="max-width:600px">
  <div class="card-body p-4">
    <form method="post">
      {% csrf_token %}
      {% for field in form %}
      <div class="mb-3">
        <label class="form-label fw-semibold">{{ field.label }}</label>
        {{ field }}
        {% if field.help_text %}<div class="form-text">{{ field.help_text }}</div>{% endif %}
        {% for error in field.errors %}<div class="text-danger small">{{ error }}</div>{% endfor %}
      </div>
      {% endfor %}
      <div class="d-flex gap-2">
        <button type="submit" id="btnSubmit" class="btn btn-primary">
          <i class="bi bi-check-lg"></i> {% if user_obj %}Guardar cambios{% else %}Crear usuario{% endif %}
        </button>
        <a href="{% url 'security:user_list' %}" class="btn btn-outline-secondary">Cancelar</a>
      </div>
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

**Paso 4.3:** Crea `security/templates/security/group_list.html`:

```html
{% extends "admin/base_admin.html" %}
{% load static %}
{% block title %}Roles{% endblock %}
{% block page_title %}Gestión de Roles{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-3">
  <span class="text-muted small">{{ group_list|length }} rol(es) registrados</span>
  <a href="{% url 'security:group_create' %}" class="btn btn-primary btn-sm">
    <i class="bi bi-plus-lg"></i> Nuevo Rol
  </a>
</div>

<div class="row g-3">
  {% for g in group_list %}
  <div class="col-12 col-md-6 col-lg-4">
    <div class="card border-0 shadow-sm h-100">
      <div class="card-body">
        <h6 class="fw-bold mb-2"><i class="bi bi-person-badge me-2"></i>{{ g.name }}</h6>
        <p class="small text-muted mb-2">{{ g.user_set.count }} usuario(s)</p>
        <p class="small mb-0">
          {% for p in g.permissions.all|slice:':5' %}
            <span class="badge bg-light text-dark me-1">{{ p.name }}</span>
          {% endfor %}
          {% if g.permissions.count > 5 %}<span class="badge bg-secondary">+{{ g.permissions.count|add:'-5' }}</span>{% endif %}
        </p>
        <a href="{% url 'security:group_update' g.pk %}" class="btn btn-sm btn-outline-secondary mt-3">
          <i class="bi bi-pencil"></i> Editar
        </a>
      </div>
    </div>
  </div>
  {% empty %}
  <div class="col-12"><p class="text-muted text-center py-4">No hay roles. Cree el primero.</p></div>
  {% endfor %}
</div>
{% endblock %}
```

**Paso 4.4:** Crea `security/templates/security/group_form.html`:

```html
{% extends "admin/base_admin.html" %}
{% load static %}
{% block title %}{% if object %}Editar{% else %}Nuevo{% endif %} Rol{% endblock %}
{% block page_title %}{% if object %}Editar{% else %}Nuevo{% endif %} Rol{% endblock %}

{% block content %}
<div class="card border-0 shadow-sm" style="max-width:700px">
  <div class="card-body p-4">
    <form method="post">
      {% csrf_token %}
      <div class="mb-3">
        <label class="form-label fw-semibold">{{ form.name.label }}</label>
        {{ form.name }}
        {% for error in form.name.errors %}<div class="text-danger small">{{ error }}</div>{% endfor %}
      </div>
      <div class="mb-3">
        <label class="form-label fw-semibold">{{ form.permissions.label }}</label>
        <div class="small text-muted mb-2">Seleccione uno o más permisos (Ctrl+clic para múltiples).</div>
        {{ form.permissions }}
      </div>
      <div class="d-flex gap-2">
        <button type="submit" id="btnSubmit" class="btn btn-primary"><i class="bi bi-check-lg"></i> Guardar</button>
        <a href="{% url 'security:group_list' %}" class="btn btn-outline-secondary">Cancelar</a>
      </div>
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

**Paso 4.5:** Crea `security/templates/security/profile.html`:

```html
{% extends "admin/base_admin.html" %}
{% load static %}
{% block title %}Mi Perfil{% endblock %}
{% block page_title %}Mi Perfil{% endblock %}

{% block content %}
<div class="row g-4">
  <div class="col-12 col-lg-4">
    <div class="card border-0 shadow-sm text-center p-4">
      {% if user.foto %}
        <img src="{{ user.foto.url }}" class="rounded-circle mx-auto mb-3" width="120" height="120" style="object-fit:cover">
      {% else %}
        <i class="bi bi-person-circle display-3 text-primary mb-3"></i>
      {% endif %}
      <h5 class="fw-bold">{{ user.get_full_name|default:user.username }}</h5>
      <p class="text-muted small mb-1">{{ user.email }}</p>
      <p class="text-muted small mb-0">Miembro desde: {{ user.date_joined|date:'d/m/Y' }}</p>
      <hr>
      <h6 class="small fw-bold text-uppercase text-muted mb-2">Roles</h6>
      {% for g in groups %}
        <span class="badge bg-secondary me-1">{{ g.name }}</span>
      {% empty %}
        <span class="text-muted small">Sin roles asignados</span>
      {% endfor %}
    </div>
  </div>
  <div class="col-12 col-lg-8">
    <div class="card border-0 shadow-sm">
      <div class="card-body p-4">
        <h6 class="fw-bold mb-3"><i class="bi bi-pencil me-2"></i>Editar Perfil</h6>
        <form method="post" enctype="multipart/form-data">
          {% csrf_token %}
          {% for field in form %}
          <div class="mb-3">
            <label class="form-label fw-semibold">{{ field.label }}</label>
            {{ field }}
            {% for error in field.errors %}<div class="text-danger small">{{ error }}</div>{% endfor %}
          </div>
          {% endfor %}
          <button type="submit" id="btnSubmit" class="btn btn-primary">
            <i class="bi bi-check-lg"></i> Guardar cambios
          </button>
        </form>
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

## Fase 5 — Actualizar el menú (MenuItem)

Para que los submódulos de "Seguridad" tengan URL funcionales, actualiza sus `url_name` en la base de datos:

```python
# Desde el shell de Django
from core.models import MenuItem

MenuItem.all_objects.filter(name='Usuarios').update(url_name='security:user_list')
MenuItem.all_objects.filter(name='Roles').update(url_name='security:group_list')
```

Agrega también la URL del perfil en el sidebar. En `core/context_processors.py`, si el usuario está autenticado, puedes agregar un enlace a `security:profile` desde el footer del sidebar o desde el header.

---

## Fase 5.5 — Verificar integridad

```bash
python manage.py check
```

Debe mostrar: `System check identified no issues (0 silenced).`

## Fase 6 — Probar el sistema

```bash
python manage.py runserver
```

| # | Prueba | Resultado |
|---|--------|-----------|
| 1 | `/security/users/` tabla paginada con usuarios | ✅ |
| 2 | Búsqueda por nombre o email filtra resultados | ✅ |
| 3 | "Nuevo Usuario" crea usuario y redirige con mensaje | ✅ |
| 4 | Editar usuario guarda cambios correctamente | ✅ |
| 5 | Desactivar usuario lo marca como inactivo | ✅ |
| 6 | No puedes desactivarte a ti mismo | ✅ |
| 7 | `/security/groups/` lista roles con permisos | ✅ |
| 8 | Crear rol con permisos funciona | ✅ |
| 9 | `/security/profile/` muestra perfil y formulario | ✅ |
| 10 | Cambio de contraseña funciona correctamente | ✅ |

---

## Próximo laboratorio

[**Lab 07 — CRUD Catálogo (Categorías + Productos)**](./guia-laboratorio-07.md) con modelos, CBVs, búsqueda, paginación y carga de imágenes.
