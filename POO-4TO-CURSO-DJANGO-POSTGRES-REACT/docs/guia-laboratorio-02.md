# Guía de Laboratorio 02 — Módulo Seguridad (User + Login)

> **Parte 2 de 3** · ⏱ **1.5 – 2 horas**
> **Asignatura:** Programación Orientada a Objetos (4to curso)
> **Prerrequisito:** [Parte 1](./guia-laboratorio-01.md) completada (proyecto Django + MySQL).
> **Alcance:** crear app `security/` con modelo User personalizado (`AbstractBaseUser`) y sistema de login.

| ⬅️ Anterior | 📘 Esta guía | ➡️ Siguiente |
|---|---|---|
| [01 — Configuración base](./guia-laboratorio-01.md) | **02** Módulo Seguridad | [**03 — Diagramas UML**](./guia-laboratorio-03.md) |

---

## 1. Fase 4 — App security con `startapp`

### 1.1 Activar entorno

```bash
cd "D:/UNEMI/2026/PERIODO-ABRIL-JUNIO/POO/POO-4TO-CURSO-DJANGO-POSTGRES-REACT/backend"
source .venv/Scripts/activate
```

### 1.2 Crear carpetas base

```bash
mkdir -p templates static/css
```

### 1.3 Crear app con `startapp`

```bash
python manage.py startapp security
```

Resultado:

```
backend/
├── config/            ← Configuración del proyecto
├── security/          ← App de usuarios
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── templates/
├── static/
└── manage.py
```

Archivos adicionales:

```bash
touch security/urls.py security/managers.py
mkdir -p security/templates/security
```

### 1.4 Registrar app

En `config/settings.py`, `LOCAL_APPS`:

```python
LOCAL_APPS = [
    "security",
]
```

---

## 2. Fase 5 — Modelo User personalizado

### 2.1 Manager

📄 **`security/managers.py`**

```python
from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


class CustomUserManager(BaseUserManager):
    def email_validator(self, email):
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError("Debe proporcionar un email válido")

    def create_user(self, username, first_name, last_name, email, password=None, **extra_fields):
        if not username:
            raise ValueError("El username es obligatorio")
        if not first_name:
            raise ValueError("El nombre es obligatorio")
        if not last_name:
            raise ValueError("El apellido es obligatorio")
        if email:
            email = self.normalize_email(email)
            self.email_validator(email)
        else:
            raise ValueError("El email es obligatorio")
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        user = self.model(
            username=username, first_name=first_name, last_name=last_name,
            email=email, **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, first_name, last_name, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser debe tener is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser debe tener is_superuser=True")
        return self.create_user(username, first_name, last_name, email, password, **extra_fields)
```

### 2.2 Instalar Pillow

```bash
pip install Pillow
```

### 2.3 Modelo

📄 **`security/models.py`**

```python
import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager


class User(AbstractBaseUser, PermissionsMixin):
    pkid = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    username = models.CharField(_("usuario"), max_length=150, unique=True)
    first_name = models.CharField(_("nombres"), max_length=50)
    last_name = models.CharField(_("apellidos"), max_length=50)
    email = models.EmailField(_("correo electrónico"), unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    foto = models.ImageField(
        upload_to='users/%Y/%m/%d/',
        verbose_name='Archive Photo',
        max_length=1024,
        blank=True, null=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("usuario")
        verbose_name_plural = _("usuarios")
        ordering = ("-date_joined",)

    def __str__(self):
        return self.username

    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
```

### 2.4 Configurar AUTH_USER_MODEL

En `config/settings.py`, agregue antes de `LOGIN_URL`:

```python
AUTH_USER_MODEL = "security.User"
```

### 2.5 Migrar

> ⚠️ Si ejecutó `migrate` en la guía 01 sin `AUTH_USER_MODEL`, al migrar ahora Django lanzará `InconsistentMigrationHistory`. Solución: borrar BD y volver a migrar.

```bash
rm -f security/migrations/0001_*.py
mysql -u root -p -e "DROP DATABASE ventas_db_local; CREATE DATABASE ventas_db_local CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
# Username: admin | Email: admin@example.com | Password: ********
```

> ✅ Si ya borró la BD y migró sin errores, solo ejecute `python manage.py createsuperuser`.

✅ **Checkpoint:** migraciones OK, superusuario creado.

---

## 3. Fase 6 — Login (autenticación)

### 3.1 Admin

📄 **`security/admin.py`**

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("email",)
    list_display = ("pkid", "id", "email", "username", "first_name", "last_name", "is_staff", "is_active")
    list_display_links = ("id", "email")
    list_filter = ("is_staff", "is_active")
    search_fields = ("email", "username", "first_name", "last_name")
    fieldsets = (
        (_("Credenciales"), {"fields": ("email", "password")}),
        (_("Photo Information"), {"fields": ("foto",)}),
        (_("Información personal"), {"fields": ("username", "first_name", "last_name")}),
        (_("Permisos"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Fechas importantes"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "first_name", "last_name", "password1", "password2"),
        }),
    )
```

### 3.2 Vistas

📄 **`security/views.py`**

```python
from __future__ import annotations

import json
import logging

from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, JsonResponse
from django.views.generic import TemplateView

logger = logging.getLogger(__name__)


class LoginPageView(TemplateView):
    """Vista de login con soporte GET (HTML) y POST (JSON o form).

    - GET  → renderiza security/login.html
    - POST → autentica y retorna JsonResponse
    """
    template_name = "security/login.html"
    http_method_names = ["get", "post"]

    def post(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        try:
            # Detectar content-type: JSON vs formulario tradicional
            if request.content_type == "application/json":
                body = json.loads(request.body)
            else:
                body = request.POST

            username = body.get("username")
            password = body.get("password")

            if not username or not password:
                return JsonResponse(
                    {"resp": False, "error": "Email y contraseña son requeridos"},
                    status=400,
                )

            user = authenticate(request, username=username, password=password)

            if user is None:
                return JsonResponse(
                    {"resp": False, "error": "Credenciales incorrectas"},
                    status=400,
                )

            if not user.is_active:
                logger.warning("Intento de login de usuario inactivo: %s", username)
                return JsonResponse(
                    {"resp": False, "error": "Usuario no habilitado"},
                    status=403,
                )

            login(request, user)
            logger.info("Login exitoso: %s", username)

            return JsonResponse({
                "resp": True,
                "user": {
                    "username": user.username,
                    "email": user.email,
                    "names": f"{user.first_name} {user.last_name}",
                },
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse(
                {"resp": False, "error": "Formato JSON inválido"},
                status=400,
            )
        except Exception:
            logger.exception("Error no controlado en login")
            return JsonResponse(
                {"resp": False, "error": "Error interno del servidor"},
                status=500,
            )


class InicioTemplate(LoginRequiredMixin, TemplateView):
    login_url = "/security/login/"
    redirect_field_name = "redirect_to"
    template_name = "index.html"
```

> 💡 **LoginPageView** está alineada con Django 5.2: usa `sensitive_post_parameters` para filtrar la contraseña en reportes de error, `authenticate(request, ...)` con el objeto request (estándar Django 5+), type hints modernos (`HttpRequest`, `JsonResponse`), `from __future__ import annotations` y detección automática de content-type para soportar peticiones JSON y form.

### 3.3 URLs

📄 **`security/urls.py`**

```python
from django.contrib.auth.views import LogoutView
from django.urls import path
from .views import InicioTemplate, LoginPageView

app_name = "security"
urlpatterns = [
    path("login/", LoginPageView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
```

### 3.4 Templates

📄 **`security/templates/security/login.html`**

```html
{% extends "base.html" %}
{% block title %}Iniciar sesión{% endblock %}
{% block content %}
<div class="row justify-content-center">
  <div class="col-md-5">
    <h2 class="mb-4">Iniciar sesión</h2>
    <form method="post" id="loginForm">
      {% csrf_token %}
      <div class="mb-3">
        <label>Email</label>
        <input type="email" name="username" class="form-control" placeholder="correo@ejemplo.com" required>
      </div>
      <div class="mb-3">
        <label>Contraseña</label>
        <input type="password" name="password" class="form-control" placeholder="********" required>
      </div>
      <button type="submit" class="btn btn-primary w-100">Entrar</button>
      <div id="loginError" class="alert alert-danger mt-3 d-none"></div>
    </form>
  </div>
</div>

<script>
document.getElementById("loginForm").addEventListener("submit", function(e) {
  e.preventDefault();
  const form = this;
  const errorDiv = document.getElementById("loginError");
  fetch(form.action, {
    method: "POST",
    headers: {"X-CSRFToken": "{{ csrf_token }}"},
    body: new FormData(form)
  })
  .then(r => r.json())
  .then(d => {
    if (d.resp) { window.location.href = "/"; }
    else {
      errorDiv.textContent = d.error || "Error al iniciar sesión";
      errorDiv.classList.remove("d-none");
    }
  })
  .catch(() => {
    errorDiv.textContent = "Error de conexión";
    errorDiv.classList.remove("d-none");
  });
});
</script>
{% endblock %}
```

📄 **`templates/index.html`**

```html
{% extends "base.html" %}
{% block title %}Inicio{% endblock %}
{% block content %}
<div class="text-center mt-5">
  <h1>Bienvenido, {{ user.get_full_name }}</h1>
  <p class="lead">Has iniciado sesión correctamente.</p>
  <p>Email: {{ user.email }}</p>
</div>
{% endblock %}
```

### 3.5 Enrutamiento principal

Reemplace **todo el contenido** de `config/urls.py`:

📄 **`config/urls.py`**

```python
from django.contrib import admin
from django.urls import include, path
from security.views import InicioTemplate

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", InicioTemplate.as_view(), name="home"),
    path("security/", include("security.urls")),
]
```

> 💡 **LogoutView** usa `LOGOUT_REDIRECT_URL` de `settings.py` (`/security/login/`). Al cerrar sesión redirige al login.

✅ **Checkpoint:** `/security/login/` y `/` (home protegido) funcionan.

---

## 4. Fase 7 — Template base con Bootstrap

📄 **`templates/base.html`**

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}App{% endblock %}</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
    <div class="container">
      <a class="navbar-brand" href="{% url 'home' %}">App</a>
      <div class="navbar-nav ms-auto">
        {% if user.is_authenticated %}
          <span class="nav-link text-light">{{ user.get_full_name }}</span>
          <form method="post" action="{% url 'security:logout' %}" class="d-inline">
            {% csrf_token %}
            <button type="submit" class="btn nav-link text-danger">Salir</button>
          </form>
        {% endif %}
      </div>
    </div>
  </nav>
  <div class="container">{% block content %}{% endblock %}</div>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

---

## 5. Probar el sistema

```bash
python manage.py runserver
```

| Prueba | URL | Esperado |
|---|---|---|
| Admin | `http://127.0.0.1:8000/admin/` | Login con superusuario |
| Login | `http://127.0.0.1:8000/security/login/` | Login con email y contraseña (AJAX) |
| Home | `http://127.0.0.1:8000/` | Dashboard protegido con datos del usuario |
| Logout | Cerrar sesión | Redirige a login |

---

## Cierre

- [x] App `security/` creada con `startapp`.
- [x] Modelo `User` personalizado (AbstractBaseUser + PermissionsMixin + CustomUserManager).
- [x] Login con email (`USERNAME_FIELD = "email"`).
- [x] Admin con fieldsets.
- [x] Vista Home protegida con `LoginRequiredMixin`.
- [x] Template base Bootstrap reutilizable.

➡️ [**Parte 3 — Diagramas UML del Sistema**](./guia-laboratorio-03.md)
