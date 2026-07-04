# User Stories — Sistema de Facturación

Formato para importar a Jira:

```
Resumen: HU-NN - Como [rol] quiero [acción] para [beneficio]
Historia: Como [rol] quiero [acción] para [beneficio]
Criterios de Aceptación:
  - Dado [contexto] cuando [acción] entonces [resultado]
Story Points: N
Sprint: N
Prioridad: Alta/Media/Baja
```

---

## Sprint 1 — Lab 01: Configuración Base

### HU-01 — Entorno Virtual Python

- **Historia:** Como **desarrollador** quiero configurar el entorno virtual con Python 3.12 para aislar dependencias del proyecto
- **Pts:** 1
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  1. Dado un sistema Windows 10/11, cuando ejecuto `python -m venv .venv`, entonces se crea la carpeta `.venv/` con Python 3.12
  2. Dado el entorno virtual creado, cuando ejecuto `.venv\Scripts\activate`, entonces el prompt cambia mostrando `(.venv)`
  3. Dado el entorno activado, cuando ejecuto `python --version`, entonces muestra `Python 3.12.x`

### HU-02 — Django + MySQL

- **Historia:** Como **desarrollador** quiero instalar Django 6.0.6 y conectar MySQL para tener la base de datos operativa
- **Pts:** 2
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  1. Dado el entorno activado, cuando ejecuto `pip install Django==6.0.6 mysqlclient python-decouple`, entonces se instalan sin errores
  2. Dado Django instalado, cuando ejecuto `django-admin startproject config .`, entonces se crea la carpeta `config/` con settings.py, urls.py
  3. Dado MySQL corriendo, cuando ejecuto `python manage.py migrate`, entonces las tablas de Django se crean en `ventas_db_local`
  4. Dado el servidor iniciado, cuando accedo a `http://localhost:8000/`, entonces veo la página de bienvenida de Django

### HU-03 — Configuración Limpia

- **Historia:** Como **desarrollador** quiero organizar settings.py con variables de entorno para mantener una configuración limpia y segura
- **Pts:** 2
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  1. Dado el archivo `.env` creado, cuando Django lee `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, entonces los aplica correctamente
  2. Dado `.env` con DB_ENGINE=mysql, cuando ejecuto migrate, entonces usa MySQL como base de datos
  3. Dado `.env` con `DJANGO_DEBUG=False`, cuando el servidor encuentra un error, entonces no muestra el traceback

### HU-04 — Variables de Entorno

- **Historia:** Como **desarrollador** quiero usar `python-decouple` para no exponer credenciales en el código fuente
- **Pts:** 1
- **Prioridad:** Media
- **Criterios de Aceptación:**
  1. Dado el archivo `.env` en `.gitignore`, cuando hago `git status`, entonces `.env` no aparece como archivo modificado
  2. Dado `.env.example` con valores placeholder, cuando un nuevo desarrollador lo copia a `.env` y ajusta valores, entonces el sistema funciona

---

## Sprint 2 — Lab 02: App Security

### HU-05 — Modelo User Personalizado

- **Historia:** Como **desarrollador** quiero crear un modelo User personalizado con email como USERNAME_FIELD para autenticar por correo electrónico
- **Pts:** 3
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  1. Dado el modelo User en `security/models.py`, cuando hereda de `AbstractBaseUser` y `PermissionsMixin`, entonces tiene los campos: email (único), username, first_name, last_name, is_active, is_staff, date_joined, foto
  2. Dado `USERNAME_FIELD = "email"`, cuando intento autenticar, entonces uso email y contraseña (no username)
  3. Dado `REQUIRED_FIELDS`, cuando creo un superusuario con `createsuperuser`, entonces pide username, first_name, last_name
  4. Dado `AUTH_USER_MODEL = "security.User"` en settings.py, cuando ejecuto `makemigrations` y `migrate`, entonces se crea la tabla `security_user`
  5. Dado el CustomUserManager, cuando creo un usuario con `create_user()`, entonces se guarda correctamente con email normalizado

### HU-06 — Inicio de Sesión

- **Historia:** Como **usuario** quiero iniciar sesión con email y contraseña desde una página de login para acceder al sistema protegido
- **Pts:** 3
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  1. Dado un usuario registrado, cuando accedo a `/security/login/`, entonces veo un formulario con campos email y contraseña
  2. Dado credenciales correctas, cuando envío el formulario, entonces el sistema me autentica y redirige a `/`
  3. Dado credenciales incorrectas, cuando envío el formulario, entonces veo un mensaje de error "Credenciales incorrectas"
  4. Dado un usuario no autenticado, cuando intento acceder a `/` directamente, entonces soy redirigido a `/security/login/`

### HU-07 — Panel Admin

- **Historia:** Como **administrador** quiero gestionar usuarios desde el panel Django admin para crear, editar y desactivar usuarios
- **Pts:** 2
- **Prioridad:** Media
- **Criterios de Aceptación:**
  1. Dado el admin registrado, cuando accedo a `/admin/`, entonces veo "Usuarios" en la sección "Security"
  2. Dado que hago clic en "Usuarios", entonces veo una tabla con columnas: email, username, first_name, last_name, is_staff, is_active
  3. Dado que hago clic en "Añadir Usuario", entonces puedo crear un nuevo usuario con email, username, nombres, apellidos, contraseña
  4. Dado un usuario seleccionado, cuando lo edito, entonces puedo cambiar su estado activo, staff y superusuario

### HU-08 — Barra de Navegación

- **Historia:** Como **usuario** quiero ver mi nombre en la barra de navegación después de iniciar sesión para confirmar que estoy autenticado
- **Pts:** 1
- **Prioridad:** Media
- **Criterios de Aceptación:**
  1. Dado que estoy autenticado, cuando veo la página de inicio, entonces la barra superior muestra mi nombre completo
  2. Dado que estoy autenticado, cuando hago clic en "Salir", entonces cierro sesión y soy redirigido al login
  3. Dado que NO estoy autenticado, cuando veo la página de login, entonces la barra de navegación no se muestra

---

## Sprint 3 — Lab 03: Diagramas UML

### HU-09 — Diagramas UML

- **Historia:** Como **arquitecto** quiero crear diagramas UML de clases, secuencia y entidad-relación para documentar el diseño del sistema de facturación
- **Pts:** 3
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  1. Dado el análisis del caso de estudio, cuando creo el diagrama de clases, entonces incluye Categoria, Producto, Cliente, Factura, DetalleFactura con sus relaciones
  2. Dado el flujo de creación de factura, cuando creo el diagrama de secuencia, entonces muestra la interacción entre los objetos con transacciones atómicas
  3. Dado el modelo de datos, cuando creo el diagrama ER, entonces muestra las 5 tablas con PKs, FKs, constraints y tipos de datos
   4. Dado un diagrama de despliegue, cuando lo creo, entonces muestra la arquitectura cliente/servidor con Django + MySQL + Bootstrap 5

### HU-10 — Verificación UML

- **Historia:** Como **analista** quiero verificar que los diagramas UML reflejan correctamente el diseño del sistema
- **Pts:** 2
- **Prioridad:** Media
- **Criterios de Aceptación:**
  1. Dado el diagrama de clases, cuando lo reviso, entonces cada clase tiene al menos 3 atributos y 1 método
  2. Dado el diagrama de secuencia, cuando lo reviso, entonces sigue el flujo correcto: crear factura → validar stock → descontar → calcular IVA → guardar
  3. Dado el diagrama ER, cuando lo reviso, entonces Factura y DetalleFactura tienen relación 1:N con FK

---

## Sprint 4 — Lab 03b: Login Profesional

### HU-11 — Diseño Split-Screen

- **Historia:** Como **usuario** quiero una pantalla de login con diseño profesional dividido en dos columnas (formulario a la derecha, branding a la izquierda) para tener una experiencia de inicio agradable
- **Pts:** 3
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  1. Dado un monitor de escritorio (≥992px), cuando accedo a `/security/login/`, entonces veo dos columnas: branding (gradiente azul, icono, features) a la izquierda y formulario a la derecha
  2. Dado un dispositivo móvil (<992px), cuando accedo al login, entonces veo solo el formulario ocupando el 100% del ancho (el branding se oculta)
  3. Dado el branding, cuando lo veo, entonces tiene un gradiente azul (#4e73df → #224abe) con animación suave de fondo
  4. Dado el formulario, cuando lo veo, entonces tiene un icono de factura en un círculo con gradiente, título "Sistema de Facturación" y campo email/contraseña

### HU-12 — Accesibilidad

- **Historia:** Como **usuario** quiero que el login sea accesible (navegación por teclado, ARIA, validación visible) para poder usarlo sin dificultad
- **Pts:** 2
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  1. Dado el formulario, cuando uso Tab para navegar, entonces el foco se mueve secuencialmente: email → contraseña → checkbox → botón, con un outline azul visible
  2. Dado el formulario con `aria-label`, cuando un lector de pantalla lo procesa, entonces anuncia "Formulario de inicio de sesión"
  3. Dado un error de validación, cuando aparece, entonces el mensaje tiene `role="alert"` y es anunciado inmediatamente
  4. Dado el botón de toggle contraseña, cuando hago clic, entonces la contraseña se muestra/oculta y el icono cambia de ojo abierto a cerrado

### HU-13 — JavaScript SOLID

- **Historia:** Como **desarrollador** quiero separar el JavaScript en 3 clases con responsabilidades únicas (ApiClient, AuthService, LoginController) para aplicar el principio de responsabilidad única (SRP)
- **Pts:** 3
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  1. Dado `api-client.js`, cuando reviso la clase ApiClient, entonces solo gestiona comunicación HTTP (Axios, CSRF, interceptors)
  2. Dado `auth-service.js`, cuando reviso la clase AuthService, entonces solo contiene los métodos `login()` y `logout()`
  3. Dado `login.js`, cuando reviso el código, entonces orquesta la interacción DOM + AuthService sin mezclar lógica HTTP
  4. Dado que AuthService recibe ApiClient por constructor, cuando quiero probar, entonces puedo inyectar un mock
  5. Dado el login.html, cuando lo reviso, entonces NO contiene JavaScript inline (todo está en archivos separados)

### HU-14 — Axios

- **Historia:** Como **desarrollador** quiero usar Axios para las peticiones POST del login para tener manejo de errores centralizado
- **Pts:** 1
- **Prioridad:** Media
- **Criterios de Aceptación:**
  1. Dado el login, cuando envío credenciales, entonces Axios envía POST a `/security/login/` con header `X-CSRFToken`
  2. Dado un error de red, cuando ocurre, entonces el interceptor captura el error y muestra "Error de conexión con el servidor"
  3. Dado un error HTTP 400, cuando el servidor responde, entonces el interceptor extrae `error.response.data.error` y lo muestra al usuario

---

## Sprint 5 — Lab 04: App Core ✅ Completado

### HU-15 — BaseModel

- **Historia:** Como **desarrollador** quiero un BaseModel abstracto con created_at, updated_at, is_active y deleted_at para que todos los modelos del sistema hereden auditoría
- **Pts:** 2
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  1. Dado BaseModel en `core/models.py`, cuando creo un modelo que hereda de él, entonces tiene automáticamente los campos `created_at`, `updated_at`, `deleted_at`, `is_active`
  2. Dado `Meta.abstract = True`, cuando ejecuto `makemigrations`, entonces Django no crea una tabla para `BaseModel`
  3. Dado un registro creado, cuando reviso `created_at`, entonces tiene la fecha/hora de creación
  4. Dado un registro modificado, cuando reviso `updated_at`, entonces se actualiza automáticamente

### HU-16 — SoftDelete

- **Historia:** Como **desarrollador** quiero implementar SoftDelete para poder restaurar registros eliminados accidentalmente
- **Pts:** 2
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  1. Dado `SoftDeleteManager`, cuando uso `Model.objects.all()`, entonces solo retorna registros con `is_active=True`
  2. Dado `Model.all_objects`, cuando lo uso, entonces retorna TODOS los registros (activos e inactivos)
  3. Dado un registro activo, cuando llamo `.soft_delete()`, entonces `is_active=False` y `deleted_at` tiene la fecha actual
  4. Dado un registro eliminado, cuando llamo `.restore()`, entonces `is_active=True` y `deleted_at=None`

### HU-17 — MenuItem Jerárquico

- **Historia:** Como **administrador** quiero un modelo de menú jerárquico con permisos para controlar la navegación del sistema según el rol del usuario
- **Pts:** 5
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  1. Dado `MenuItem` con `parent` FK a sí mismo, cuando `parent=None`, entonces es un módulo raíz (visible en el sidebar)
  2. Dado `MenuItem` con `parent` asignado, cuando existe, entonces es un submódulo hijo de ese módulo
  3. Dado `has_access(user)`, cuando el usuario no tiene los permisos requeridos, entonces retorna `False`
  4. Dado `has_access(user)`, cuando el usuario SÍ tiene los permisos (directamente o por grupo), entonces retorna `True`
  5. Dado un módulo sin hijos accesibles, cuando se evalúa `has_access(user)`, entonces retorna `False` (el módulo se oculta)

### HU-18 — Seed Data

- **Historia:** Como **desarrollador** quiero una migración de datos con la estructura inicial del menú para tener el sistema preconfigurado
- **Pts:** 2
- **Prioridad:** Media
- **Criterios de Aceptación:**
  1. Dada la migración seed, cuando ejecuto `migrate`, entonces se crean 5 módulos: Dashboard, Seguridad, Catálogo, Clientes, Ventas
  2. Dada la migración seed, cuando se completa, entonces existen 7 submódulos distribuidos entre los módulos
  3. Dado Dashboard, cuando se crea, entonces tiene `url_name='home'` y funciona como enlace directo
  4. Dada la migración reversa, cuando ejecuto `migrate core 0001`, entonces todos los datos semilla se eliminan

---

## Sprint 6 — Lab 05: Panel Administrativo

### HU-19 — Sidebar de Navegación

- **Historia:** Como **usuario** quiero un panel administrativo con sidebar izquierdo que muestre los módulos del sistema para navegar entre las diferentes secciones
- **Pts:** 5
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  1. Dado que estoy autenticado, cuando accedo a cualquier página del sistema, entonces veo un sidebar fijo a la izquierda (250px) con el logo del sistema en la parte superior
  2. Dado el sidebar, cuando hay módulos disponibles, entonces se muestran como elementos verticales con icono y nombre (ej: 🔐 Seguridad, 📦 Catálogo)
  3. Dado un módulo con submódulos, cuando hago clic en él, entonces se expande/contrae mostrando los submódulos hijos
  4. Dado un módulo sin submódulos (Dashboard), cuando hago clic en él, entonces navego directamente a su URL
  5. Dado el sidebar, cuando el usuario NO tiene permiso para ver un módulo/submódulo, entonces NO se muestra en el menú
  6. Dado un dispositivo móvil (<768px), cuando veo el panel, entonces el sidebar está oculto y un botón hamburguesa lo muestra como overlay

### HU-20 — Panel Principal con Accordion

- **Historia:** Como **usuario** quiero que el panel principal muestre los módulos en accordion con acceso directo a submódulos para visualizar todo el sistema de un vistazo
- **Pts:** 3
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  1. Dado el panel principal, cuando accedo al dashboard, entonces veo tarjetas de módulos en formato accordion (Bootstrap)
  2. Dado un accordion de módulo, cuando hago clic en el encabezado, entonces se expande mostrando los submódulos con icono, nombre y enlace
  3. Dado un submódulo en el accordion, cuando hago clic en él, entonces navego a la URL correspondiente
  4. Dado el layout general, cuando lo veo, entonces tiene un header superior con el nombre del usuario y botón de cerrar sesión

### HU-21 — Filtro por Permisos

- **Historia:** Como **usuario** quiero que el menú solo muestre los módulos/submódulos que tengo permiso de ver para no ver opciones no autorizadas
- **Pts:** 3
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  1. Dado un usuario sin permisos de seguridad, cuando veo el sidebar, entonces el módulo "Seguridad" no aparece
  2. Dado un usuario con permiso `auth.view_group`, cuando veo el módulo "Seguridad", entonces solo veo el submódulo "Roles" (no "Usuarios" si no tiene ese permiso)
  3. Dado un usuario administrador (is_superuser), cuando veo el menú, entonces TODOS los módulos y submódulos son visibles

---

## Sprint 7 — Lab 06: Usuarios y Roles

### HU-22 — CRUD Usuarios

- **Historia:** Como **administrador** quiero listar, crear, editar y desactivar usuarios desde una interfaz propia (no solo admin de Django) para gestionar el acceso al sistema
- **Pts:** 5
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  1. Dado `/security/users/`, cuando accedo, entonces veo una tabla con todos los usuarios: email, nombre, rol, estado, última conexión
  2. Dada la tabla de usuarios, cuando escribo en el campo de búsqueda, entonces filtra por nombre o email
  3. Dado que hago clic en "Nuevo Usuario", cuando completo el formulario, entonces se crea el usuario y veo mensaje de éxito
  4. Dado que hago clic en "Editar" en un usuario, cuando modifico sus datos, entonces se actualizan correctamente
  5. Dado que hago clic en "Desactivar" en un usuario activo, cuando confirmo, entonces el usuario se desactiva (is_active=False)
  6. Dado el formulario de usuario, cuando no completo campos requeridos, entonces veo mensajes de validación

### HU-23 — Roles y Permisos

- **Historia:** Como **administrador** quiero crear roles con permisos específicos usando Django Groups para controlar qué puede hacer cada perfil
- **Pts:** 3
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  1. Dado `/security/roles/`, cuando accedo, entonces veo una lista de roles (groups) con nombre, cantidad de usuarios y permisos
  2. Dado que hago clic en "Nuevo Rol", cuando ingreso el nombre y selecciono permisos de una lista, entonces el rol se crea
  3. Dado un rol existente, cuando lo edito, entonces puedo agregar o quitar permisos
  4. Dado que elimino un rol, cuando confirmo, entonces el rol se elimina pero los usuarios no se afectan

### HU-24 — Asignar Usuarios a Roles

- **Historia:** Como **administrador** quiero asignar usuarios a roles para otorgarles permisos de forma masiva
- **Pts:** 2
- **Prioridad:** Media
- **Criterios de Aceptación:**
  1. Dado un rol, cuando veo su detalle, entonces puedo agregar/quitar usuarios del grupo
  2. Dado un usuario en la lista, cuando lo selecciono y asigno a un rol, entonces hereda todos los permisos del rol
  3. Dado un usuario con múltiples roles, cuando tiene permisos de todos los roles combinados, entonces `user.has_perm()` retorna True si al menos un rol tiene el permiso

### HU-25 — Perfil de Usuario

- **Historia:** Como **usuario** quiero ver y editar mi perfil (nombre, email, contraseña, foto) para mantener mis datos actualizados
- **Pts:** 3
- **Prioridad:** Media
- **Criterios de Aceptación:**
  1. Dado `/security/profile/`, cuando accedo, entonces veo mis datos: nombres, email, fecha de registro, última conexión
  2. Dado el formulario de perfil, cuando cambio mi nombre, entonces se actualiza en la base de datos
  3. Dado el formulario de cambio de contraseña, cuando ingreso la actual y la nueva dos veces, entonces la contraseña se actualiza
  4. Dado el campo de foto, cuando selecciono una imagen, entonces se sube y se muestra en el perfil

---

## Sprint 8 — Lab 07: Catálogo

### HU-26 — CRUD Categorías

- **Historia:** Como **administrador** quiero gestionar categorías (crear, editar, listar, desactivar) para clasificar los productos del sistema
- **Pts:** 3
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  1. Dado `/catalog/categories/`, cuando accedo, entonces veo una tabla con nombre, descripción, cantidad de productos, estado
  2. Dado que hago clic en "Nueva Categoría", cuando ingreso nombre y descripción, entonces la categoría se crea
  3. Dado una categoría existente, cuando la edito, entonces puedo cambiar nombre y descripción
  4. Dado que desactivo una categoría, cuando lo hago, entonces sus productos no se eliminan pero la categoría no aparece en selectores

### HU-27 — CRUD Productos

- **Historia:** Como **administrador** quiero gestionar productos con nombre, precio, stock, categoría y foto para mantener el inventario actualizado
- **Pts:** 5
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  1. Dado `/catalog/products/`, cuando accedo, entonces veo una tabla con imagen, nombre, precio, stock, categoría, estado
  2. Dado que hago clic en "Nuevo Producto", cuando completo el formulario (nombre, precio>0, stock≥0, categoría, foto opcional), entonces el producto se crea
  3. Dado que edito un producto, cuando cambio el precio o stock, entonces se actualiza en la base de datos
  4. Dado que intento crear un producto sin nombre o con precio negativo, entonces veo mensajes de validación
  5. Dado la lista de productos, cuando uso el buscador, entonces filtra por nombre o categoría

### HU-28 — Búsqueda de Productos

- **Historia:** Como **vendedor** quiero buscar productos por nombre o categoría para encontrar rápidamente lo que necesito
- **Pts:** 3
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  1. Dado la lista de productos, cuando escribo en el buscador, entonces los resultados se filtran en tiempo real (AJAX)
  2. Dado el filtro por categoría, cuando selecciono una categoría del dropdown, entonces solo se muestran productos de esa categoría
  3. Dada la paginación, cuando hay más de 10 productos, entonces se muestran con paginador

### HU-29 — Vista de Stock

- **Historia:** Como **vendedor** quiero ver el stock disponible de cada producto en la lista para saber si puedo venderlo
- **Pts:** 1
- **Prioridad:** Media
- **Criterios de Aceptación:**
  1. Dado la lista de productos, cuando veo la columna "Stock", entonces muestra el número disponible
  2. Dado un producto con stock=0, cuando lo veo, entonces se muestra con badge rojo "Sin stock"
  3. Dado un producto con stock<5, cuando lo veo, entonces se muestra con badge amarillo "Stock bajo"

---

## Sprint 9 — Lab 08: Clientes

### HU-30 — Registro de Clientes

- **Historia:** Como **vendedor** quiero registrar clientes con nombre, cédula, email, teléfono y dirección para poder crear facturas a su nombre
- **Pts:** 3
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  1. Dado `/customers/`, cuando accedo, entonces veo una tabla con cédula, nombre, email, teléfono
  2. Dado que hago clic en "Nuevo Cliente", cuando ingreso cédula (10 dígitos), nombres, email, teléfono, dirección, entonces el cliente se crea
  3. Dado que intento registrar un cliente con cédula existente, entonces veo error "La cédula ya está registrada"
  4. Dado que intento registrar con email existente, entonces veo error "El email ya está registrado"

### HU-31 — Búsqueda de Clientes

- **Historia:** Como **vendedor** quiero buscar clientes por cédula o nombre para agilizar el proceso de facturación
- **Pts:** 2
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  1. Dado la lista de clientes, cuando escribo en el buscador, entonces filtra en tiempo real por cédula o nombre
  2. Dado que busco por cédula exacta, cuando encuentro el cliente, entonces puedo hacer clic para ver su detalle

### HU-32 — Editar/Desactivar Clientes

- **Historia:** Como **administrador** quiero editar y desactivar clientes para mantener la base de datos actualizada
- **Pts:** 2
- **Prioridad:** Media
- **Criterios de Aceptación:**
  1. Dado un cliente existente, cuando hago clic en "Editar", entonces puedo modificar todos sus datos excepto la fecha de registro
  2. Dado que desactivo un cliente, cuando lo busco por defecto, entonces no aparece en los resultados (soft delete)
  3. Dado un cliente desactivado, cuando busco incluyendo inactivos, entonces lo veo marcado como "Inactivo"

### HU-33 — Validación Única

- **Historia:** Como **vendedor** quiero que el sistema valide que el email y cédula sean únicos para evitar duplicados en la base de datos
- **Pts:** 1
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  1. Dado el formulario de cliente, cuando ingreso una cédula existente, entonces el sistema muestra error antes de guardar (validación AJAX)
  2. Dado el formulario de cliente, cuando ingreso un email existente, entonces el sistema muestra error antes de guardar

---

## Sprint 10 — Lab 09: Facturación

### HU-34 — Crear Factura

- **Historia:** Como **vendedor** quiero crear una factura seleccionando cliente, productos y cantidades para registrar una venta de forma rápida
- **Pts:** 5
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  1. Dado `/invoicing/invoices/create/`, cuando accedo, entonces veo un formulario con selector de cliente y tabla de detalles vacía
  2. Dado que selecciono un cliente, cuando elijo del buscador, entonces el ID del cliente se asigna a la factura
  3. Dado que agrego un producto a la factura, cuando selecciono producto y cantidad, entonces se agrega una fila a la tabla de detalles con: producto, cantidad, precio unitario, subtotal
  4. Dado que completo la factura, cuando hago clic en "Guardar", entonces la factura se crea con todos los detalles, el stock se descuenta y veo mensaje de éxito con el número de factura
  5. Dado que intento agregar un producto con cantidad > stock, entonces veo error "Stock insuficiente"

### HU-35 — Descuento Automático de Stock

- **Historia:** Como **vendedor** quiero que el stock de productos se descuente automáticamente al crear una factura para mantener el inventario consistente sin intervención manual
- **Pts:** 3
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  1. Dado una factura creada con 5 unidades del Producto A, cuando consulto el stock del Producto A, entonces se redujo en 5
  2. Dado que dos usuarios crean facturas simultáneamente del mismo producto, cuando el stock es suficiente para ambas, entonces ambas se completan sin condiciones de carrera
  3. Dado que el stock no es suficiente, cuando intento crear la factura, entonces la transacción completa se revierte (rollback)

### HU-36 — Cálculo Automático de IVA

- **Historia:** Como **vendedor** quiero que el IVA (15%) y los subtotales se calculen automáticamente en la factura para evitar errores manuales de cálculo
- **Pts:** 2
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  1. Dado un detalle de factura, cuando agrego un producto con precio 100 y cantidad 2, entonces el subtotal se calcula como 200
  2. Dado el total de la factura, cuando se calcula, entonces el subtotal = suma de subtotales, IVA = subtotal * 0.15, total = subtotal + IVA
  3. Dado la factura guardada, cuando la veo, entonces muestra: subtotal, IVA 15%, total, en formato moneda ($)

### HU-37 — Anular Factura

- **Historia:** Como **administrador** quiero anular una factura y restaurar el stock automáticamente para corregir errores en las ventas
- **Pts:** 5
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  1. Dado una factura existente, cuando hago clic en "Anular", entonces veo un modal de confirmación explicando que el stock se restaurará
  2. Dado que confirmo la anulación, entonces la factura se marca como anulada (is_active=False) y el stock de cada producto se incrementa en la cantidad vendida
  3. Dado que intento anular una factura ya anulada, entonces veo error "La factura ya está anulada"
  4. Dado que la anulación se completa, cuando veo el historial, entonces la factura aparece con badge "Anulada"

### HU-38 — Historial de Facturas

- **Historia:** Como **usuario** quiero ver el historial de facturas con filtros por fecha y cliente para consultar ventas anteriores
- **Pts:** 3
- **Prioridad:** Media
- **Criterios de Aceptación:**
  1. Dado `/invoicing/invoices/`, cuando accedo, entonces veo una tabla con: número, fecha, cliente, subtotal, IVA, total, estado
  2. Dado el filtro de fechas, cuando selecciono un rango, entonces solo se muestran facturas de ese período
  3. Dado el filtro por cliente, cuando selecciono un cliente, entonces solo se muestran sus facturas
  4. Dado que hago clic en una factura, cuando veo el detalle, entonces muestra todos los productos, cantidades, precios y totales

### HU-38b — Interfaz Profesional de Facturación

- **Historia:** Como **vendedor** quiero una interfaz profesional con buscador de productos, tabla de detalles editable en vivo y totales automáticos para facturar de manera rápida y eficiente
- **Pts:** 3
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  1. Dado el formulario de factura, cuando escribo en el buscador de productos, entonces se filtran en tiempo real mostrando código, nombre, stock y precio
  2. Dado que selecciono un producto del buscador, cuando hago clic, entonces se agrega a la tabla de detalles con cantidad=1 y subtotal calculado automáticamente
  3. Dado la tabla de detalles, cuando cambio la cantidad de un ítem, entonces el subtotal de línea, el descuento y los totales generales se actualizan en vivo (sin recargar la página)
  4. Dado la tabla de detalles, cuando hago clic en ✕ eliminar, entonces el ítem se quita y los totales se recalculan
  5. Dado que hay un ítem con cantidad > stock disponible, cuando lo veo, entonces la fila se marca en rojo y el botón Guardar se deshabilita con mensaje de advertencia
  6. Dado el formulario completo, cuando hago clic en "Guardar Factura", entonces se muestra un spinner de carga y al finalizar un toast de éxito con el número de factura generado

---

## Sprint 11 — Lab 10: Dashboard

### HU-39 — Tarjetas de Resumen

- **Historia:** Como **usuario** quiero ver un dashboard con tarjetas de resumen (facturas hoy, ventas del mes, total clientes, productos bajos en stock) para tener una visión general del negocio
- **Pts:** 3
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  1. Dado el dashboard, cuando accedo a `/`, entonces veo 4 tarjetas numéricas: Facturas Hoy, Ventas del Mes, Clientes Registrados, Productos con Stock Bajo
  2. Dado cada tarjeta, cuando la veo, entonces tiene un icono representativo, el valor numérico y una etiqueta descriptiva
  3. Dado que hay facturas hoy, cuando miro la tarjeta, entonces el número se actualiza automáticamente

### HU-40 — Gráfico de Ventas

- **Historia:** Como **administrador** quiero ver un gráfico de ventas por día/semana/mes para analizar tendencias del negocio
- **Pts:** 3
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  1. Dado el dashboard, cuando veo la sección de gráficos, entonces hay un gráfico de líneas/barras con ventas de los últimos 7 días
  2. Dado el gráfico, cuando paso el mouse sobre un punto, entonces veo un tooltip con la fecha y el valor exacto
  3. Dado que cambio el filtro a "Mes", entonces el gráfico se actualiza para mostrar ventas del mes actual

### HU-41 — Últimas Facturas

- **Historia:** Como **usuario** quiero ver las últimas 5 facturas creadas en el dashboard para tener acceso rápido a las transacciones recientes
- **Pts:** 2
- **Prioridad:** Media
- **Criterios de Aceptación:**
  1. Dado el dashboard, cuando veo la sección "Últimas Facturas", entonces hay una tabla con las 5 facturas más recientes
  2. Dado cada factura en la tabla, cuando hago clic en el número, entonces navego al detalle de la factura

### HU-42 — Accesos Directos

- **Historia:** Como **vendedor** quiero accesos directos a "Nueva Factura" y "Buscar Cliente" desde el dashboard para ser más eficiente en mi trabajo diario
- **Pts:** 1
- **Prioridad:** Media
- **Criterios de Aceptación:**
  1. Dado el dashboard, cuando veo la parte superior, entonces hay botones de acceso rápido: "Nueva Factura", "Buscar Cliente", "Catálogo"
  2. Dado que hago clic en "Nueva Factura", cuando el enlace funciona, entonces navego directamente al formulario de creación de factura

---

## Sprint 12 — Lab 11: Verificación Final

### HU-43 — Pruebas de Aceptación

- **Historia:** Como **analista** quiero ejecutar las pruebas de aceptación para verificar que todas las funcionalidades cumplen los requisitos definidos
- **Pts:** 3
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  1. Dado el checklist final, cuando ejecuto cada prueba, entonces cada criterio se marca como "Cumple" o "No Cumple"
  2. Dado que una prueba falla, cuando la identifico, entonces se registra como bug en Jira
  3. Dado que todas las pruebas pasan, cuando reviso el checklist, entonces el proyecto se da por finalizado

### HU-44 — Documentación de Despliegue

- **Historia:** Como **desarrollador** quiero documentar los pasos de despliegue para que el sistema pueda instalarse en cualquier entorno de producción
- **Pts:** 2
- **Prioridad:** Media
- **Criterios de Aceptación:**
  1. Dado el documento de despliegue, cuando lo leo, entonces contiene: requisitos del sistema, pasos de instalación, configuración de BD, variables de entorno
  2. Dado el documento, cuando sigo los pasos en un entorno limpio, entonces el sistema se instala y funciona correctamente

### HU-45 — Cierre del Proyecto

- **Historia:** Como **product owner** quiero revisar el sprint final con el checklist completo para dar por finalizado el proyecto
- **Pts:** 1
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  1. Dado el checklist completo, cuando reviso cada ítem, entonces todos están marcados como "Cumple"
  2. Dado el repositorio, cuando reviso la documentación, entonces existe README, ROADMAP, user-stories y guías de laboratorio

---

## Sprint 13 — Lab 12: Reportes PDF

### HU-46 — Cierre Diario PDF

- **Historia:** Como **administrador** quiero generar un reporte PDF de cierre diario con totales, métodos de pago y detalle de facturas
- **Pts:** 3
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  1. Dado `/invoicing/reports/daily-close/`, cuando accedo, entonces descargo un PDF con el cierre del día actual
  2. Dado el PDF de cierre, cuando lo abro, entonces veo: header corporativo, tarjetas de resumen (facturas, subtotal, IVA, total), tabla de métodos de pago con barras de distribución, detalle de cada factura, y totales
  3. Dado el PDF, cuando hay facturas anuladas, entonces se muestran con badge "ANULADA" en rojo

### HU-47 — Listado de Facturas PDF

- **Historia:** Como **administrador** quiero generar un listado PDF de facturas por período con resumen de totales
- **Pts:** 2
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  1. Dado `/invoicing/reports/invoice-list/?desde=...&hasta=...`, cuando accedo, entonces descargo un PDF con las facturas del período
  2. Dado el PDF de listado, cuando lo abro, entonces veo: header corporativo, tarjetas de resumen, tabla con todas las facturas del período, totales acumulados
  3. Dado el formulario en la página de reportes, cuando selecciono fechas, entonces el PDF se genera solo para ese rango

### HU-48 — Descargar Factura PDF

- **Historia:** Como **vendedor** quiero descargar una factura en PDF desde su detalle para entregarla al cliente
- **Pts:** 2
- **Prioridad:** Media
- **Criterios de Aceptación:**
  1. Dado el detalle de una factura, cuando veo la página, entonces hay un botón "Descargar PDF"
  2. Dado que hago clic en "Descargar PDF", entonces se descarga un archivo con formato profesional: logo, datos del cliente, detalle de productos, IVA, totales
  3. Dado el PDF descargado, cuando lo abro, entonces el nombre del archivo es `factura_FAC-XXXXXX.pdf`

---

## Resumen para Jira

| Sprint | HU IDs | Total Pts |
|--------|--------|:---------:|
| Lab 01 | HU-01 al HU-04 | 6 |
| Lab 02 | HU-05 al HU-08 | 9 |
| Lab 03 | HU-09 al HU-10 | 5 |
| Lab 03b | HU-11 al HU-14 | 9 |
| Lab 04 | HU-15 al HU-18 | 11 |
| Lab 05 | HU-19 al HU-21 | 11 |
| Lab 06 | HU-22 al HU-25 | 13 |
| Lab 07 | HU-26 al HU-29 | 12 |
| Lab 08 | HU-30 al HU-33 | 8 |
| Lab 09 | HU-34 al HU-38b | 21 |
| Lab 10 | HU-39 al HU-42 | 9 |
| Lab 11 | HU-43 al HU-45 | 6 |
| Lab 12 | HU-46 al HU-48 | 7 |
| | **Total** | **127** |
