# Roadmap de Laboratorios — Sistema de Facturación (Django MVT)

> **Base de datos principal:** MySQL 8.0+ · **Opcional:** PostgreSQL 15+

## Metodología

Cada laboratorio representa un **Sprint** de 1 semana. Las **Historias de Usuario** se registran en Jira y se estiman en puntos (1-5 pts = 1-5 días). Al final de cada sprint hay un **checkpoint de verificación**.

---

## Proyecto completo

```
Sprint 1  │ Lab 01 │ Configuración Django + MySQL                  📄
Sprint 2  │ Lab 02 │ App Security (User, Login, Admin)             📄
Sprint 3  │ Lab 03 │ Diagramas UML                                 📄
Sprint 4  │ Lab 03b│ Login Profesional (Bootstrap 5 + Axios)       📄
────────────────────────────────────────────────────────────────────
Sprint 5  │ Lab 04 │ App Core (BaseModel, MenuItem, SoftDelete)    📄
Sprint 6  │ Lab 05 │ Panel Admin (Sidebar + Layout + Context)      📄
Sprint 7  │ Lab 06 │ CRUD Usuarios + Roles y Permisos              📄
Sprint 8  │ Lab 07 │ CRUD Catálogo (Categorías + Productos)        📄
Sprint 9  │ Lab 08 │ CRUD Clientes                                 📄
Sprint 10 │ Lab 09 │ Facturación Transaccional (ACID)              📄
Sprint 11 │ Lab 10 │ Dashboard + Card Resume + Chart.js          📄
Sprint 12 │ Lab 11 │ Verificación Final + Despliegue               📄
Sprint 13 │ Lab 12 │ Reportes Profesionales PDF                    📄
```

---

## LAB 01 — Configuración Base y Proyecto Django

**Objetivo:** Crear entorno virtual, instalar Django, configurar MySQL, proyecto base.

### User Stories

| ID | Historia | Pts |
|----|----------|:---:|
| HU-01 | Como **desarrollador** quiero configurar el entorno virtual con Python 3.12 para aislar dependencias del proyecto | 1 |
| HU-02 | Como **desarrollador** quiero instalar Django 6.0.6 y conectar MySQL para tener la base de datos operativa | 2 |
| HU-03 | Como **desarrollador** quiero crear el proyecto Django `config` con settings modular para mantener una configuración limpia | 2 |
| HU-04 | Como **desarrollador** quiero configurar variables de entorno con `python-decouple` para no exponer credenciales en el código | 1 |

**Total Sprint: 6 pts**

**Frontend:** Ninguno (solo backend)
**Backend:** `python manage.py runserver` con página de bienvenida Django

---

## LAB 02 — App Security: Modelo User Personalizado + Login

**Objetivo:** Crear app `security` con modelo User, login por email, admin, templates Bootstrap.

### User Stories

| ID | Historia | Pts |
|----|----------|:---:|
| HU-05 | Como **desarrollador** quiero crear un modelo User personalizado con email como USERNAME_FIELD para autenticar por correo | 3 |
| HU-06 | Como **usuario** quiero iniciar sesión con email y contraseña para acceder al sistema | 3 |
| HU-07 | Como **administrador** quiero gestionar usuarios desde el panel de Django admin para administrar el sistema | 2 |
| HU-08 | Como **usuario** quiero ver mi nombre en la barra de navegación después de iniciar sesión para confirmar que estoy autenticado | 1 |

**Total Sprint: 9 pts**

**Frontend:** Templates Bootstrap básicos (login, base, home)
**Backend:** `security/models.py`, `security/views.py`, `security/admin.py`, `security/urls.py`

---

## LAB 03 — Diagramas UML + Verificación

**Objetivo:** Documentar la arquitectura con diagramas PlantUML y verificar el funcionamiento.

### User Stories

| ID | Historia | Pts |
|----|----------|:---:|
| HU-09 | Como **arquitecto** quiero crear diagramas UML de clases, secuencia y ER para documentar el diseño del sistema | 3 |
| HU-10 | Como **analista** quiero verificar que todos los componentes del sistema funcionan correctamente mediante un checklist | 2 |

**Total Sprint: 5 pts**

**Archivos creados:** Diagramas PlantUML en `docs/uml/`

---

## LAB 03b — Login Profesional con Bootstrap 5 + Axios + SOLID

**Objetivo:** Rediseñar el login con split-screen profesional, accesibilidad, Axios y SOLID en JS.

### User Stories

| ID | Historia | Pts |
|----|----------|:---:|
| HU-11 | Como **usuario** quiero una pantalla de login profesional con diseño split-screen para tener una experiencia agradable | 3 |
| HU-12 | Como **usuario** quiero que el login sea accesible (ARIA, teclado, validación) para poder usarlo sin dificultad | 2 |
| HU-13 | Como **desarrollador** quiero separar el JavaScript en 3 clases con responsabilidades únicas (ApiClient, AuthService, LoginController) para aplicar SOLID | 3 |
| HU-14 | Como **desarrollador** quiero usar Axios en lugar de fetch para las peticiones asíncronas para tener un manejo de errores más robusto | 1 |

**Total Sprint: 9 pts**

**Frontend:** `login.css`, `app.css`, `api-client.js`, `auth-service.js`, `login.js`, `login.html` rediseñado
**Backend:** Sin cambios (vista de login existente)

---

## LAB 04 — App Core: BaseModel + MenuItem + SoftDelete

**Objetivo:** Crear la app `core` con `BaseModel`, `SoftDeleteManager`, modelo `MenuItem` auto-referencial, seed data y admin.

### User Stories

| ID | Historia | Pts |
|----|----------|:---:|
| HU-15 | Como **desarrollador** quiero un BaseModel abstracto con created_at/updated_at/is_active/deleted_at para que todos los modelos tengan auditoría | 2 |
| HU-16 | Como **desarrollador** quiero implementar SoftDelete para poder restaurar registros eliminados accidentalmente | 2 |
| HU-17 | Como **administrador** quiero un modelo de menú jerárquico (módulos → submódulos) con permisos asociados para controlar la navegación del sistema | 5 |
| HU-18 | Como **desarrollador** quiero una migración de datos semilla con la estructura inicial del menú para tener el sistema preconfigurado | 2 |

**Total Sprint: 11 pts**

**Frontend:** Ninguno
**Backend:** `core/models.py`, `core/admin.py`, migraciones

---

## LAB 05 — Panel Administrativo (Sidebar + Layout + Context Processor)

**Objetivo:** Construir el layout profesional del panel con sidebar izquierdo, panel principal derecho, context processor del menú, diseño UX profesional con Bootstrap 5.

### User Stories

| ID | Historia | Pts |
|----|----------|:---:|
| HU-19 | Como **usuario** quiero un panel administrativo con sidebar izquierdo que muestre los módulos del sistema para navegar fácilmente | 5 |
| HU-20 | Como **usuario** quiero que el panel principal muestre los módulos en accordion con acceso directo a los submódulos para visualizar todo el sistema | 3 |
| HU-21 | Como **usuario** quiero que el menú solo muestre los módulos/submódulos que tengo permiso de ver para no ver opciones no autorizadas | 3 |

**Total Sprint: 11 pts**

**Frontend:**
- `core/static/core/css/admin.css` — Estilos del panel (sidebar, accordion)
- `core/static/core/js/admin.js` — Sidebar toggle, accordion interactivo (SOLID)
- `templates/admin/base_admin.html` — Layout base con sidebar + panel
- `templates/admin/panel.html` — Panel principal con accordion de módulos
- `templates/base.html` — Redirección a admin layout

**Backend:**
- `core/context_processors.py` — Menú del sidebar
- `config/settings.py` — Agregar context processor
- `core/views.py` — DashboardView (hereda de TemplateView)

**UX Features:**
- Sidebar colapsable (toggle button)
- Módulo activo destacado (clase `.active`)
- Accordion con animación suave
- Responsive: sidebar se oculta en mobile, menú hamburguesa
- Indicador de submódulos con permisos
- Footer con datos del usuario y cerrar sesión

---

## LAB 06 — Gestión de Usuarios y Roles

**Objetivo:** CRUD completo de usuarios y roles (grupos) con CBVs, búsqueda, paginación y asignación de permisos.

### User Stories

| ID | Historia | Pts |
|----|----------|:---:|
| HU-22 | Como **administrador** quiero listar, crear, editar y desactivar usuarios para gestionar el acceso al sistema | 5 |
| HU-23 | Como **administrador** quiero crear roles (grupos) con permisos específicos para controlar qué puede hacer cada perfil | 3 |
| HU-24 | Como **administrador** quiero asignar usuarios a roles para otorgarles permisos de forma masiva | 2 |
| HU-25 | Como **usuario** quiero ver y editar mi perfil (nombre, email, contraseña, foto) para mantener mis datos actualizados | 3 |

**Total Sprint: 13 pts**

**Frontend:**
- `security/static/security/js/user-list.js` — CRUD asíncrono (Axios)
- `security/templates/security/user_list.html` — Tabla con búsqueda
- `security/templates/security/user_form.html` — Modal/formulario
- `security/templates/security/profile.html` — Perfil de usuario

**Backend:**
- `security/views.py` — UserListView, UserCreateView, UserUpdateView, UserDeleteView, ProfileView
- `security/forms.py` — UserForm, ProfileForm, GroupForm
- `security/urls.py` — URLs para CRUD usuarios + grupos

---

## LAB 07 — CRUD Catálogo (Categorías + Productos)

**Objetivo:** Crear app `catalog` con modelos Categoría y Producto, CRUD completo, búsqueda, paginación y foto de producto.

### User Stories

| ID | Historia | Pts |
|----|----------|:---:|
| HU-26 | Como **administrador** quiero gestionar categorías (crear, editar, listar, desactivar) para clasificar los productos | 3 |
| HU-27 | Como **administrador** quiero gestionar productos con nombre, precio, stock, categoría y foto para mantener el inventario | 5 |
| HU-28 | Como **vendedor** quiero buscar productos por nombre o categoría para encontrar rápidamente lo que necesito | 3 |
| HU-29 | Como **vendedor** quiero ver el stock disponible de cada producto para saber si puedo venderlo | 1 |

**Total Sprint: 12 pts**

**Frontend:**
- `catalog/static/catalog/js/catalog.js` — CRUD asíncrono
- `catalog/templates/catalog/` — Listados y formularios

**Backend:**
- `catalog/models.py` — Categoria, Producto (heredan BaseModel)
- `catalog/views.py` — CBVs con SearchMixin, PaginationMixin
- `catalog/forms.py`
- `catalog/urls.py`

---

## LAB 08 — CRUD Clientes

**Objetivo:** Crear app `customers` con modelo Cliente, CRUD completo, búsqueda por cédula/nombre/email, validación de cédula.

### User Stories

| ID | Historia | Pts |
|----|----------|:---:|
| HU-30 | Como **vendedor** quiero registrar clientes con nombre, cédula, email, teléfono y dirección para crear facturas | 3 |
| HU-31 | Como **vendedor** quiero buscar clientes por cédula o nombre para agilizar el proceso de facturación | 2 |
| HU-32 | Como **administrador** quiero editar y desactivar clientes para mantener la base de datos actualizada | 2 |
| HU-33 | Como **vendedor** quiero validar que el email y cédula sean únicos para evitar duplicados | 1 |

**Total Sprint: 8 pts**

**Frontend:**
- `customers/static/customers/js/customers.js` — CRUD asíncrono
- `customers/templates/customers/` — Listados y formularios

**Backend:**
- `customers/models.py` — Cliente (hereda BaseModel)
- `customers/views.py` — CBVs
- `customers/forms.py`
- `customers/urls.py`

---

## LAB 09 — Facturación Transaccional (ACID)

**Objetivo:** Crear app `invoicing` con modelos Factura y DetalleFactura, transacciones ACID, stock atómico con `F()`, IVA, anulación.

### User Stories

| ID | Historia | Pts |
|----|----------|:---:|
| HU-34 | Como **vendedor** quiero crear una factura seleccionando cliente, productos y cantidades para registrar una venta | 5 |
| HU-35 | Como **vendedor** quiero que el stock se descuente automáticamente con F() para mantener el inventario consistente sin condiciones de carrera | 3 |
| HU-36 | Como **vendedor** quiero que el IVA (15%) y subtotales se calculen automáticamente para evitar errores manuales | 2 |
| HU-37 | Como **administrador** quiero anular una factura y restaurar el stock atómicamente para corregir errores | 5 |
| HU-38 | Como **usuario** quiero ver el historial de facturas con filtros por fecha y cliente para consultar ventas anteriores | 3 |
| HU-38b | Como **vendedor** quiero una interfaz profesional con buscador de productos, tabla de detalles editable en vivo y totales automáticos para facturar rápido | 3 |

**Total Sprint 10: 21 pts**

**Total Sprint: 21 pts**

**Frontend:**
- `invoicing/static/invoicing/js/invoice-service.js` — Lógica de negocio (SRP)
- `invoicing/static/invoicing/js/invoice-calculator.js` — Cálculos financieros (SRP)
- `invoicing/static/invoicing/js/invoice-form.js` — Controlador DOM (SRP)
- `invoicing/static/invoicing/css/invoice.css` — Estilos profesionales
- `invoicing/templates/invoicing/invoice_form.html` — Formulario maestro-detalle
- `invoicing/templates/invoicing/invoice_list.html` — Historial con filtros
- `invoicing/templates/invoicing/invoice_detail.html` — Vista de factura

**Backend:**
- `invoicing/models.py` — Factura (maestro), DetalleFactura (detalle)
- `invoicing/services.py` — FacturaService.crear(), .anular() con `@transaction.atomic` y `F()`
- `invoicing/views.py` — InvoiceListView, InvoiceCreateView, InvoiceDetailView, InvoiceAnnulView
- `invoicing/urls.py`
- `invoicing/forms.py`

**Reglas de negocio:** Número secuencial, stock suficiente con F(), cálculo automático, transacción completa, anulación con restauración atómica.

---

## LAB 10 — Dashboard con Chart.js

**Objetivo:** Dashboard principal con tarjetas de resumen, gráficos (Chart.js), últimos movimientos, accesos rápidos.

### User Stories

| ID | Historia | Pts |
|----|----------|:---:|
| HU-39 | Como **usuario** quiero ver un dashboard con tarjetas de resumen (facturas hoy, total ventas, productos bajos en stock) para tener una visión general del negocio | 3 |
| HU-40 | Como **administrador** quiero ver un gráfico de ventas por día/semana/mes para analizar tendencias | 3 |
| HU-41 | Como **usuario** quiero ver las últimas 5 facturas creadas en el dashboard para tener acceso rápido | 2 |
| HU-42 | Como **vendedor** quiero accesos directos a "Nueva Factura" y "Buscar Cliente" desde el dashboard para ser más eficiente | 1 |

**Total Sprint: 9 pts**

**Frontend:**
- `dashboard/static/dashboard/js/dashboard.js` — Gráficos Chart.js
- `dashboard/static/dashboard/css/dashboard.css`
- `dashboard/templates/dashboard/` — Cards, gráficos, tabla

**Backend:**
- `dashboard/views.py` — DashboardView
- `dashboard/urls.py`

---

## LAB 11 — Verificación Final y Despliegue

**Objetivo:** Testing, checklist final, documentación de despliegue, cierre del proyecto.

### User Stories

| ID | Historia | Pts |
|----|----------|:---:|
| HU-43 | Como **analista** quiero ejecutar las pruebas de aceptación para verificar que todas las funcionalidades cumplen los requisitos | 3 |
| HU-44 | Como **desarrollador** quiero documentar los pasos de despliegue en producción para que el sistema pueda ser instalado en cualquier entorno | 2 |
| HU-45 | Como **product owner** quiero revisar el sprint final con el checklist completo para dar por finalizado el proyecto | 1 |

**Total Sprint: 6 pts**

---
## LAB 12 — Reportes Profesionales PDF

**Objetivo:** Implementar generación de reportes PDF profesionales con xhtml2pdf, incluyendo cierre diario y listado de facturas por periodo.

### User Stories

| ID | Historia | Pts |
|----|----------|:---:|
| HU-46 | Como **administrador** quiero generar un reporte PDF de cierre diario con totales, métodos de pago y detalle de facturas | 3 |
| HU-47 | Como **administrador** quiero generar un listado PDF de facturas por período con resumen de totales | 2 |
| HU-48 | Como **vendedor** quiero descargar una factura en PDF desde su detalle para entregarla al cliente | 2 |

**Total Sprint: 7 pts**

---

## Resumen de User Stories

| Sprint | Lab | Total HU | Total Pts |
|--------|-----|:---------:|:---------:|
| 1 | Lab 01 | 4 | 6 |
| 2 | Lab 02 | 4 | 9 |
| 3 | Lab 03 | 2 | 5 |
| 4 | Lab 03b | 4 | 9 |
| 5 | Lab 04 | 4 | 11 |
| 6 | Lab 05 | 3 | 11 |
| 7 | Lab 06 | 4 | 13 |
| 8 | Lab 07 | 4 | 12 |
| 9 | Lab 08 | 4 | 8 |
| 10 | Lab 09 | 6 | 21 |
| 11 | Lab 10 | 4 | 9 |
| 12 | Lab 11 | 3 | 6 |
| 13 | Lab 12 | 3 | 7 |
| | **Total** | **49** | **127** |

---

## Principios de diseño en cada capa

### Frontend (Bootstrap 5 + Vanilla JS ES6)

```
HTML templates/    → Solo estructura y carga de assets
       │
CSS static/*.css   → Diseño visual (Bootstrap 5 + personalizado)
       │
JS static/*.js     → SOLID aplicado:
                     ├── api-client.js   (SRP: HTTP)
                     ├── auth-service.js (SRP: Auth)
                     ├── login.js        (SRP: DOM Controller)
                     └── [module].js     (SRP: CRUD Controller)
```

### Backend (Django CBVs + DRY)

```
Models/     → BaseModel, SoftDelete, F() atómico
Views/      → ListView, CreateView, UpdateView, DeleteView + Mixins
Services/   → Lógica de negocio separada (transaccional)
URLs/       → app_name + name para reverse
Templates/  → Herencia: base_admin.html → module_list.html
```

### Scrum / Jira

Cada HU se registra en Jira con:
- **Resumen:** `HU-NN - Como [rol] quiero [acción]`
- **Descripción:** Criterios de aceptación
- **Story Points:** 1-5
- **Sprint:** Asignado al laboratorio correspondiente
- **Estado:** To Do → In Progress → Done
