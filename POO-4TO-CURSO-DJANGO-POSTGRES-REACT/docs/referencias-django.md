# Referencia del Framework Django — MVT, componentes y arquitectura

> **Documento de referencia** (no se ejecuta paso a paso como las guías de laboratorio). Léalo **antes** de la práctica para entender los conceptos, o **durante** la práctica cuando una guía mencione un componente que quiera profundizar.
>
> **Audiencia:** estudiantes de **Programación Orientada a Objetos (4to curso)** que ya saben Python y están dando sus primeros pasos con Django.
>
> **Enfoque:** el *porqué* detrás del *cómo*. Cada componente se explica con un diagrama ASCII, una tabla comparativa y un ejemplo mínimo.
>
> ⚠️ **Nota sobre DRF:** Este documento incluye secciones sobre Django REST Framework (DRF) como referencia teórica general. **El proyecto de laboratorio (guías 01–11) usa exclusivamente Django MVT (Vistas Basadas en Clases + Templates, sin React ni APIs REST).** Las secciones de DRF son complementarias y no necesarias para completar las guías.

---

## Tabla de contenido

1. [¿Qué es Django?](#1-qué-es-django)
2. [Filosofía: DRY, convención sobre configuración, "batteries included"](#2-filosofía-dry-convención-sobre-configuración-batteries-included)
3. [Arquitectura MVT (vs MVC)](#3-arquitectura-mvt-vs-mvc)
4. [El ciclo Request/Response](#4-el-ciclo-requestresponse)
5. [Estructura de un proyecto Django](#5-estructura-de-un-proyecto-django)
6. [Models y ORM](#6-models-y-orm)
7. [Views: FBV, CBV y ViewSets](#7-views-fbv-cbv-y-viewsets)
8. [URL Dispatcher](#8-url-dispatcher)
9. [Django REST Framework: la capa API](#9-django-rest-framework-la-capa-api)
10. [Middleware](#10-middleware)
11. [Settings divididos y el patrón 12-Factor](#11-settings-divididos-y-el-patrón-12-factor)
12. [Django Admin](#12-django-admin)
13. [Comandos esenciales de `manage.py`](#13-comandos-esenciales-de-managepy)
14. [Glosario POO aplicado a Django](#14-glosario-poo-aplicado-a-django)
15. [Referencias](#15-referencias)

---

## 1. ¿Qué es Django?

**Django** es un *framework* web de alto nivel escrito en Python que fomenta un desarrollo rápido y un diseño limpio y pragmático. Lo mantienen la *Django Software Foundation* y miles de contribuidores; es **gratuito y de código abierto**.

Lo usan Instagram, Pinterest, Mozilla, Disqus, National Geographic y muchos más. Su lema es *"The web framework for perfectionists with deadlines"* (el framework para perfeccionistas con plazos).

**Para qué sirve:** APIs REST, sitios web con panel administrativo, CMS, plataformas de datos, MVPs. **No** es ideal para: microservicios muy pequeños (use Flask/FastAPI) o aplicaciones en tiempo real de alta concurrencia (use Node.js, Go).

```powershell
# Tres líneas y ya tiene una API REST funcionando:
pip install "Django>=5.1,<6.0" djangorestframework
django-admin startproject config .
python manage.py runserver
```

---

## 2. Filosofía: DRY, convención sobre configuración, "batteries included"

| Principio | Significado | Ejemplo en Django |
|---|---|---|
| **DRY** (*Don't Repeat Yourself*) | Una sola fuente de verdad para cada pieza de información | Definir un modelo *una vez*; el ORM genera la tabla SQL, el admin muestra la UI, el serializer expone el JSON. |
| **Convención sobre configuración** | Decisiones tomadas por defecto; solo se configura lo que cambia | `python manage.py startapp accounts` crea la estructura de carpetas esperada. |
| **Batteries included** | Todo lo común viene incluido; nada de instalar 20 paquetes | ORM, admin, auth, sesiones, i18n, formularios, caché, signals, *middleware* — todo en `django.contrib.*`. |

> **POO:** estos tres principios se traducen a **abstracción** (no reinventar la rueda), **encapsulación** (cada componente oculta sus detalles) y **reutilización** (las apps se mueven entre proyectos).

---

## 3. Arquitectura MVT (vs MVC)

Django implementa el patrón **MVT** (*Model-View-Template*). Es una variante del clásico **MVC** (*Model-View-Controller*) en la que Django absorbe el rol del *Controller* en su framework (URL dispatcher + middleware), por lo que solo deja visibles M, V y T al desarrollador.

```
+---------------------------+        +---------------------------+
|         MVC clásico       |        |   Django MVT              |
+---------------------------+        +---------------------------+
|  Model   → datos           |        |  Model    → datos         |
|  View    → presentación    |  -->   |  Template → presentación  |
|  Controller → lógica +     |        |  View     → lógica        |
|              enrutamiento  |        |  (enrutamiento lo hace   |
|                           |        |   el framework: urls +   |
|                           |        |   middleware)            |
+---------------------------+        +---------------------------+
```

**Tabla comparativa MVT vs MVC:**

| Pieza | MVC | MVT (Django) | Responsabilidad |
|---|---|---|---|
| **Model** | Model | Model | Acceso a datos (ORM). |
| **View** | View | **Template** | Lo que se *muestra* al usuario (HTML). |
| **Controller** | Controller | **View** | La *lógica* que decide qué hacer con la petición. |
| *(implícito)* | *(no existe)* | URL Dispatcher | Decide qué `View` se ejecuta según la URL. |

**¿Por qué importa entender MVT?** Porque cuando un estudiante busca "Django view vs MVC view" en internet, encuentra documentación que mezcla ambos modelos. La conclusión es: **en Django, "View" significa "lógica"**, no "presentación" como en otros frameworks.

```
  Cliente (navegador)                 Django
        |                                |
        | GET /notes/                    |
        |------------------------------->|
        |                                |  1. MIDDLEWARE (request)
        |                                |     (sesión, CSRF, auth...)
        |                                |  2. URLconf  ->  View
        |                                |  3. VIEW     (lógica)
        |                                |  4. MODEL    (consulta ORM)
        |                                |  5. SERIALIZER / TEMPLATE
        |                                |  6. MIDDLEWARE (response)
        |  HTTP 200 [                    |
        |    {nota1}, {nota2}, ... ]     |
        |<-------------------------------|
        |                                |
```

---

## 4. El ciclo Request/Response

Cada petición HTTP pasa por una *cadena de montaje* y *desmontaje*. Los componentes se ejecutan en un orden estricto:

| # | Componente | Qué hace | Cuándo corre |
|---|---|---|---|
| 1 | **Middleware (request)** | Procesa la petición antes de la vista (auth, sesión, CSRF). | Antes de la vista |
| 2 | **URLconf** | Resuelve `/api/v1/notes/` → `NoteViewSet`. | Antes de la vista |
| 3 | **View / ViewSet** | Lógica de negocio: recibe la request, decide qué hacer. | Centro del flujo |
| 4 | **Authentication** (DRF) | Lee el token JWT, identifica al usuario. | Dentro de la view |
| 5 | **Permission** (DRF) | Verifica `IsAuthenticated`, `IsAdmin`, etc. | Dentro de la view |
| 6 | **Serializer / Form** | Valida y deserializa la entrada. | Dentro de la view |
| 7 | **Model / ORM** | Ejecuta `Note.objects.filter(owner=...)` → SQL. | Dentro de la view |
| 8 | **Response** | Construye la respuesta (HTML, JSON, redirect). | Después de la view |
| 9 | **Middleware (response)** | Comprime, cifra cookies, añade headers. | Después de la view |
| 10 | **Middleware (exception)** | Si algo falló, lo convierte en 404/500/etc. | Si hay excepción |

**Diagrama con DRF (lo que usa este laboratorio):**

```
Petición HTTP
    │
    ▼
┌──────────────────┐
│  MIDDLEWARES     │  CorsMiddleware, SessionMiddleware,
│  (request)       │  AuthenticationMiddleware
└─────┬────────────┘
      ▼
┌──────────────────┐
│  ROOT_URLCONF    │  config/urls.py
└─────┬────────────┘
      ▼
┌──────────────────┐
│  URLconf de app  │  apps/core/urls.py  (DefaultRouter)
└─────┬────────────┘
      ▼
┌──────────────────┐
│  APIView         │  NoteViewSet (ModelViewSet)
│  (CBV en DRF)    │
└─────┬────────────┘
      ▼
┌──────────────────┐
│  Authentication  │  JWTAuthentication (lee Bearer)
└─────┬────────────┘
      ▼
┌──────────────────┐
│  Permission      │  IsAuthenticated
└─────┬────────────┘
      ▼
┌──────────────────┐
│  Serializer      │  NoteSerializer (valida entrada)
└─────┬────────────┘
      ▼
┌──────────────────┐
│  perform_create  │  serializer.save(owner=request.user)
└─────┬────────────┘
      ▼
┌──────────────────┐
│  ORM             │  Note.objects.create(...) → SQL
└─────┬────────────┘
      ▼
┌──────────────────┐
│  Response        │  JSON 201 + Location header
└─────┬────────────┘
      ▼
┌──────────────────┐
│  MIDDLEWARES     │  compresión, CORS headers
│  (response)      │
└─────┬────────────┘
      ▼
  Cliente
```

> **Concepto POO:** la cadena *Middleware → URLconf → View → ORM → Middleware* es una composición de objetos (cada uno con un solo trabajo) que se encadenan para resolver la petición. Es el patrón **Cadena de Responsabilidad**.

---

## 5. Estructura de un proyecto Django

> Un *proyecto* es la configuración global (base de datos, settings, URLs raíz). Una *app* es un módulo reusable que agrupa modelos y vistas de un bounded context.

**Diferencia proyecto vs app:**

| | Proyecto (`config/`) | App (`apps/accounts/`) |
|---|---|---|
| Qué contiene | Settings, URLs raíz, WSGI/ASGI | Modelos, vistas, serializers, admin, migrations |
| Cuántos hay | **Uno** por proyecto Django | **Muchos** (uno por bounded context) |
| Se reusa entre proyectos | No (es único) | Sí (puede moverse a otro proyecto) |
| Analogía POO | El *contenedor* principal | Un *módulo* cohesivo |

**Cuándo crear una app nueva:** cuando un conjunto de modelos, vistas y serializers tiene una responsabilidad clara y se podría reusar. Regla práctica: si la palabra "y" aparece en el nombre (`accounts_and_profiles`), probablemente son **dos apps**.

**Estructura de carpetas del laboratorio (Parte 2):**

```
backend/
├── manage.py                    # CLI: python manage.py <comando>
├── requirements.txt
├── .env                         # variables de entorno (no se commitea)
├── .env.example                 # plantilla (sí se commitea)
├── config/                      # PROYECTO
│   ├── __init__.py
│   ├── settings/                # settings divididos (base/dev/prod)
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── urls.py                  # URLconf raíz
│   ├── wsgi.py                  # entry point para servidores sync
│   └── asgi.py                  # entry point para servidores async
└── apps/                        # APPS
    ├── __init__.py
    ├── accounts/                # bounded context: usuarios
    │   ├── __init__.py
    │   ├── apps.py              # AppConfig
    │   ├── models.py            # User
    │   ├── admin.py             # registro en el panel admin
    │   ├── serializers.py       # UserSerializer, RegisterSerializer
    │   ├── views.py             # RegisterView, MeView
    │   ├── urls.py              # /auth/register/, /auth/me/
    │   └── migrations/
    │       └── __init__.py
    └── core/                    # bounded context: dominio de la app
        ├── __init__.py
        ├── apps.py
        ├── models.py            # Note
        ├── admin.py
        ├── serializers.py       # NoteSerializer
        ├── views.py             # NoteViewSet
        ├── urls.py              # /notes/ (router)
        └── migrations/
            └── __init__.py
```

---

## 6. Models y ORM

El **ORM** (*Object-Relational Mapper*) traduce clases Python a tablas SQL. Usted define la *clase*; Django genera el `CREATE TABLE`, el `INSERT`, el `SELECT`, etc.

**Mapeo clase ↔ tabla:**

```
  Clase Python                              Tabla SQL
  ─────────────────────────                 ─────────────────────────────
  class Note(models.Model):                 CREATE TABLE notes (
      title = CharField(200)                   id          BIGINT PRIMARY KEY,
      body  = TextField()                      title       VARCHAR(200) NOT NULL,
      owner = ForeignKey(User)                 body        TEXT NOT NULL,
                                               owner_id    BIGINT REFERENCES users(id),
  )                                           created_at  DATETIME NOT NULL,
                                              updated_at  DATETIME NOT NULL
                                          );
```

**Anatomía de un campo (Field):**

```python
title = models.CharField(
    max_length=200,                   # obligatorio para CharField
    verbose_name="Título",            # etiqueta legible en admin
    help_text="Título corto",         # tooltip
    default="",                       # valor por defecto
    null=False, blank=False,          # null=False → NOT NULL en SQL
    db_index=True,                    # crea índice (acelera búsquedas)
    unique=False,                     # crea UNIQUE constraint
)
```

**Tipos de relación:**

| Tipo | SQL | Ejemplo |
|---|---|---|
| `ForeignKey` | `*_id BIGINT REFERENCES` | `Note.owner` → `User` (N notas → 1 usuario) |
| `OneToOneField` | `UNIQUE` en la FK | `User.profile` → `Profile` (1 a 1) |
| `ManyToManyField` | tabla intermedia | `User.groups` → `Group` (N a N) |

**QuerySet API — los métodos que más usará:**

```python
# SELECT
Note.objects.all()                                   # todas
Note.objects.filter(owner=request.user)              # WHERE
Note.objects.exclude(is_draft=True)                  # WHERE NOT
Note.objects.get(pk=1)                               # WHERE id=1 (¡1 resultado!)
Note.objects.order_by("-created_at")                 # ORDER BY
Note.objects.first() / .last()                       # LIMIT 1
Note.objects.count()                                 # SELECT COUNT(*)
Note.objects.exists()                                # SELECT 1 ... LIMIT 1

# Mutaciones
note = Note.objects.create(title="x", owner=u)       # INSERT
note.title = "y"; note.save()                        # UPDATE
note.delete()                                        # DELETE

# Encadenamiento (cada método devuelve un nuevo QuerySet)
Note.objects.filter(owner=u).exclude(is_draft=True).order_by("-created_at")[:10]
```

**Migrations — qué son y cómo funcionan:**

```powershell
python manage.py makemigrations     # detecta cambios en models.py y genera archivo .py
python manage.py migrate            # aplica las migrations pendientes a la BD
```

Una *migration* es un archivo Python versionado que describe el cambio al esquema (`AddField`, `AlterField`, `CreateModel`, etc.). Se commitea al repositorio junto con el modelo. **Nunca edite la BD a mano;** siempre via migration.

```
0001_initial.py     # estado inicial
0002_note_priority.py  # añadió Note.priority
0003_alter_user_email.py  # User.email ahora es único
```

> **Concepto POO:** cada `Model` es una **abstracción** de una tabla SQL; cada instancia es un **objeto** con identidad, estado y comportamiento (puede tener métodos como `def is_recent(self): ...`).

---

## 7. Views: FBV, CBV y ViewSets

Django ofrece tres estilos de vista. Cada uno resuelve un problema diferente.

**Jerarquía de clases (DRF + Django CBV):**

```
                        View (django.views.View)
                            │
                        APIView (rest_framework.views)
                            │
                        GenericAPIView (rest_framework.generics)
                       /        |         \
              ListAPIView   CreateAPIView   RetrieveAPIView
                  ↓              ↓                ↓
              ListCreateAPIView          RetrieveUpdateDestroyAPIView
                            │
                        ModelViewSet (rest_framework.viewsets)
                            │
                        NoteViewSet  (su view personalizada)
```

**Tabla comparativa:**

| Estilo | Cuándo usarlo | Líneas para CRUD simple |
|---|---|---|
| **FBV** (Function-Based View) | Lógica simple, una sola acción, integración con libs externas. | ~5 |
| **CBV** (Class-Based View) | Necesita reutilizar comportamiento (formularios, login_required, mixins). | ~3 |
| **Generic CBV** (ListCreateAPIView, etc.) | CRUD estándar sobre un modelo. | ~3 |
| **ViewSet** (DRF) | CRUD completo de un recurso + router automático. | ~6 (incluye `get_queryset`, `perform_create`) |

**Ejemplo de los 4 estilos para la misma operación "crear nota":**

```python
# FBV (Function-Based View) ----------------------------
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_note(request):
    serializer = NoteSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(owner=request.user)
    return Response(serializer.data, status=201)


# CBV (Class-Based View) -------------------------------
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

class CreateNoteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = NoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user)
        return Response(serializer.data, status=201)


# Generic CBV -----------------------------------------
from rest_framework import generics

class CreateNoteView(generics.CreateAPIView):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]
    # perform_create se hereda y llama a serializer.save()
    # PERO: no pasa el owner automáticamente → hay que sobreescribirlo


# ViewSet (lo que usa este laboratorio) ----------------
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Note.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
```

**¿Por qué el laboratorio usa `ModelViewSet`?** Porque con 6 líneas obtiene 5 endpoints (`GET /notes/`, `POST /notes/`, `GET /notes/<id>/`, `PUT /notes/<id>/`, `DELETE /notes/<id>/`) y el router genera las URLs automáticamente. **Es DRY al extremo.**

> **Concepto POO:** `ViewSet` aplica el patrón **Template Method** — la clase base define el algoritmo (`list`, `create`, `retrieve`, ...) y deja a las subclases sobreescribir solo los pasos variables (`get_queryset`, `perform_create`). Es **herencia con polimorfismo**.

---

## 8. URL Dispatcher

El `URLconf` mapea una URL a una view. La evaluación es **de arriba a abajo** y se detiene en el primer match.

```python
# config/urls.py
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/token/", TokenObtainPairView.as_view()),
    path("api/v1/", include("apps.core.urls")),
]

# apps/core/urls.py
from rest_framework.routers import DefaultRouter
from .views import NoteViewSet

router = DefaultRouter()
router.register(r"notes", NoteViewSet, basename="note")
# genera: /notes/        (GET, POST)
//        /notes/<pk>/   (GET, PUT, PATCH, DELETE)

urlpatterns = router.urls
```

**Conversores de URL (path converters):**

| Conversor | Match | Ejemplo |
|---|---|---|
| `int` | dígitos | `path("notes/<int:pk>/")` → `notes/42/` |
| `str` | cualquier texto (sin `/`) | `path("u/<str:username>/")` |
| `slug` | letras, dígitos, `-`, `_` | `path("p/<slug:slug>/")` |
| `uuid` | UUID | `path("t/<uuid:id>/")` |
| `path` | cualquier texto (incluye `/`) | `path("files/<path:fp>/")` |

**`include()` y namespaces:**

```python
# URL raíz
path("api/v1/", include(("apps.core.urls", "core"), namespace="v1"))
# en apps/core/urls.py: app_name = "core"

# Reverse URL en el código
from django.urls import reverse
url = reverse("v1:note-list")              # /api/v1/notes/
url = reverse("v1:note-detail", args=[42]) # /api/v1/notes/42/
```

> **Buena práctica:** use `reverse()` en lugar de hardcodear URLs. Si cambia el prefijo `/api/v1/` a `/api/v2/`, no tiene que buscar en 50 archivos.

---

## 9. Django REST Framework: la capa API

Django por sí solo es para servir HTML. Para construir APIs JSON se usa **Django REST Framework (DRF)**, que añade:

| Componente DRF | Equivalente Django | Qué hace |
|---|---|---|
| `Serializer` | `Form` | Valida entrada + serializa salida |
| `APIView` | `View` | Una view HTTP con un método por verbo |
| `ViewSet` | `View` genérica | Agrupa las 5 acciones CRUD en una clase |
| `Router` | `urls.py` | Genera URLs a partir de un ViewSet |
| `Authentication` | `request.user` | Lee token JWT, sesión, etc. |
| `Permission` | `@login_required` | `IsAuthenticated`, `IsAdminUser`, etc. |
| `Pagination` | (no existe) | Corta resultados en páginas |
| `Throttle` | (no existe) | Limita requests por usuario/IP |

**El Serializer — el adaptador más importante:**

Un `Serializer` cumple **dos roles**:

1. **Deserializar y validar** datos de entrada (request).
2. **Serializar** un objeto de Python a un formato portable (JSON).

```python
class NoteSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Note
        fields = ("id", "title", "body", "owner", "created_at", "updated_at")
        read_only_fields = ("id", "owner", "created_at", "updated_at")
```

**Equivalente "adaptador":**

```
                    ┌─────────────────────┐
   JSON entrante → │                     │ → objeto Model válido
   {"title": "x"}  │  NoteSerializer     │
                    │  (deserializa)      │
   objeto Model  →  │                     │ → JSON saliente
   Note(id=1,...)   │  (serializa)        │    {"id": 1, "title": "x", ...}
                    └─────────────────────┘
```

**Autenticación en DRF — cómo encadena con JWT:**

```
1. Request llega con "Authorization: Bearer eyJhbGc..."
                              │
2. JWTAuthentication.authenticate(request)
                              │
3. Decodifica el JWT → obtiene el user_id
                              │
4. SELECT user por id → request.user
                              │
5. Si IsAuthenticated: request.user.is_authenticated → True → allow
   Si no: 401 Unauthorized
```

**Composición típica de una view DRF:**

```python
class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer     # qué serializer usar
    permission_classes = [IsAuthenticated]  # quién puede llamar
    authentication_classes = [JWTAuthentication]  # cómo identificar al usuario
    pagination_class = PageNumberPagination  # cómo paginar
    throttle_classes = [UserRateThrottle]   # cuánto puede llamar

    def get_queryset(self):                 # QUÉ objetos ve
        return Note.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):   # CÓMO crea (inyecta owner)
        serializer.save(owner=self.request.user)
```

> **Concepto POO:** DRF aplica **Inyección de Dependencias**: la view no *crea* su serializer ni su permission; los recibe como atributos que se pueden cambiar. Esto facilita los tests (inyectar un mock) y la composición.

---

## 10. Middleware

Un *middleware* es un objeto que envuelve cada petición y cada respuesta. Útil para: autenticación transversal, CORS, compresión, logging, manejo de excepciones.

```python
def simple_middleware(get_response):
    def middleware(request):
        # === código ANTES de la view (request) ===
        print(f"[req] {request.method} {request.path}")

        response = get_response(request)   # llama a la view

        # === código DESPUÉS de la view (response) ===
        print(f"[res] {response.status_code}")
        return response
    return middleware
```

**Orden de middleware** (en `settings.py` — el orden importa):

```
request:  →  SecurityMiddleware  →  CorsMiddleware  →  SessionMiddleware
          →  CommonMiddleware  →  CsrfViewMiddleware  →  AuthenticationMiddleware
          →  MessageMiddleware  →  ClickjackingMiddleware  →  View

response: ←  View  ←  ... (orden inverso)  ←  SecurityMiddleware
```

**Regla práctica:** ponga su middleware **antes** de cualquier middleware que necesite su output. Por ejemplo, `CorsMiddleware` debe ir antes de cualquier middleware que pueda generar una respuesta (para que los headers CORS aparezcan incluso en errores).

---

## 11. Settings divididos y el patrón 12-Factor

El patrón **12-Factor App** dice: la configuración debe venir del entorno, no del código. Django lo implementa así:

```python
# config/settings/base.py   ← valores comunes
SECRET_KEY = config("DJANGO_SECRET_KEY")     # lee de os.environ
DEBUG = config("DJANGO_DEBUG", default=False, cast=bool)
DATABASES = {
    "default": {
        "ENGINE": config("DB_ENGINE"),
        "NAME":   config("DB_NAME"),
        ...
    }
}

# config/settings/dev.py    ← overrides para desarrollo
from .base import *
DEBUG = True
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# config/settings/prod.py   ← overrides para producción
from .base import *
DEBUG = False
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
```

```
   .env (variables)             config/settings/
   ─────────────────            ────────────────
   DJANGO_SECRET_KEY=abc…        base.py  ← lee con python-decouple
   DB_ENGINE=postgresql            ↓
   DB_NAME=poo_db                dev.py   ← hereda y sobreescribe
   ...                          prod.py  ← hereda y sobreescribe
```

Para activar un settings: `DJANGO_SETTINGS_MODULE=config.settings.dev python manage.py runserver`.

**Ventajas:**

| Aspecto | Sin split | Con split |
|---|---|---|
| Mismo settings para dev y prod | Sí (con `if DEBUG:`) | No (cada entorno tiene el suyo) |
| Riesgo de subir DEBUG=True a prod | Alto | Nulo (no se importa dev.py) |
| Onboarding de nuevos devs | Copiar settings.py y rezar | Copiar `.env.example` y rellenar |

---

## 12. Django Admin

El `admin` es un **CRUD autogenerado** para los modelos. Una vez que registra un modelo, Django crea las pantallas de lista, detalle, crear y editar sin que usted escriba HTML.

```python
# apps/core/admin.py
from django.contrib import admin
from .models import Note

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner", "created_at")  # columnas de la tabla
    list_filter = ("owner",)                                 # filtros laterales
    search_fields = ("title", "body", "owner__username")    # caja de búsqueda
    readonly_fields = ("created_at", "updated_at")           # no editables
    ordering = ("-created_at",)                              # ORDER BY
```

**Cómo se ve** (`http://localhost:8000/admin/`):

```
+---------------------------------------------+
| Django administration                       |
+---------------------------------------------+
| ACCOUNTS                                    |
|   > Users                                   |  ← @admin.register(User)
|     Add user +                               |
|     Search username, email...               |
|                                             |
| CORE                                        |
|   > Notes                                   |  ← @admin.register(Note)
|     Add note +                               |
|     Search title...                          |
+---------------------------------------------+
```

**Reglas del admin:**

- Para usar el admin, primero cree un superusuario: `python manage.py createsuperuser`.
- El admin **no es para usuarios finales**; es para administradores internos.
- Para CRUD desde el frontend use DRF (`ModelViewSet`) — es la API que consume el cliente.

---

## 13. Comandos esenciales de `manage.py`

`manage.py` es la CLI de Django. Los comandos más usados:

| Comando | Para qué sirve |
|---|---|
| `startproject <name>` | Crea un nuevo proyecto (esqueleto). |
| `startapp <name>` | Crea una nueva app dentro del proyecto. |
| `runserver [puerto]` | Inicia el servidor de desarrollo (auto-reload). |
| `makemigrations [app]` | Genera archivos de migration a partir de cambios en `models.py`. |
| `migrate` | Aplica las migrations pendientes a la BD. |
| `showmigrations` | Lista todas las migrations y su estado (`[X]` aplicada, `[ ]` pendiente). |
| `createsuperuser` | Crea un usuario con permisos de admin. |
| `shell` | Abre una consola Python con el proyecto ya cargado. |
| `dbshell` | Abre el cliente nativo de la BD (psql, mysql, sqlite3). |
| `check` | Ejecuta los chequeos de configuración sin tocar la BD. |
| `collectstatic` | Copia los archivos estáticos a `STATIC_ROOT` (para producción). |
| `test [app]` | Ejecuta los tests con `unittest`/`pytest`. |
| `dumpdata` / `loaddata` | Exporta / importa datos en formato JSON. |
| `sqlmigrate <app> <n>` | Muestra el SQL que generará una migration (útil para entender). |

```powershell
# Flujo de trabajo típico
python manage.py makemigrations         # 1. detectar cambios en modelos
python manage.py migrate                # 2. aplicar a la BD
python manage.py createsuperuser        # 3. crear admin
python manage.py runserver              # 4. desarrollar
python manage.py check                  # 5. verificar antes de commit
```

> **Atajo:** use `python manage.py <comando> --help` para ver todas las opciones de cualquier comando.

---

## 14. Glosario POO aplicado a Django

| Principio POO | Aplicación en Django |
|---|---|
| **SRP** (Responsabilidad Única) | Cada app tiene una sola responsabilidad. Si su `views.py` supera ~200 líneas, divídala. |
| **OCP** (Abierto/Cerrado) | Las *generic class-based views* y *mixins* permiten extender sin modificar el código base. |
| **LSP** (Liskov Substitution) | Cualquier subclase de `AbstractUser` (como nuestro `User`) es sustituible en todo el framework. |
| **DIP** (Inversión de Dependencias) | `base.py` no conoce directamente PostgreSQL o MySQL; depende de la *abstracción* `DB_ENGINE`. |
| **ISP** (Segregación de Interfaces) | `IsAuthenticated` y `IsAdminUser` son interfaces pequeñas y combinables, no un "God Permission". |
| **DRY** | Modelos, migrations, admin, serializers y vistas derivan todos de la misma definición de `class Note(models.Model)`. |
| **Encapsulación** | Un *manager* (`Note.objects`) oculta el SQL generado; usted llama `Note.objects.filter(...)` sin saber el SQL. |
| **Composición** | Una `ViewSet` *contiene* un serializer, un permission y un authentication class — en lugar de heredar de cada uno. |
| **Inyección de Dependencias** | Las `THIRD_PARTY_APPS` se enchufan al framework sin modificarlo; basta con añadirlas a `INSTALLED_APPS`. |

---

## 15. Referencias

- [Documentación oficial de Django 5](https://docs.djangoproject.com/en/5.0/)
- [Tutorial oficial (vota por la "Polls app")](https://docs.djangoproject.com/en/5.0/intro/tutorial01/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Classy Class-Based Views](https://ccbv.co.uk/) — referencia visual de CBV
- [Classy DRF](https://www.cdrf.co/) — referencia visual de DRF
- [Django for Everybody (Dr. Chuck)](https://www.dj4e.com/) — curso gratuito
- [Two Scoops of Django (libro)](https://www.feldroy.com/books/two-scoops-of-django-3-x) — best practices
- [Django Source Code en GitHub](https://github.com/django/django) — la mejor documentación es el código

---

*Fin de la referencia. Si encuentra un concepto que no está aquí y debería estarlo, añádalo — la documentación viva es la que más se usa.*
