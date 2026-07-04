# Guía de Laboratorio 03 — Diagramas UML del Sistema

> **Parte 3** · ⏱ **45 min – 1 hora**
> **Prerrequisito:** [Parte 2](./guia-laboratorio-02.md) completada (módulo seguridad funcional).
> **Alcance:** diagramas UML del sistema de autenticación.

| ⬅️ Anterior | 📘 Esta guía | ➡️ Siguiente |
|---|---|---|
| [02 — Módulo Seguridad](./guia-laboratorio-02.md) | **03** UML | [**03b — Login Profesional**](./guia-laboratorio-03b.md) |

---

## 1. Fase 8 — Diagramas UML (PlantUML)

> 💡 **Concepto POO:** un diagrama UML captura la estructura (clases) y el comportamiento (secuencia) del sistema.

### 1.1 Instalar PlantUML en VSCode

`Ctrl + Shift + X` → busque **PlantUML** (jebbs) → instale. Previsualizar: `Alt + D` con el `.puml` abierto.

### 1.2 Crear archivos

En `docs/uml/` cree 4 archivos vacíos:

```
docs/uml/
├── 03-despliegue.puml
├── 03-clases-seguridad.puml
├── 03-er-auth.puml
└── 03-secuencia-login.puml
```

### 1.3 Diagrama de despliegue

📄 **`docs/uml/03-despliegue.puml`**

```plantuml
@startuml 03-despliegue
title Arquitectura Monolito MVT

node "Navegador" as Browser {
  component "HTML + Bootstrap + JS" as Frontend
}

node "Servidor Django" as Server {
  component "URL Dispatcher\n(config/urls.py)" as URLs
  component "Views\n(lógica de negocio)" as Views
  component "Templates\n(HTML dinámico)" as Templates
  component "Models + ORM\n(abstracción de datos)" as Models
}

node "Base de datos" as DBNode {
  database "MySQL / PostgreSQL" as DB
}

Browser --> Server : HTTP (GET/POST/JSON)
Server --> Browser : HTTP Response (HTML/JSON)
URLs --> Views : enruta petición
Views --> Models : consulta/guarda
Views --> Templates : renderiza HTML
Models --> DB : SQL
@enduml
```

### 1.4 Diagrama de clases

📄 **`docs/uml/03-clases-seguridad.puml`**

```plantuml
@startuml 03-clases-seguridad
title Clases del módulo seguridad

class User <<security>> {
  - pkid: BigAutoField <<PK>>
  - id: UUIDField <<unique>>
  - username: str
  - email: str
  - first_name: str
  - last_name: str
  - password: str
  - is_active: bool
  - is_staff: bool
  - date_joined: datetime
  - created_at: datetime
  - updated_at: datetime
  - foto: ImageField
  + get_full_name: str
}

class CustomUserManager <<security>> {
  + create_user(username, first_name, last_name, email, password): User
  + create_superuser(username, first_name, last_name, email, password): User
}

class LoginPageView <<security>> {
  + get(): HTML
  + post(): JsonResponse
}

class InicioTemplate <<security>> {
  + get(): HTML
}

CustomUserManager ..> User : crea
LoginPageView ..> User : autentica
InicioTemplate ..> User : muestra datos
@enduml
```

### 1.5 Modelo ER

📄 **`docs/uml/03-er-auth.puml`**

```plantuml
@startuml 03-er-auth
title Modelo ER — Tabla security_user

entity "security_user" as users {
  *pkid : BIGINT <<PK>>
  *id : UUID <<UNIQUE>>
  *username : VARCHAR(150) <<UNIQUE>>
  *email : VARCHAR(254) <<UNIQUE>>
  *password : VARCHAR(128)
  *first_name : VARCHAR(50)
  *last_name : VARCHAR(50)
  *is_active : BOOLEAN
  *is_staff : BOOLEAN
  *date_joined : DATETIME
  *created_at : DATETIME
  *updated_at : DATETIME
  foto : VARCHAR(1024)
  last_login : DATETIME
}
@enduml
```

### 1.6 Diagrama de secuencia (login)

📄 **`docs/uml/03-secuencia-login.puml`**

```plantuml
@startuml 03-secuencia-login
title Secuencia — Login con AJAX (MVT)

actor Usuario
participant "Navegador" as Browser
participant "LoginPageView\n(security/views.py)" as View
participant "Authentication\nBackend" as Auth
participant "Template\nlogin.html" as Template
database "MySQL" as DB

Usuario -> Browser: email y contraseña
Browser -> View: POST /security/login/ (JSON o FormData)
note right: Fetch API con X-CSRFToken

View -> View: detecta content-type\n(JSON vs form)
View -> Auth: authenticate(request, email, password)
Auth -> DB: SELECT * FROM security_user WHERE email=?
DB --> Auth: row (password hash)

alt credenciales válidas + usuario activo
  Auth --> View: user object
  View -> View: login(request, user)
  View --> Browser: 200 {"resp": True, "user": {...}}
  Browser -> Browser: window.location.href = "/"
else usuario inactivo
  View --> Browser: 403 {"resp": False, "error": "Usuario no habilitado"}
else credenciales incorrectas
  View --> Browser: 400 {"resp": False, "error": "Credenciales incorrectas"}
else error interno
  View --> Browser: 500 {"resp": False, "error": "Error interno"}
end
@enduml
```

✅ **Checkpoint:** 4 diagramas renderizan sin errores (Alt+D en VSCode).

---

## 2. Verificación final

```bash
cd "D:/UNEMI/2026/PERIODO-ABRIL-JUNIO/POO/POO-4TO-CURSO-DJANGO-POSTGRES-REACT/backend"
source .venv/Scripts/activate
python manage.py runserver
```

| # | Criterio | ✅ |
|---|---|---|
| 1 | `python manage.py check` sin errores | ☐ |
| 2 | `showmigrations` todo `[X]` | ☐ |
| 3 | Admin en `/admin/` muestra User con foto | ☐ |
| 4 | Login en `/security/login/` con AJAX (email+pass) | ☐ |
| 5 | Login exitoso redirige a `/` (home) | ☐ |
| 6 | Home `/` muestra nombre completo y email | ☐ |
| 7 | Logout redirige a `/security/login/` | ☐ |
| 8 | Sin sesión → al visitar `/` redirige a login | ☐ |
| 9 | Error con credenciales inválidas (JS muestra alerta) | ☐ |
| 10 | Diagramas UML renderizan (Alt+D) | ☐ |

---

## Cierre

| Parte | Resultado |
|---|---|
| [01](./guia-laboratorio-01.md) | Django + MySQL (`config/` settings) |
| [02](./guia-laboratorio-02.md) | Módulo seguridad: User personalizado + login AJAX |
| **03** | Diagramas UML del sistema |

### Siguiente paso

Continúa con la [**Guía 03b — Login Profesional**](./guia-laboratorio-03b.md) para mejorar la interfaz de inicio de sesión con Bootstrap 5, Axios y SOLID.
