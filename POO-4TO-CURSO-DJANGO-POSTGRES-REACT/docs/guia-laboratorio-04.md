# Guía de Laboratorio 04 — App Core: BaseModel + SoftDelete + Menú de Navegación con Permisos

## Objetivo

Crear la aplicación `core` que servirá como base para todo el sistema. Implementará:

1. **BaseModel** — Clase abstracta con auditoría (`created_at`, `updated_at`, `deleted_at`, `is_active`)
2. **SoftDeleteManager** — Manager que excluye automáticamente registros eliminados
3. **MenuItem** — Modelo único auto-referencial para el menú de navegación con permisos
4. **Seed data** — Migración de datos con la estructura inicial del menú
5. **Admin** — Registro del modelo en el panel de Django

## Duración estimada

2 horas (presencial) + 1 hora (trabajo autónomo)

## Prerrequisitos

- Laboratorio 03b completado (login profesional con Bootstrap 5 + Axios + SOLID)
- Python 3.12, Django 6.0.6, MySQL configurado y migrado
- Servidor Django funcionando (`python manage.py runserver`)

## Resultado al finalizar

- App `core` instalada y migrada
- `BaseModel` listo para que todos los modelos del sistema hereden de él
- `MenuItem` creado con 5 módulos y 7 submódulos en base de datos
- Admin funcional para gestionar menú y permisos desde el navegador
- Método `has_access(user)` implementado para filtrar visibilidad por permisos

---

## Estructura final del proyecto

```
backend/
├── core/
│   ├── __init__.py
│   ├── apps.py                   (NUEVO)
│   ├── models.py                 (NUEVO) — BaseModel, SoftDeleteManager, MenuItem
│   ├── admin.py                  (NUEVO) — MenuItemAdmin
│   └── migrations/
│       ├── __init__.py
│       ├── 0001_initial.py       (AUTO) — Creación tabla MenuItem
│       └── 0002_seed_menu.py     (AUTO) — Datos semilla del menú
├── config/
│   └── settings.py               (MODIFICADO) — + 'core' en INSTALLED_APPS
└── docs/
    └── uml/
        └── 04-clases-modulo-navegacion.puml  (NUEVO — diagrama de navegación y permisos)
```

---

## Fase 1 — Conceptos previos

### 1.1 ¿Qué es un BaseModel?

Un `BaseModel` es una clase abstracta de Django de la que heredarán **todos** los modelos del sistema. Contiene campos comunes de auditoría:

| Campo | Tipo | Propósito |
|-------|------|-----------|
| `created_at` | `DateTimeField(auto_now_add=True)` | Fecha de creación (solo lectura) |
| `updated_at` | `DateTimeField(auto_now=True)` | Fecha de última modificación |
| `deleted_at` | `DateTimeField(null=True)` | Fecha de eliminación (soft delete) |
| `is_active` | `BooleanField(default=True)` | Indicador de registro activo |

### 1.2 ¿Qué es SoftDelete?

**Soft delete** significa que cuando "eliminamos" un registro, en realidad no se borra de la base de datos. Solo se marca como `is_active=False` y se registra la fecha en `deleted_at`.

**Ventajas:**
- Los datos pueden restaurarse
- Se mantiene la integridad referencial
- Auditoría completa (saber qué se eliminó, cuándo y por quién)
- Los usuarios normales no ven datos eliminados

### 1.3 ¿Qué es un Manager en Django?

Un `Manager` es la clase que define cómo se recuperan los objetos de la base de datos. `Model.objects` es el manager por defecto. Podemos crear managers personalizados para cambiar el comportamiento:

```python
# Manager normal: devuelve todo
Producto.objects.all()  # → SELECT * FROM producto

# SoftDeleteManager: solo activos
Producto.objects.all()  # → SELECT * FROM producto WHERE is_active=True
```

### 1.4 ¿Qué es un modelo auto-referencial?

Es un modelo que tiene una clave foránea (`ForeignKey`) apuntando a sí mismo. Esto permite crear estructuras jerárquicas (árboles) con una sola tabla:

```
MenuItem
├── id: 1, name: "Seguridad", parent: null  ← Módulo raíz
│   ├── id: 2, name: "Usuarios", parent: 1  ← Submódulo
│   └── id: 3, name: "Roles",    parent: 1  ← Submódulo
└── id: 4, name: "Catálogo", parent: null   ← Módulo raíz
    ├── id: 5, name: "Categorías", parent: 4 ← Submódulo
    └── id: 6, name: "Productos",  parent: 4 ← Submódulo
```

**Ventajas frente a dos modelos separados (Module + Submodule):**

| Aspecto | Dos modelos | Auto-referencial |
|---------|-------------|------------------|
| Flexibilidad | Solo 2 niveles | N niveles |
| Código | 2 modelos, 2 admins | 1 modelo, 1 admin |
| Consultas | Joins entre tablas | Misma tabla, misma query |
| Escalabilidad | Nuevo nivel = nueva tabla | Solo agregar más padres |

---

## Fase 2 — Crear la app `core`

**Paso 2.1:** Abre una terminal en `backend/` y activa el entorno virtual:

```bash
cd backend
.venv\Scripts\activate      # Windows
source .venv/bin/activate    # Linux/Mac
```

**Paso 2.2:** Crea la aplicación `core`:

```bash
python manage.py startapp core
```

Esto crea la carpeta `core/` con los archivos básicos.

**Paso 2.3:** Verifica la estructura creada:

```bash
ls -R core/
```

Debes ver:
```
core/
├── __init__.py
├── admin.py
├── apps.py
├── migrations/
│   └── __init__.py
├── models.py
├── tests.py
└── views.py
```

---

## Fase 3 — Configurar `apps.py`

**Paso 3.1:** Abre `core/apps.py` y escribe:

```python
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Core'
```

**Paso 3.2:** Abre `config/settings.py` y agrega `'core'` en `LOCAL_APPS`, **antes** de `'security'`:

```python
LOCAL_APPS = [
    "core",
    "security",
]
```

> **Nota:** El orden importa. `core` va primero porque contiene el `BaseModel` del que otros modelos podrían depender.

---

## Fase 4 — Crear `BaseModel` y `SoftDeleteManager`

**Paso 4.1:** Abre `core/models.py` y escribe TODO el contenido:

```python
from django.contrib.auth.models import Permission
from django.db import models
from django.utils import timezone


class SoftDeleteManager(models.Manager):
    """Manager que excluye automáticamente registros con is_active=False."""
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class BaseModel(models.Model):
    """Clase abstracta base con campos de auditoría y soft delete."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def soft_delete(self):
        """Marca el registro como eliminado (sin borrarlo físicamente)."""
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_active', 'deleted_at', 'updated_at'])

    def restore(self):
        """Restaura un registro eliminado."""
        self.is_active = True
        self.deleted_at = None
        self.save(update_fields=['is_active', 'deleted_at', 'updated_at'])
```

**Explicación:**

| Elemento | ¿Qué hace? |
|----------|------------|
| `SoftDeleteManager` | Sobrescribe `get_queryset()` para filtrar solo `is_active=True` |
| `BaseModel.objects` | Usa `SoftDeleteManager` → por defecto solo ves activos |
| `BaseModel.all_objects` | Usa `models.Manager()` → ves TODOS (activos e inactivos) |
| `soft_delete()` | Marca como inactivo y registra la fecha |
| `restore()` | Reactiva y limpia la fecha de eliminación |
| `abstract = True` | Django NO crea una tabla para `BaseModel`. Solo es para heredar |
| `update_fields` | Optimización: solo actualiza los campos modificados |

---

## Fase 5 — Crear el modelo `MenuItem`

El modelo `MenuItem` representa tanto módulos como submódulos del menú de navegación, usando una **clave foránea a sí mismo** (`parent`) para crear la jerarquía.

**Paso 5.1:** Al final del archivo `core/models.py` (después de `BaseModel`), agrega:

```python
class MenuItem(BaseModel):
    """Elemento de navegación del sistema. Módulo (parent=None) o submódulo."""
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='children',
        verbose_name='Módulo padre',
        help_text='Null = módulo raíz en el sidebar',
    )
    name = models.CharField('Nombre', max_length=100)
    icon = models.CharField(
        'Icono', max_length=50, blank=True,
        help_text='Clase Bootstrap Icon (ej: bi-shield-lock)',
    )
    url_name = models.CharField(
        'URL interna', max_length=200, blank=True,
        help_text='Nombre de ruta Django (ej: security:user_list)',
    )
    order = models.PositiveIntegerField('Orden', default=0)
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        verbose_name='Permisos requeridos',
        help_text='Visible solo para usuarios con estos permisos. Vacío = visible para todos.',
    )

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Elemento de menú'
        verbose_name_plural = 'Elementos del menú'

    def __str__(self):
        return self.name

    @property
    def is_module(self):
        """True si es un módulo raíz (sin padre)."""
        return self.parent is None

    @property
    def is_submodule(self):
        """True si es un submódulo (tiene padre)."""
        return self.parent is not None

    def _check_permissions(self, user):
        """Verifica si el usuario tiene los permisos requeridos."""
        if not self.permissions.exists():
            return True
        return user.has_perms([
            f'{p.content_type.app_label}.{p.codename}'
            for p in self.permissions.select_related('content_type').only(
                'codename', 'content_type__app_label'
            )
        ])

    def has_access(self, user):
        """¿Puede el usuario ver este elemento en el menú?"""
        if not self.is_active:
            return False
        if self.is_module:
            children = MenuItem.all_objects.filter(parent=self, is_active=True)
            if children.exists():
                return any(child.has_access(user) for child in children)
        return self._check_permissions(user)

    def accessible_children(self, user):
        """Retorna los hijos que el usuario puede ver."""
        if not self.is_module:
            return MenuItem.objects.none()
        children = MenuItem.all_objects.filter(parent=self, is_active=True).order_by('order')
        return [child for child in children if child.has_access(user)]
```

**Campos uno por uno:**

| Campo | Tipo | Explicación |
|-------|------|-------------|
| `parent` | FK a sí mismo | `null` = es módulo raíz. Con valor = es submódulo de ese padre |
| `name` | CharField(100) | Nombre visible en el menú. Ej: "Usuarios", "Facturas" |
| `icon` | CharField(50) | Clase de Bootstrap Icon. Ej: `bi-people`, `bi-receipt` |
| `url_name` | CharField(200) | Nombre de la ruta Django. Ej: `security:user_list` |
| `order` | IntegerField | Posición en el menú (1, 2, 3...) |
| `permissions` | M2M a `auth.Permission` | Qué permisos debe tener el usuario para ver este ítem |

**Métodos uno por uno:**

| Método | ¿Qué hace? |
|--------|------------|
| `is_module` | Propiedad: `True` si es raíz (`parent is None`) |
| `is_submodule` | Propiedad: `True` si es hijo (`parent is not None`) |
| `_check_permissions(user)` | Compara los permisos del `MenuItem` contra los del usuario |
| `has_access(user)` | Lógica completa: módulo revisa hijos; submódulo revisa permisos |
| `accessible_children(user)` | Filtra los hijos visibles para el usuario |

### 5.1 ¿Cómo funciona `has_access`?

```
has_access(user)
    │
    ├── ¿is_active? No  → False (no se muestra)
    │
    ├── ¿is_module (sin padre)?
    │   ├── ¿tiene hijos activos?
    │   │   ├── Sí → ¿algún hijo tiene access? Sí → True / No → False
    │   │   └── No → revisar permisos propios
    │   └── revisar permisos propios
    │
    └── ¿is_submodule (con padre)?
        └── revisar permisos propios
                ├── ¿sin permisos? → True (visible para todos)
                └── ¿con permisos? → user.has_perms(...) ?
                                         ├── Sí → True
                                         └── No → False
```

### 5.2 ¿Cómo funciona con Perfiles (Groups)?

Django `auth.Group` = el perfil/rol. Sin crear modelos nuevos.

```
Admin Django → Crear Group "Vendedor"
             → Asignar permiso "catalog.view_product" al grupo
             → Asignar usuario al grupo "Vendedor"
             → En MenuItem "Productos", asignar permiso "catalog.view_product"

Flujo:
    user.has_perm("catalog.view_product") → True (heredado del grupo)
    MenuItem.has_access(user) → True → se muestra en sidebar
```

---

## Fase 6 — Crear el Admin

**Paso 6.1:** Abre `core/admin.py` y escribe:

```python
from django.contrib import admin
from .models import MenuItem


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent_link', 'order', 'url_name', 'is_active']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'url_name']
    ordering = ['order', 'name']
    filter_horizontal = ['permissions']
    list_editable = ['order', 'is_active']

    def parent_link(self, obj):
        return obj.parent.name if obj.parent else '—'
    parent_link.short_description = 'Módulo padre'
    parent_link.admin_order_field = 'parent'

    def get_queryset(self, request):
        return MenuItem.all_objects.all()
```

**Explicación:**

| Configuración | ¿Qué hace? |
|---------------|------------|
| `list_display` | Columnas visibles en la tabla del admin |
| `list_editable` | Campos que se pueden editar directamente desde la lista |
| `filter_horizontal` | Widget visual para asignar permisos (M2M) |
| `get_queryset` | Usa `all_objects` para mostrar INCLUSO los eliminados en el admin |

---

## Fase 7 — Generar y ejecutar migraciones

**Paso 7.1:** Genera la migración inicial para `core`:

```bash
python manage.py makemigrations core
```

Deberías ver:
```
Migrations for 'core':
  core\migrations\0001_initial.py
    + Create model MenuItem
```

**Paso 7.2:** Crea una migración de datos vacía para el menú semilla:

```bash
python manage.py makemigrations core --empty --name seed_menu
```

Esto crea `core/migrations/0002_seed_menu.py`.

**Paso 7.3:** Abre `core/migrations/0002_seed_menu.py` y **reemplaza TODO** su contenido:

```python
from django.db import migrations


def seed_menu(apps, schema_editor):
    MenuItem = apps.get_model('core', 'MenuItem')

    modules = [
        {'name': 'Dashboard', 'icon': 'bi-speedometer2', 'url_name': 'home',
         'children': []},
        {'name': 'Seguridad', 'icon': 'bi-shield-lock', 'url_name': '',
         'children': [
            {'name': 'Usuarios', 'icon': 'bi-people', 'url_name': ''},
            {'name': 'Roles', 'icon': 'bi-person-badge', 'url_name': ''},
        ]},
        {'name': 'Cat\u00e1logo', 'icon': 'bi-box', 'url_name': '',
         'children': [
            {'name': 'Categor\u00edas', 'icon': 'bi-tags', 'url_name': ''},
            {'name': 'Productos', 'icon': 'bi-box-seam', 'url_name': ''},
        ]},
        {'name': 'Clientes', 'icon': 'bi-people', 'url_name': '',
         'children': [
            {'name': 'Listado de Clientes', 'icon': 'bi-list-ul', 'url_name': ''},
        ]},
        {'name': 'Ventas', 'icon': 'bi-cart', 'url_name': '',
         'children': [
            {'name': 'Facturas', 'icon': 'bi-receipt', 'url_name': ''},
            {'name': 'Reportes', 'icon': 'bi-graph-up', 'url_name': ''},
        ]},
    ]

    for idx, mod in enumerate(modules, start=1):
        module = MenuItem.objects.create(
            name=mod['name'],
            icon=mod['icon'],
            url_name=mod['url_name'],
            order=idx,
        )
        for jdx, sub in enumerate(mod['children'], start=1):
            MenuItem.objects.create(
                parent=module,
                name=sub['name'],
                icon=sub['icon'],
                url_name=sub['url_name'],
                order=jdx,
            )


def reverse_seed(apps, schema_editor):
    MenuItem = apps.get_model('core', 'MenuItem')
    MenuItem.all_objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_menu, reverse_seed),
    ]
```

**¿Qué hace esta migración?**

1. Crea 5 módulos raíz: Dashboard, Seguridad, Catálogo, Clientes, Ventas
2. Crea 7 submódulos hijos (Usuarios, Roles, Categorías, Productos, etc.)
3. Dashboard tiene `url_name='home'` para enlazar a la página principal
4. Los demás submódulos tienen `url_name=''` porque se crearán en laboratorios futuros
5. `reverse_seed` permite deshacer la migración (`python manage.py migrate core 0001`)

**Paso 7.4:** Ejecuta todas las migraciones:

```bash
python manage.py migrate
```

Deberías ver:
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, core, security, sessions
Running migrations:
  Applying core.0001_initial... OK
  Applying core.0002_seed_menu... OK
```

---

## Fase 8 — Verificar la base de datos

**Paso 8.1:** Verifica que los datos se crearon correctamente:

```bash
python manage.py shell
```

Dentro del shell interactivo, escribe:

```python
from core.models import MenuItem

print(f'Total elementos: {MenuItem.all_objects.count()}')
print(f'Elementos activos: {MenuItem.objects.count()}')

for m in MenuItem.all_objects.filter(parent__isnull=True).order_by('order'):
    children = MenuItem.all_objects.filter(parent=m).order_by('order')
    print(f'  [{m.order}] {m.icon} {m.name} ({len(children)} submodulos)')
    for s in children:
        print(f'    [{s.order}] {s.icon} {s.name} url={s.url_name!r}')
```

Deberías ver:
```
Total elementos: 12
Elementos activos: 12
  [1] bi-speedometer2 Dashboard (0 submodulos)
  [2] bi-shield-lock Seguridad (2 submodulos)
    [1] bi-people Usuarios url=''
    [2] bi-person-badge Roles url=''
  [3] bi-box Catálogo (2 submodulos)
    [1] bi-tags Categorías url=''
    [2] bi-box-seam Productos url=''
  [4] bi-people Clientes (1 submodulos)
    [1] bi-list-ul Listado de Clientes url=''
  [5] bi-cart Ventas (2 submodulos)
    [1] bi-receipt Facturas url=''
    [2] bi-graph-up Reportes url=''
```

**Paso 8.2:** Prueba el método `has_access`:

```python
from security.models import User

# Crear un usuario de prueba
user = User.objects.create_user(
    username='test', email='test@test.com',
    first_name='Test', last_name='User',
    password='test123'
)

# Verificar acceso a cada módulo
for m in MenuItem.all_objects.filter(parent__isnull=True).order_by('order'):
    access = m.has_access(user)
    children = m.accessible_children(user)
    print(f'{m.icon} {m.name}: access={access}, children={[c.name for c in children]}')

# Probar permisos: agregar permiso a Roles y verificar filtro
from django.contrib.auth.models import Group, Permission

roles = MenuItem.all_objects.get(name='Roles')
perm = Permission.objects.get(codename='view_group')
roles.permissions.add(perm)

seguridad = MenuItem.all_objects.get(name='Seguridad')
print(f'\nSin grupo: {[c.name for c in seguridad.accessible_children(user)]}')

vendedor = Group.objects.create(name='Vendedor')
vendedor.permissions.add(perm)
user.groups.add(vendedor)

print(f'Con grupo "Vendedor": {[c.name for c in seguridad.accessible_children(user)]}')

# Limpiar
roles.permissions.remove(perm)
vendedor.delete()
user.delete()
```

Deberías ver:
```
bi-speedometer2 Dashboard: access=True, children=[]
bi-shield-lock Seguridad: access=True, children=['Usuarios', 'Roles']
bi-box Catálogo: access=True, children=['Categorías', 'Productos']
bi-people Clientes: access=True, children=['Listado de Clientes']
bi-cart Ventas: access=True, children=['Facturas', 'Reportes']

Sin grupo: ['Usuarios']     ← Roles oculto (no tiene permiso)
Con grupo "Vendedor": ['Usuarios', 'Roles']  ← Roles visible ahora
```

**Escribe `exit()` para salir del shell.**

---

## Fase 9 — Probar en el Admin de Django

**Paso 9.1:** Inicia el servidor:

```bash
python manage.py runserver
```

**Paso 9.2:** Abre `http://localhost:8000/admin/` e inicia sesión con tu superusuario.

**Paso 9.3:** Busca la sección **"Core"** → **"Elementos del menú"**.

**Paso 9.4:** Verifica que ves los 12 elementos (5 módulos + 7 submódulos) con sus iconos y orden.

**Paso 9.5:** Haz clic en "Roles" y en el campo "Permisos requeridos" selecciona `auth | group | Can view group`.

**Paso 9.6:** Guarda los cambios. Ahora "Roles" solo será visible para usuarios con ese permiso.

---

## Fase 10 — Probar soft delete

**Paso 10.1:** En el admin, selecciona un submódulo (ej: "Reportes") y desmarca `is_active`, luego guarda.

**Paso 10.2:** Verifica en el shell:

```bash
python manage.py shell
```

```python
from core.models import MenuItem

print('Activos:', MenuItem.objects.count())
print('Total:', MenuItem.all_objects.count())
print('Desactivados:', MenuItem.all_objects.filter(is_active=False).count())
```

**Paso 10.3:** Restaura desde el shell:

```python
item = MenuItem.all_objects.get(name='Reportes')
item.restore()
print('Restaurado:', item.is_active, item.deleted_at)
exit()
```

---

## Checkpoint de verificación

```bash
python manage.py check
python manage.py migrate --list
```

Debe mostrar:
```
System check identified no issues (0 silenced).
core
 [X] 0001_initial
 [X] 0002_seed_menu
```

### Lista de criterios

| # | Criterio | Cumple |
|---|----------|--------|
| 1 | App `core` en `INSTALLED_APPS` | ☐ |
| 2 | Migraciones ejecutadas sin error | ☐ |
| 3 | 12 elementos de menú en base de datos | ☐ |
| 4 | `SoftDeleteManager` filtra `is_active=True` por defecto | ☐ |
| 5 | `all_objects` muestra todos los registros | ☐ |
| 6 | Admin de `MenuItem` funcional con `filter_horizontal` | ☐ |
| 7 | `has_access(user)` devuelve `True` para usuarios sin permisos | ☐ |
| 8 | `has_access(user)` oculta ítems con permisos que el usuario no tiene | ☐ |
| 9 | `has_access(user)` oculta módulos sin hijos accesibles | ☐ |
| 10 | `soft_delete()` y `restore()` funcionan correctamente | ☐ |

---

## Resumen — Lo que construimos hoy

```
┌──────────────────────────────────────────────────────────────────┐
│                         core/models.py                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  SoftDeleteManager(models.Manager)                               │
│    └── get_queryset() → filter(is_active=True)                   │
│                                                                  │
│  BaseModel(models.Model)  [abstract]                             │
│    ├── created_at: DateTime (auto_now_add)                       │
│    ├── updated_at: DateTime (auto_now)                           │
│    ├── deleted_at: DateTime (nullable)                           │
│    ├── is_active: Boolean (default=True)                         │
│    ├── objects = SoftDeleteManager()                             │
│    ├── all_objects = models.Manager()                            │
│    ├── soft_delete() → is_active=False, deleted_at=now           │
│    └── restore() → is_active=True, deleted_at=None               │
│                                                                  │
│  MenuItem(BaseModel)                                             │
│    ├── parent: FK → self (null = módulo raíz)                   │
│    ├── name: CharField(100)                                      │
│    ├── icon: CharField(50)                                       │
│    ├── url_name: CharField(200)                                  │
│    ├── order: PositiveIntegerField                               │
│    ├── permissions: M2M → auth.Permission                       │
│    ├── is_module: property (parent is None)                      │
│    ├── is_submodule: property (parent is not None)               │
│    ├── has_access(user): bool                                    │
│    └── accessible_children(user): list[MenuItem]                 │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Próximo laboratorio

[**Laboratorio 05 — Panel Admin: Sidebar + Layout + Context Processor**](./guia-laboratorio-05.md)

Crearemos el context processor de menú, el layout del panel administrativo con sidebar izquierdo (módulos → submódulos) y el panel derecho con accordion de módulos y enlaces a vistas.

---

## Referencias

- [Django Models](https://docs.djangoproject.com/en/6.0/topics/db/models/)
- [Django Managers](https://docs.djangoproject.com/en/6.0/topics/db/managers/)
- [Django Migrations](https://docs.djangoproject.com/en/6.0/topics/migrations/)
- [Django Admin](https://docs.djangoproject.com/en/6.0/ref/contrib/admin/)
- [Django auth — Permission and Groups](https://docs.djangoproject.com/en/6.0/topics/auth/default/#permissions-and-authorization)
- [Bootstrap Icons](https://icons.getbootstrap.com/)
- [Soft Delete Pattern](https://en.wikipedia.org/wiki/Soft_deletion)
