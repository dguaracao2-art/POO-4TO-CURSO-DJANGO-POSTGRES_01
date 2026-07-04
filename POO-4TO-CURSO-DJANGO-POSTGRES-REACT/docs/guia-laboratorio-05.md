# Guía de Laboratorio 05 — Panel Administrativo Profesional

## Objetivo

Construir el layout profesional del panel administrativo con sidebar, encabezado, panel de contenido, context processor del menú y template tags personalizados para filtrar por permisos.

## Duración estimada

2 horas (presencial) + 1 hora (trabajo autónomo)

## Prerrequisitos

- Laboratorio 04 completado (app core, MenuItem con seed data)
- Laboratorio 03b completado (login profesional funcional)
- Servidor Django funcionando

## Estructura final

```
backend/
├── core/
│   ├── context_processors.py         (NUEVO) — inyecta menú en todas las plantillas
│   ├── templatetags/
│   │   ├── __init__.py
│   │   └── menu_tags.py              (NUEVO) — filtros has_access, accessible_children
│   └── static/core/
│       ├── css/admin.css             (NUEVO) — estilos del panel
│       └── js/admin.js               (NUEVO) — interactividad del sidebar
├── templates/
│   ├── index.html                    (MODIFICADO) — ahora extiende base_admin
│   └── admin/
│       └── base_admin.html           (NUEVO) — layout sidebar + header + main
└── config/
    └── settings.py                   (MODIFICADO) — + context processor
```

---

## Fase 1 — Context Processor

**Paso 1.1:** Crea `core/context_processors.py`:

```python
from .models import MenuItem


def menu_items(request):
    if not request.user.is_authenticated:
        return {'menu_modules': []}
    modules = MenuItem.all_objects.filter(
        parent__isnull=True, is_active=True
    ).order_by('order')
    return {'menu_modules': modules}
```

**Paso 1.2:** En `config/settings.py`, agrega el context processor:

```python
TEMPLATES = [
    {
        ...
        "OPTIONS": {
            "context_processors": [
                ...
                "core.context_processors.menu_items",
            ],
        },
    },
]
```

---

## Fase 2 — Template Tags para Permisos

Los métodos `has_access(user)` y `accessible_children(user)` necesitan el argumento `user`. Django templates no soportan llamar métodos con argumentos directamente, así que creamos **template tags** (filtros personalizados).

**Paso 2.1:** Crea la carpeta y archivos:

```bash
mkdir -p core/templatetags
touch core/templatetags/__init__.py
```

**Paso 2.2:** Crea `core/templatetags/menu_tags.py`:

```python
from django import template

register = template.Library()


@register.filter
def has_access(menu_item, user):
    return menu_item.has_access(user)


@register.filter
def accessible_children(menu_item, user):
    return menu_item.accessible_children(user)
```

---

## Fase 3 — Admin Layout (base_admin.html)

**Paso 3.1:** Crea la carpeta y el archivo:

```bash
mkdir -p templates/admin
```

**Paso 3.2:** Crea `templates/admin/base_admin.html`:

```html
{% load static %}
{% load menu_tags %}
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}SIF — Panel{% endblock %}</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css" rel="stylesheet">
  <link href="{% static 'core/css/admin.css' %}" rel="stylesheet">
  {% block extra_head %}{% endblock %}
</head>
<body>
  <div class="admin-wrapper">
    <!-- SIDEBAR -->
    <aside class="sidebar" id="sidebar">
      <div class="sidebar-header">
        <a href="{% url 'home' %}" class="sidebar-brand">
          <i class="bi bi-receipt-cutoff"></i>
          <span class="brand-text">SIF</span>
        </a>
        <button class="sidebar-toggle d-lg-none" id="sidebarClose" aria-label="Cerrar menú">
          <i class="bi bi-x-lg"></i>
        </button>
      </div>
      <div class="sidebar-search">
        <div class="input-group input-group-sm">
          <span class="input-group-text bg-transparent border-0 text-secondary">
            <i class="bi bi-search"></i>
          </span>
          <input type="text" class="form-control form-control-sm bg-transparent border-0 text-light"
                 id="menuFilter" placeholder="Buscar menú...">
        </div>
      </div>
      <nav class="sidebar-nav" id="sidebarNav">
        {% for module in menu_modules %}
          {% if module|has_access:request.user %}
          <div class="sidebar-module">
            <div class="module-header" data-target="ch-{{ module.id }}">
              <i class="bi {{ module.icon }} module-icon"></i>
              <span class="module-name">{{ module.name }}</span>
              {% with children=module|accessible_children:request.user %}
                {% if children %}
                  <i class="bi bi-chevron-down module-chevron"></i>
                {% endif %}
              {% endwith %}
            </div>
            {% with children=module|accessible_children:request.user %}
              {% if children %}
              <div class="module-children" id="ch-{{ module.id }}">
                {% for child in children %}
                  {% if child.url_name %}
                  <a href="{% url child.url_name %}" class="child-link">
                    <i class="bi {{ child.icon }}"></i><span>{{ child.name }}</span>
                  </a>
                  {% else %}
                  <span class="child-link disabled">
                    <i class="bi {{ child.icon }}"></i><span>{{ child.name }}</span>
                    <small class="text-secondary">próximamente</small>
                  </span>
                  {% endif %}
                {% endfor %}
              </div>
              {% endif %}
            {% endwith %}
          </div>
          {% endif %}
        {% empty %}
          <div class="px-3 py-2">
            <div class="skeleton skeleton-text mb-2"></div>
            <div class="skeleton skeleton-text-sm mb-2"></div>
            <div class="skeleton skeleton-text mb-2"></div>
            <div class="skeleton skeleton-text-sm mb-2"></div>
            <div class="skeleton skeleton-text mb-2"></div>
          </div>
        {% endfor %}
      </nav>
      <div class="sidebar-footer">
        <div class="d-flex align-items-center">
          <i class="bi bi-person-circle fs-5 me-2 text-secondary"></i>
          <div class="small">
            <div class="text-light">{{ user.get_full_name|default:user.email }}</div>
            <form method="post" action="{% url 'security:logout' %}">
              {% csrf_token %}
              <button type="submit" class="btn btn-sm btn-link text-secondary p-0">
                <i class="bi bi-box-arrow-right me-1"></i>Cerrar sesión
              </button>
            </form>
          </div>
        </div>
      </div>
    </aside>
    <div class="sidebar-overlay" id="sidebarOverlay"></div>
    <!-- MAIN -->
    <div class="main-content">
      <header class="main-header">
        <div class="d-flex align-items-center">
          <button class="btn btn-header me-3" id="sidebarToggle" aria-label="Abrir menú">
            <i class="bi bi-list fs-5"></i>
          </button>
          <div>
            <h5 class="mb-0 page-title">{% block page_title %}Panel Principal{% endblock %}</h5>
            <small class="text-muted">{% block page_subtitle %}{% now "d/m/Y" %}{% endblock %}</small>
          </div>
        </div>
      </header>
      <div class="content-area">
        {% if messages %}
          {% for message in messages %}
          <div class="alert alert-{{ message.tags|default:'info' }} alert-dismissible fade show">
            {{ message }}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>
          </div>
          {% endfor %}
        {% endif %}
        {% block content %}{% endblock %}
      </div>
    </div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
  <script src="{% static 'core/js/admin.js' %}"></script>
  {% block extra_scripts %}{% endblock %}
</body>
</html>
```

---

## Fase 4 — CSS del Panel (admin.css)

**Paso 4.1:** Crea `core/static/core/css/admin.css`:

```css
:root {
  --sidebar-width: 260px;
  --sidebar-bg: #1e293b;
  --sidebar-hover: #334155;
  --sidebar-active: #4e73df;
  --header-bg: #ffffff;
  --content-bg: #f1f5f9;
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --border-color: #e2e8f0;
}

html, body { height: 100%; margin: 0; font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif; background: var(--content-bg); }
.admin-wrapper { display: flex; height: 100vh; overflow: hidden; }

/* SIDEBAR */
.sidebar {
  width: var(--sidebar-width);
  min-width: var(--sidebar-width);
  background: var(--sidebar-bg);
  color: #cbd5e1;
  display: flex;
  flex-direction: column;
  transition: transform .3s ease;
  z-index: 1040;
}
.sidebar-header { display: flex; align-items: center; justify-content: space-between; padding: 1rem 1.25rem; border-bottom: 1px solid rgba(255,255,255,.08); }
.sidebar-brand { display: flex; align-items: center; gap: .5rem; color: #fff; text-decoration: none; font-size: 1.25rem; font-weight: 700; }
.sidebar-brand i { font-size: 1.5rem; color: var(--sidebar-active); }
.sidebar-search { padding: .75rem 1rem; border-bottom: 1px solid rgba(255,255,255,.06); }
.sidebar-nav { flex: 1; overflow-y: auto; padding: .5rem 0; }

.module-header { display: flex; align-items: center; padding: .625rem 1.25rem; cursor: pointer; transition: background .15s; gap: .75rem; user-select: none; }
.module-header:hover { background: var(--sidebar-hover); }
.module-icon { font-size: 1.1rem; width: 1.25rem; text-align: center; }
.module-name { flex: 1; font-size: .9rem; font-weight: 500; }
.module-chevron { font-size: .75rem; transition: transform .2s; color: #64748b; }
.module-header.open .module-chevron { transform: rotate(180deg); }
.module-children { display: none; background: rgba(0,0,0,.15); }
.module-header.open + .module-children,
.module-children.open { display: block; }

.child-link { display: flex; align-items: center; gap: .75rem; padding: .5rem 1.25rem .5rem 3.25rem; color: #94a3b8; text-decoration: none; font-size: .85rem; transition: all .15s; }
.child-link:hover { color: #fff; background: var(--sidebar-hover); }
.child-link.active { color: #fff; background: var(--sidebar-active); }
.child-link.disabled { opacity: .45; cursor: default; }
.sidebar-footer { padding: 1rem 1.25rem; border-top: 1px solid rgba(255,255,255,.08); }
.sidebar-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,.5); z-index: 1030; }

/* MAIN */
.main-content { flex: 1; display: flex; flex-direction: column; min-width: 0; overflow: hidden; }
.main-header { display: flex; align-items: center; justify-content: space-between; padding: .75rem 1.5rem; background: var(--header-bg); border-bottom: 1px solid var(--border-color); min-height: 64px; }
.btn-header { background: none; border: none; color: var(--text-secondary); padding: .25rem .5rem; cursor: pointer; }
.page-title { font-size: 1.1rem; font-weight: 600; }
.content-area { flex: 1; overflow-y: auto; padding: 1.5rem; }

/* ACCORDION */
.accordion-module { background: #fff; border: 1px solid var(--border-color); border-radius: 10px; margin-bottom: 1rem; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,.04); }
.accordion-header { display: flex; align-items: center; padding: 1rem 1.25rem; cursor: pointer; gap: 1rem; user-select: none; }
.accordion-header i:first-child { font-size: 1.5rem; width: 2rem; text-align: center; }
.accordion-header .acc-title { flex: 1; font-weight: 600; color: var(--text-primary); }
.accordion-header .acc-chevron { transition: transform .2s; color: var(--text-secondary); }
.accordion-header.open .acc-chevron { transform: rotate(180deg); }
.accordion-body { display: none; padding: 0 1.25rem 1rem 4.25rem; }
.accordion-body.open { display: block; }
.acc-item { display: flex; align-items: center; gap: .75rem; padding: .5rem .75rem; margin: 2px 0; color: var(--text-secondary); text-decoration: none; border-radius: 8px; transition: all .15s; }
.acc-item:hover { background: #f1f5f9; color: var(--sidebar-active); }

@media (max-width: 991.98px) {
  .sidebar { position: fixed; top: 0; left: 0; height: 100%; transform: translateX(-100%); }
  .sidebar.open { transform: translateX(0); }
  .sidebar-overlay.active { display: block; }
}
:focus-visible { outline: 2px solid var(--sidebar-active); outline-offset: 2px; }
```

---

## Fase 5 — JavaScript del Panel (admin.js)

**Paso 5.1:** Crea `core/static/core/js/admin.js`:

```javascript
(function () {
  'use strict';
  class AdminLayout {
    constructor() {
      this.sidebar = document.getElementById('sidebar');
      this.overlay = document.getElementById('sidebarOverlay');
      this.toggleBtn = document.getElementById('sidebarToggle');
      this.closeBtn = document.getElementById('sidebarClose');
      this.filterInput = document.getElementById('menuFilter');
      this._init();
    }
    _init() {
      this._bindSidebarToggle();
      this._bindModuleToggle();
      this._bindFilter();
      this._highlightActive();
      this._openCurrentModule();
    }
    _bindSidebarToggle() {
      this.toggleBtn?.addEventListener('click', () => this.sidebar?.classList.add('open') || this.overlay?.classList.add('active'));
      this.closeBtn?.addEventListener('click', () => this._close());
      this.overlay?.addEventListener('click', () => this._close());
    }
    _close() { this.sidebar?.classList.remove('open'); this.overlay?.classList.remove('active'); }
    _bindModuleToggle() {
      document.querySelectorAll('.module-header').forEach(el => {
        el.addEventListener('click', (e) => {
          e.stopPropagation();
          const children = el.nextElementSibling;
          if (!children?.classList.contains('module-children')) return;
          children.classList.toggle('open');
          el.classList.toggle('open');
        });
      });
    }
    _bindFilter() {
      this.filterInput?.addEventListener('input', (e) => {
        const q = e.target.value.toLowerCase().trim();
        document.querySelectorAll('.sidebar-module').forEach(mod => {
          const name = mod.querySelector('.module-name')?.textContent?.toLowerCase() || '';
          const children = mod.querySelectorAll('.child-link');
          let match = name.includes(q);
          children.forEach(ch => {
            const text = ch.textContent.toLowerCase();
            ch.style.display = text.includes(q) || !q ? '' : 'none';
            if (text.includes(q) && q) match = true;
          });
          mod.style.display = match || !q ? '' : 'none';
        });
      });
    }
    _highlightActive() {
      const current = window.location.pathname;
      document.querySelectorAll('.child-link').forEach(link => {
        if (link.getAttribute('href') === current) link.classList.add('active');
      });
    }
    _openCurrentModule() {
      const active = document.querySelector('.child-link.active');
      if (!active) return;
      const children = active.closest('.module-children');
      const header = children?.previousElementSibling;
      if (children && header) { children.classList.add('open'); header.classList.add('open'); }
    }
  }
  document.addEventListener('DOMContentLoaded', () => { new AdminLayout(); });
})();
```

---

## Fase 6 — Home (index.html)

**Paso 6.1:** Reemplaza `templates/index.html`:

```html
{% extends "admin/base_admin.html" %}
{% load static %}
{% load menu_tags %}
{% block title %}Inicio{% endblock %}
{% block page_title %}Panel Principal{% endblock %}

{% block content %}
<div class="row g-4">
  <div class="col-12 col-lg-4">
    <div class="card border-0 shadow-sm h-100">
      <div class="card-body text-center p-4">
        <i class="bi bi-person-circle display-6 text-primary mb-3 d-block"></i>
        <h5 class="fw-bold">Bienvenido, {{ user.first_name|default:user.username }}</h5>
        <p class="text-muted small mb-0">{{ user.email }}</p>
      </div>
    </div>
  </div>
  <div class="col-12 col-lg-8">
    <div class="row g-3">
      <div class="col-6 col-md-3">
        <div class="card border-0 shadow-sm text-center p-3 h-100 skeleton-card">
          <i class="bi bi-receipt fs-2 text-primary d-block"></i>
          <div class="fw-bold fs-5 mt-1">0</div>
          <small class="text-muted">Facturas Hoy</small>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card border-0 shadow-sm text-center p-3 h-100 skeleton-card">
          <i class="bi bi-currency-dollar fs-2 text-success d-block"></i>
          <div class="fw-bold fs-5 mt-1">$0</div>
          <small class="text-muted">Ventas del Mes</small>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card border-0 shadow-sm text-center p-3 h-100 skeleton-card">
          <i class="bi bi-people fs-2 text-info d-block"></i>
          <div class="fw-bold fs-5 mt-1">0</div>
          <small class="text-muted">Clientes</small>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card border-0 shadow-sm text-center p-3 h-100 skeleton-card">
          <i class="bi bi-exclamation-triangle fs-2 text-warning d-block"></i>
          <div class="fw-bold fs-5 mt-1">0</div>
          <small class="text-muted">Stock Bajo</small>
        </div>
      </div>
    </div>
  </div>
  <div class="col-12">
    <h5 class="fw-bold mb-3"><i class="bi bi-grid me-2"></i>Módulos del Sistema</h5>
    {% for module in menu_modules %}
      {% if module|has_access:request.user %}
      <div class="accordion-module">
        <div class="accordion-header" data-target="am-{{ module.id }}">
          <i class="bi {{ module.icon }} text-primary"></i>
          <span class="acc-title">{{ module.name }}</span>
          {% with children=module|accessible_children:request.user %}
            {% if children %}<i class="bi bi-chevron-down acc-chevron"></i>{% endif %}
          {% endwith %}
        </div>
        {% with children=module|accessible_children:request.user %}
          {% if children %}
          <div class="accordion-body" id="am-{{ module.id }}">
            {% for child in children %}
              {% if child.url_name %}
              <a href="{% url child.url_name %}" class="acc-item">
                <i class="bi {{ child.icon }}"></i><span>{{ child.name }}</span>
              </a>
              {% else %}
              <div class="acc-item disabled text-muted opacity-50">
                <i class="bi {{ child.icon }}"></i><span>{{ child.name }}</span>
                <small class="ms-auto">próximamente</small>
              </div>
              {% endif %}
            {% endfor %}
          </div>
          {% endif %}
        {% endwith %}
      </div>
      {% endif %}
    {% endfor %}
  </div>
</div>
{% endblock %}
```

---

## Fase 7 — Verificación

```bash
python manage.py check
python manage.py runserver
```

1. Autentícate → ves sidebar con 5 módulos y submódulos
2. Submódulos sin URL muestran "próximamente" (deshabilitados)
3. El buscador en el sidebar filtra en tiempo real
4. En mobile (< 992px) el sidebar se oculta; aparece con ☐
5. El ítem activo se destaca con fondo azul (#4e73df)

## Próximo laboratorio

[**Lab 06 — CRUD Usuarios + Roles y Permisos**](./guia-laboratorio-06.md) con CBVs, búsqueda y paginación.
