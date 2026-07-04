# Guía de Laboratorio 11 — Verificación Final + Despliegue

## Objetivo

Ejecutar las pruebas de aceptación final, documentar los pasos de despliegue y cerrar el proyecto con el checklist completo.

## Duración estimada

1 hora (presencial) + 1 hora (trabajo autónomo)

## Prerrequisitos

- Labs 01 al 10 completados y funcionando
- Servidor corriendo con datos de prueba

## User Stories

| ID | Historia | Pts |
|----|----------|:---:|
| HU-43 | Como **analista** quiero ejecutar pruebas de aceptación para verificar todas las funcionalidades | 3 |
| HU-44 | Como **desarrollador** quiero documentar pasos de despliegue en producción | 2 |
| HU-45 | Como **product owner** quiero revisar el sprint final con checklist completo | 1 |

---

## Fase 1 — Checklist de Verificación General

Marca cada criterio como ✅ (cumple) o ❌ (no cumple). Todos deben estar en ✅ para cerrar el proyecto.

### Módulo de Seguridad

| # | Criterio | Estado |
|---|----------|--------|
| 1 | Login profesional con split-screen (Lab 03b) | ☐ |
| 2 | Accesibilidad: ARIA labels, focus-visible, roles | ☐ |
| 3 | JavaScript SOLID con 3 clases separadas | ☐ |
| 4 | Sidebar con módulos y submódulos (Lab 05) | ☐ |
| 5 | Sidebar filtra por permisos del usuario | ☐ |
| 6 | Sidebar responsive (oculto en mobile con overlay) | ☐ |
| 7 | Búsqueda en el sidebar filtra en tiempo real | ☐ |
| 8 | CRUD Usuarios completo con búsqueda y paginación | ☐ |
| 9 | CRUD Roles con asignación de permisos | ☐ |
| 10 | Perfil de usuario con cambio de contraseña | ☐ |
| 11 | No puedes desactivarte a ti mismo | ☐ |

### Módulo de Catálogo

| # | Criterio | Estado |
|---|----------|--------|
| 12 | CRUD Categorías con soft delete | ☐ |
| 13 | CRUD Productos con imagen, precio, stock | ☐ |
| 14 | Búsqueda de productos por nombre y categoría | ☐ |
| 15 | Filtro por categoría en listado de productos | ☐ |
| 16 | Badge de stock: rojo (0), amarillo (<mínimo), verde | ☐ |
| 17 | No se puede desactivar categoría con productos activos | ☐ |

### Módulo de Clientes

| # | Criterio | Estado |
|---|----------|--------|
| 18 | CRUD Clientes con búsqueda por cédula/nombre | ☐ |
| 19 | Validación de cédula única | ☐ |
| 20 | Validación de email único | ☐ |
| 21 | Soft delete de clientes funcional | ☐ |

### Módulo de Facturación

| # | Criterio | Estado |
|---|----------|--------|
| 22 | Formulario maestro-detalle con buscador de productos | ☐ |
| 23 | Tabla de detalles editable en vivo (cantidad, descuento) | ☐ |
| 24 | Totales se actualizan automáticamente | ☐ |
| 25 | Stock se descuenta al crear factura (F() atómico) | ☐ |
| 26 | Stock insuficiente muestra error y no guarda | ☐ |
| 27 | Número secuencial FAC-XXXXXX generado automáticamente | ☐ |
| 28 | Cálculo correcto de subtotal, IVA (15%), total | ☐ |
| 29 | Historial de facturas con filtros por fecha | ☐ |
| 30 | Detalle de factura con desglose completo | ☐ |
| 31 | Anular factura restaura stock y marca como anulada | ☐ |
| 32 | No se puede anular una factura ya anulada | ☐ |

### Dashboard

| # | Criterio | Estado |
|---|----------|--------|
| 33 | 4 tarjetas de resumen con datos reales | ☐ |
| 34 | Gráfico de ventas (Chart.js) últimos 7 días | ☐ |
| 35 | Lista de últimas 5 facturas con enlaces | ☐ |
| 36 | Accesos directos a módulos principales | ☐ |

### Módulo de Reportes (Lab 12)

| # | Criterio | Estado |
|---|----------|--------|
| 37 | Página de reportes en `/invoicing/reports/` | ☐ |
| 38 | Cierre diario PDF genera documento con header, tarjetas, tabla y totales | ☐ |
| 39 | Listado PDF filtra por período desde/hasta | ☐ |
| 40 | Botón "Descargar PDF" en detalle de factura | ☐ |
| 41 | Tablas PDF con bordes, cabecera oscura y filas alternadas | ☐ |

---

## Fase 2 — Pruebas de Humo (Smoke Tests)

Ejecuta estas pruebas manuales en orden:

```bash
# 1. Iniciar servidor
python manage.py runserver

# 2. Verificar login
# Abrir http://localhost:8000/ → debe redirigir a login
# Ingresar credenciales correctas → debe entrar al dashboard

# 3. Verificar menú
# El sidebar debe mostrar todos los módulos con iconos
# Hacer clic en cada módulo para expandir/contraer

# 4. CRUD Categorías
# Crear, editar, listar, desactivar una categoría

# 5. CRUD Productos
# Crear producto con imagen, verificar stock

# 6. CRUD Clientes
# Crear cliente, buscar por cédula

# 7. Crear Factura
# Seleccionar cliente, agregar 2+ productos, guardar
# Verificar que el stock se descontó

# 8. Ver factura
# Ir al detalle, verificar cálculos

# 9. Anular factura
# Anular, verificar que stock se restauró

# 10. Dashboard
# Verificar tarjetas, gráfico, últimas facturas

# 11. Reportes PDF
# Ir a /invoicing/reports/, generar cierre diario y listado PDF
# Verificar que los PDFs se descargan con formato profesional
```

---

## Fase 3 — Documentación de Despliegue

### Requisitos de Producción

- Python 3.12
- MySQL 8 / MariaDB 10
- Git
- Servidor WSGI: Gunicorn (Linux) o Waitress (Windows)

### Pasos de Despliegue

```bash
# 1. Clonar repositorio
git clone <repo-url>
cd POO-4TO-CURSO-DJANGO-POSTGRES-REACT

# 2. Crear entorno virtual
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con valores de producción:
# DJANGO_DEBUG=False
# DJANGO_SECRET_KEY=<generar clave segura>
# DB_* configurar base de datos real

# 5. Migrar y recolectar estáticos
python manage.py migrate
python manage.py collectstatic --noinput

# 6. Crear superusuario
python manage.py createsuperuser

# 7. Iniciar con servidor WSGI
# Opción 1: Gunicorn (Linux)
# gunicorn config.wsgi:application --bind 0.0.0.0:8000

# Opción 2: Waitress (Windows)
# waitress-serve --port=8000 config.wsgi:application
```

### Configuración de Seguridad para Producción

```python
# En .env
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=tu-clave-secreta-aqui-12345
DJANGO_ALLOWED_HOSTS= tudominio.com,www.tudominio.com

# Configurar HTTPS si hay proxy (nginx, apache)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

---

## Fase 4 — Resumen del Proyecto

```
┌────────────────────────────────────────────────────────────────┐
│              SISTEMA DE FACTURACIÓN — RESUMEN                   │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Apps:                                                         │
│    core/        → BaseModel, MenuItem, SoftDelete              │
│    security/    → User, Login, Roles, Perfiles                 │
│    catalog/     → Categorías, Productos                        │
│    customers/   → Clientes                                     │
│    invoicing/   → Facturación ACID                             │
│                                                                │
│  Modelos: 8 (Categoria, Producto, Cliente, Factura,            │
│            DetalleFactura, User, MenuItem, Group)              │
│                                                                │
│  Vistas: 25+ CBVs con PermissionRequiredMixin                  │
│                                                                │
│  Templates: 15+ con Bootstrap 5 + diseño profesional           │
│                                                                │
│  JavaScript: Clases SOLID separadas por responsabilidad        │
│    - ApiClient (HTTP)                                          │
│    - AuthService (login/logout)                                │
│    - AdminLayout (sidebar)                                     │
│    - InvoiceCalculator (cálculos)                              │
│    - InvoiceService (facturación)                              │
│    - InvoiceForm (controlador DOM)                            │
│                                                                │
│  Principios aplicados:                                         │
│    POO: Abstracción, encapsulación, herencia, polimorfismo     │
│    SOLID: SRP, OCP, LSP, ISP, DIP                             │
│    DRY: BaseModel, mixins, templates reutilizables             │
│    ACID: Transacciones atómicas con F()                        │
│    Scrum: 46 User Stories en 12 sprints (120 pts total)        │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Fase 5 — Cierre

```bash
# Verificación final
python manage.py check
python manage.py showmigrations  # Todos deben tener [X]
```

| Lab | Estado |
|-----|--------|
| Lab 01 — Config Django + MySQL | 📄 |
| Lab 02 — App Security | 📄 |
| Lab 03 — Diagramas UML | 📄 |
| Lab 03b — Login Profesional | 📄 |
| Lab 04 — App Core (BaseModel, MenuItem) | 📄 |
| Lab 05 — Panel Administrativo | 📄 |
| Lab 06 — CRUD Usuarios + Roles | 📄 |
| Lab 07 — CRUD Catálogo | 📄 |
| Lab 08 — CRUD Clientes | 📄 |
| Lab 09 — Facturación ACID | 📄 |
| Lab 10 — Dashboard + Chart.js | 📄 |
| Lab 11 — Verificación Final | 📄 |
| Lab 12 — Reportes Profesionales PDF | 📄 |

➡️ **Siguiente:** [Lab 12 — Reportes Profesionales PDF](./guia-laboratorio-12.md)

**¡Proyecto listo para comenzar!**
