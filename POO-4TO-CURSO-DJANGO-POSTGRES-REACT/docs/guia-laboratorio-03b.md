# Guía de Laboratorio 03b — Login Profesional con Bootstrap 5 + Axios + SOLID

## Objetivo

Mejorar la experiencia de inicio de sesión del sistema aplicando principios de **diseño UI/UX profesional**, **accesibilidad web (WCAG)**, **JavaScript modular con Axios** y **principios SOLID en la capa frontend**.

## Duración estimada

2 horas (presencial) + 1 hora (trabajo autónomo)

## Prerrequisitos

- Laboratorio 03 completado (login funcional con Django + Bootstrap básico)
- Python 3.12, Django 6.0.6, MySQL configurado
- Superusuario creado y funcional

## Resultado al finalizar

- Pantalla de login profesional dividida (formulario derecha + branding izquierda)
- Código JavaScript organizado en 3 clases con responsabilidades únicas (SOLID)
- Peticiones asíncronas vía Axios
- Validación de formulario con feedback visual
- Accesibilidad: ARIA labels, roles, focus management
- HTML y JavaScript en archivos separados

---

## Contenido

1. [Estructura final del proyecto](#estructura-final-del-proyecto)
2. [Fase 1 — Crear la estructura de archivos estáticos](#fase-1--crear-la-estructura-de-archivos-estáticos)
3. [Fase 2 — Crear el CSS del Login](#fase-2--crear-el-css-del-login-logincss)
4. [Fase 3 — Crear el CSS global del sistema](#fase-3--crear-el-css-global-del-sistema-appcss)
5. [Fase 4 — Capa HTTP con Axios (api-client.js)](#fase-4--crear-la-capa-http-con-axios-api-clientjs--principio-srp)
6. [Fase 5 — Servicio de Autenticación (auth-service.js)](#fase-5--crear-el-servicio-de-autenticación-auth-servicejs--principio-srp--dip)
7. [Fase 6 — Controlador de Login (login.js)](#fase-6--crear-el-controlador-de-login-loginjs--principio-srp--dip)
8. [Fase 7 — Template Login](#fase-7--rediseñar-el-template-de-login-loginhtml)
9. [Fase 8 — Template Base](#fase-8--actualizar-el-template-base-basehtml)
10. [Fase 9 — Página de Inicio](#fase-9--actualizar-la-página-de-inicio-indexhtml)
11. [Fase 10 — Token CSRF](#fase-10--verificar-el-token-csrf-en-la-vista-de-login)
12. [Fase 11 — Archivos estáticos](#fase-11--verificar-que-django-encuentra-los-archivos-estáticos)
13. [Fase 12 — Probar servidor](#fase-12--probar-el-servidor)
14. [Resumen SOLID](#resumen-de-principios-solid-aplicados)
15. [Errores comunes](#posibles-errores-y-soluciones)
16. [Apéndice — Skeleton Loading](#apéndice--skeleton-loading-system)

---

## Estructura final del proyecto

```
backend/
├── security/
│   ├── static/
│   │   └── security/
│   │       ├── css/
│   │       │   ├── login.css        (NUEVO) — estilos del login
│   │       │   └── app.css          (NUEVO) — estilos generales
│   │       └── js/
│   │           ├── api-client.js    (NUEVO) — wrapper de Axios
│   │           ├── auth-service.js  (NUEVO) — lógica autenticación
│   │           └── login.js         (NUEVO) — controlador login
│   └── templates/
│       └── security/
│           └── login.html           (MODIFICADO)
├── templates/
│   ├── base.html                    (MODIFICADO)
│   └── index.html                   (MODIFICADO)
```

---

## Fase 1 — Crear la estructura de archivos estáticos

**Paso 1.1:** Abre una terminal en la carpeta `backend/` y activa el entorno virtual:

```bash
cd backend
.venv\Scripts\activate      # Windows PowerShell
source .venv/bin/activate    # Linux/Mac
```

**Paso 1.2:** Crea las carpetas para los archivos estáticos de la app `security`:

```bash
mkdir -p security/static/security/css
mkdir -p security/static/security/js
```

**Paso 1.3:** Verifica que las carpetas se crearon:

```bash
ls -R security/static/
```

Debes ver:
```
security/static/security/:
css/  js/

security/static/security/css/:
(vacío)

security/static/security/js/:
(vacío)
```

---

## Fase 2 — Crear el CSS del Login (login.css)

**Paso 2.1:** Crea el archivo `security/static/security/css/login.css`:

```css
:root {
  --brand-start: #4e73df;
  --brand-end: #224abe;
  --brand-light: #f8f9fc;
}

html, body {
  height: 100%;
  overflow: hidden;
}

body {
  font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  background: var(--brand-light);
}

.login-form-col {
  background: #fff;
  padding: 2rem;
  overflow-y: auto;
}

.login-card {
  width: 100%;
  max-width: 400px;
}

.brand-icon {
  width: 72px;
  height: 72px;
  margin: 0 auto;
  background: linear-gradient(135deg, var(--brand-start), var(--brand-end));
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.branding-col {
  background: linear-gradient(135deg, var(--brand-start) 0%, var(--brand-end) 100%);
  position: relative;
  overflow: hidden;
}

.branding-col::before {
  content: '';
  position: absolute;
  inset: -50%;
  background: radial-gradient(circle, rgba(255,255,255,.06) 0%, transparent 70%);
  animation: float 12s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(5%, -5%) scale(1.05); }
  66% { transform: translate(-5%, 5%) scale(0.95); }
}

.branding-content {
  position: relative;
  z-index: 1;
}

.branding-icon-box {
  width: 100px;
  height: 100px;
  margin: 0 auto;
  background: rgba(255,255,255,.12);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(8px);
}

.feature-item {
  font-size: 1.05rem;
  opacity: .85;
  margin: .5rem 0;
}

.form-control-lg:focus {
  border-color: var(--brand-start);
  box-shadow: 0 0 0 .2rem rgba(78, 115, 223, .15);
}

.btn-login {
  background: linear-gradient(135deg, var(--brand-start), var(--brand-end));
  border: none;
  padding: .75rem 1.5rem;
  font-weight: 600;
  transition: all .25s ease;
}

.btn-login:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(78, 115, 223, .4);
}

.btn-login:disabled {
  opacity: .65;
  cursor: not-allowed;
}

:focus-visible {
  outline: 2px solid var(--brand-start);
  outline-offset: 2px;
}

@media (max-width: 991.98px) {
  .login-form-col { padding: 1.5rem; }
  .login-card { max-width: 100%; }
}
```

**Explicación línea por línea:**

| Líneas | ¿Qué hace? |
|--------|------------|
| `:root` | Define variables CSS reutilizables (colores del gradiente) |
| `html, body` | Altura 100% del viewport, sin scroll |
| `.login-form-col` | Fondo blanco, padding, scroll si el contenido es muy alto |
| `.login-card` | Ancho máximo 400px, centrado |
| `.brand-icon` | Círculo con gradiente para el logo |
| `.branding-col` | Gradiente azul de fondo, posición relativa para el pseudo-elemento |
| `.branding-col::before` | Círculo decorativo animado con `radial-gradient` |
| `@keyframes float` | Animación suave de 12s que se mueve y escala |
| `.branding-icon-box` | Caja traslúcida con `backdrop-filter` para el icono grande |
| `.btn-login` | Botón con gradiente que se eleva al hacer hover |
| `:focus-visible` | Outline azul solo cuando se navega con teclado (no con mouse) |
| `@media` | Ajustes para pantallas menores a 992px |

---

## Fase 3 — Crear el CSS global del sistema (app.css)

**Paso 3.1:** Crea el archivo `security/static/security/css/app.css`:

```css
:root {
  --sidebar-width: 250px;
}

body {
  background: #f8f9fc;
  font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
}

.card {
  border-radius: 10px;
  transition: box-shadow .2s ease;
}

.card:hover {
  box-shadow: 0 .5rem 1rem rgba(0,0,0,.08);
}

.navbar-brand {
  letter-spacing: -.5px;
}

main {
  min-height: calc(100vh - 76px);
}

:focus-visible {
  outline: 2px solid #4e73df;
  outline-offset: 2px;
}
```

**¿Por qué necesitamos este archivo?** Porque los estilos del login son exclusivos para la página de inicio de sesión. Una vez que el usuario ingresa al sistema, las demás páginas usan `app.css`. Esto separa responsabilidades (SRP) incluso en CSS.

---

## Fase 4 — Crear la capa HTTP con Axios (api-client.js) — Principio SRP

**Paso 4.1:** Crea el archivo `security/static/security/js/api-client.js`:

```javascript
class ApiClient {
  constructor(config = {}) {
    this.client = axios.create({
      baseURL: config.baseURL || '',
      timeout: config.timeout || 15000,
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': this._getCsrfToken(),
      },
    });
    this._setupInterceptors();
  }

  _getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) return meta.getAttribute('content');
    const cookie = this._getCookie('csrftoken');
    return cookie || '';
  }

  _getCookie(name) {
    const match = document.cookie.match(new RegExp('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)'));
    return match ? decodeURIComponent(match[2]) : null;
  }

  _setupInterceptors() {
    this.client.interceptors.response.use(
      (res) => res,
      (err) => {
        const msg = err.response?.data?.error
          || err.response?.data?.detail
          || 'Error de conexión con el servidor';
        return Promise.reject(new Error(msg));
      }
    );
  }

  async post(url, data) {
    const res = await this.client.post(url, data);
    return res.data;
  }

  async get(url, params = {}) {
    const res = await this.client.get(url, { params });
    return res.data;
  }
}
```

**¿Qué hace cada método?**

| Método | Responsabilidad |
|--------|-----------------|
| `constructor(config)` | Crea una instancia de Axios con configuración base (URL, timeout, headers) |
| `_getCsrfToken()` | Obtiene el token CSRF desde un `<meta>` tag o desde la cookie |
| `_getCookie(name)` | Lee una cookie del navegador por su nombre |
| `_setupInterceptors()` | Configura un interceptor que convierte errores HTTP en mensajes legibles |
| `post(url, data)` | Envía petición POST y retorna solo los datos (`response.data`) |
| `get(url, params)` | Envía petición GET con parámetros y retorna solo los datos |

**¿Por qué SRP?** Esta clase tiene **una sola responsabilidad**: gestionar la comunicación HTTP. Si en el futuro cambiamos de Axios a `fetch`, solo modificamos esta clase. El resto del sistema no se entera.

---

## Fase 5 — Crear el Servicio de Autenticación (auth-service.js) — Principio SRP + DIP

**Paso 5.1:** Crea el archivo `security/static/security/js/auth-service.js`:

```javascript
class AuthService {
  constructor(apiClient) {
    this.api = apiClient;
  }

  async login(email, password) {
    return this.api.post('/security/login/', {
      username: email,
      password: password,
    });
  }

  async logout() {
    return this.api.post('/security/logout/');
  }
}
```

**¿Por qué SRP?** Esta clase tiene **una sola responsabilidad**: encapsular la lógica de autenticación. Sabe qué datos enviar al login, pero no sabe cómo se envía la petición HTTP.

**¿Por qué DIP (Inversión de Dependencias)?** La clase `AuthService` no crea su propio cliente HTTP. Recibe `apiClient` por el constructor (inyección de dependencia). Esto permite:
- Probar `AuthService` con un cliente mock en lugar de Axios real
- Cambiar la implementación del cliente sin modificar `AuthService`

---

## Fase 6 — Crear el Controlador de Login (login.js) — Principio SRP + DIP

**Paso 6.1:** Crea el archivo `security/static/security/js/login.js`:

```javascript
(function () {
  const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  const api = new ApiClient();
  const auth = new AuthService(api);

  const els = {
    form: document.getElementById('loginForm'),
    email: document.getElementById('loginEmail'),
    password: document.getElementById('loginPassword'),
    submit: document.getElementById('loginSubmit'),
    error: document.getElementById('loginError'),
    toggle: document.getElementById('passwordToggle'),
  };

  function showError(msg) {
    els.error.textContent = msg;
    els.error.classList.remove('d-none');
    els.error.setAttribute('role', 'alert');
  }

  function clearError() {
    els.error.classList.add('d-none');
    els.error.textContent = '';
  }

  function setLoading(loading) {
    els.submit.disabled = loading;
    els.submit.innerHTML = loading
      ? '<span class="spinner-border spinner-border-sm me-2"></span>Ingresando...'
      : '<i class="bi bi-box-arrow-in-right me-2"></i>Iniciar sesi\u00f3n';
  }

  function validate() {
    const email = els.email.value.trim();
    const password = els.password.value;

    if (!email) { showError('El correo electr\u00f3nico es requerido'); els.email.focus(); return false; }
    if (!EMAIL_REGEX.test(email)) { showError('Ingrese un correo electr\u00f3nico v\u00e1lido'); els.email.focus(); return false; }
    if (!password) { showError('La contrase\u00f1a es requerida'); els.password.focus(); return false; }
    if (password.length < 4) { showError('La contrase\u00f1a debe tener al menos 4 caracteres'); els.password.focus(); return false; }
    return true;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    clearError();
    if (!validate()) return;

    setLoading(true);
    try {
      const result = await auth.login(els.email.value.trim(), els.password.value);
      if (result.resp) {
        window.location.href = '/';
      } else {
        showError(result.error || 'Credenciales incorrectas');
      }
    } catch (err) {
      showError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function togglePassword() {
    const isPassword = els.password.type === 'password';
    els.password.type = isPassword ? 'text' : 'password';
    const icon = els.toggle.querySelector('i');
    icon.classList.toggle('bi-eye');
    icon.classList.toggle('bi-eye-slash');
  }

  els.form.addEventListener('submit', handleSubmit);
  els.toggle.addEventListener('click', togglePassword);
  els.email.addEventListener('input', clearError);
  els.password.addEventListener('input', clearError);

  els.email.focus();
})();
```

**¿Qué hace cada función?**

| Función | Responsabilidad |
|---------|-----------------|
| `showError(msg)` | Muestra el mensaje de error y agrega `role="alert"` para accesibilidad |
| `clearError()` | Oculta el mensaje de error |
| `setLoading(loading)` | Deshabilita el botón, muestra spinner o restaura texto |
| `validate()` | Valida email y contraseña, retorna `true/false` |
| `handleSubmit(e)` | Orquesta el flujo: valida → llama a AuthService → redirige o muestra error |
| `togglePassword()` | Alterna entre mostrar/ocultar contraseña |

**¿Por qué IIFE `(function () { ... })()`?**

- Evita contaminar el ámbito global (`window`)
- Las variables como `api`, `auth`, `els` no son accesibles desde la consola del navegador
- Es un patrón estándar para encapsular código

---

## Fase 7 — Rediseñar el Template de Login (login.html)

**Paso 7.1:** Abre el archivo `security/templates/security/login.html` y **reemplaza TODO su contenido** con el siguiente código:

```html
{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="csrf-token" content="{{ csrf_token }}">
  <title>Iniciar sesión — Sistema de Facturación</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css" rel="stylesheet">
  <link href="{% static 'security/css/login.css' %}" rel="stylesheet">
</head>
<body>
  <div class="container-fluid vh-100 overflow-hidden p-0">
    <div class="row vh-100 g-0">
      <!-- COLUMNA IZQUIERDA: Branding (visible solo en desktop) -->
      <div class="col-lg-7 d-none d-lg-flex flex-column align-items-center justify-content-center branding-col">
        <div class="branding-content text-center text-white px-4">
          <div class="branding-icon-box mb-4" aria-hidden="true">
            <i class="bi bi-receipt-cutoff display-3"></i>
          </div>
          <h2 class="fw-bold mb-3">Gestión de Facturación</h2>
          <p class="lead mb-4 opacity-75">
            Administre sus ventas, productos y clientes<br>
            de manera eficiente y profesional.
          </p>
          <div class="text-start d-inline-block">
            <div class="feature-item"><i class="bi bi-check-circle-fill me-2"></i>Control de inventario</div>
            <div class="feature-item"><i class="bi bi-check-circle-fill me-2"></i>Facturación electrónica</div>
            <div class="feature-item"><i class="bi bi-check-circle-fill me-2"></i>Reportes en tiempo real</div>
          </div>
        </div>
      </div>

      <!-- COLUMNA DERECHA: Formulario de login -->
      <div class="col-12 col-lg-5 d-flex align-items-center justify-content-center login-form-col">
        <div class="login-card">
          <div class="text-center mb-4">
            <div class="brand-icon mb-3" aria-hidden="true">
              <i class="bi bi-receipt-cutoff fs-1"></i>
            </div>
            <h1 class="h3 fw-bold mb-1">Sistema de Facturación</h1>
            <p class="text-muted small">Ingrese sus credenciales para continuar</p>
          </div>

          <!-- Mensaje de error -->
          <div id="loginError" class="alert alert-danger d-none" role="alert" aria-live="assertive"></div>

          <!-- Formulario -->
          <form id="loginForm" novalidate aria-label="Formulario de inicio de sesión">
            <div class="mb-3">
              <label for="loginEmail" class="form-label fw-semibold">Correo electrónico</label>
              <div class="input-group">
                <span class="input-group-text" aria-hidden="true"><i class="bi bi-envelope"></i></span>
                <input type="email"
                       id="loginEmail"
                       name="username"
                       class="form-control form-control-lg"
                       placeholder="ejemplo@correo.com"
                       required
                       autocomplete="email"
                       aria-describedby="emailHelp">
              </div>
              <div id="emailHelp" class="form-text">Ingrese el correo registrado en el sistema.</div>
            </div>

            <div class="mb-4">
              <div class="d-flex justify-content-between align-items-center">
                <label for="loginPassword" class="form-label fw-semibold mb-0">Contraseña</label>
                <a href="#" class="text-decoration-none small" tabindex="-1"
                   aria-label="Recuperar contraseña">¿Olvidó su contraseña?</a>
              </div>
              <div class="input-group">
                <span class="input-group-text" aria-hidden="true"><i class="bi bi-lock"></i></span>
                <input type="password"
                       id="loginPassword"
                       name="password"
                       class="form-control form-control-lg"
                       placeholder="••••••••"
                       required
                       autocomplete="current-password"
                       minlength="4">
                <button type="button"
                        id="passwordToggle"
                        class="input-group-text"
                        aria-label="Mostrar u ocultar contraseña"
                        tabindex="-1">
                  <i class="bi bi-eye"></i>
                </button>
              </div>
            </div>

            <div class="mb-4 form-check">
              <input type="checkbox" class="form-check-input" id="rememberMe">
              <label class="form-check-label" for="rememberMe">Recordarme</label>
            </div>

            <button type="submit"
                    id="loginSubmit"
                    class="btn btn-primary btn-lg w-100 btn-login">
              <i class="bi bi-box-arrow-in-right me-2"></i>Iniciar sesión
            </button>
          </form>

          <p class="text-center text-muted mt-4 mb-0 small">
            © {% now "Y" %} Sistema de Facturación. Todos los derechos reservados.
          </p>
        </div>
      </div>
    </div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
  <script src="{% static 'security/js/api-client.js' %}"></script>
  <script src="{% static 'security/js/auth-service.js' %}"></script>
  <script src="{% static 'security/js/login.js' %}"></script>
</body>
</html>
```

**¿Qué cambió respecto al login anterior?**

| Cambio | Antes (Lab 03) | Ahora (Lab 03b) |
|--------|----------------|-----------------|
| Layout | Una columna centrada | Split-screen (branding izq + formulario der) |
| Template | Extendía `base.html` | Standalone (sin navbar) |
| CSS | Bootstrap default + inline | CSS personalizado separado |
| JS | Inline en el HTML (`<script>` directo) | 3 archivos separados con clases |
| HTTP | `fetch` API nativa | Axios con interceptors |
| CSRF | `{{ csrf_token }}` en form + header manual | Meta tag + header automático |
| Validación | Solo HTML5 | HTML5 + JS con mensajes |
| Accesibilidad | Mínima | ARIA labels, roles, focus-visible |

---

## Fase 8 — Actualizar el Template Base (base.html)

**Paso 8.1:** Abre el archivo `templates/base.html` y **reemplaza TODO su contenido**:

```html
{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}App{% endblock %}</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css" rel="stylesheet">
  <link href="{% static 'security/css/app.css' %}" rel="stylesheet">
  {% block extra_head %}{% endblock %}
</head>
<body>
  {% if user.is_authenticated %}
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark shadow-sm">
    <div class="container-fluid px-4">
      <a class="navbar-brand fw-bold" href="{% url 'home' %}">
        <i class="bi bi-receipt-cutoff me-2"></i>SIF
      </a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav me-auto">
          <li class="nav-item">
            <a class="nav-link" href="{% url 'home' %}"><i class="bi bi-house me-1"></i>Inicio</a>
          </li>
        </ul>
        <div class="d-flex align-items-center">
          <span class="text-light me-3 small">
            <i class="bi bi-person-circle me-1"></i>
            {{ user.get_full_name|default:user.email }}
          </span>
          <form method="post" action="{% url 'security:logout' %}" class="d-inline">
            {% csrf_token %}
            <button type="submit" class="btn btn-outline-light btn-sm">
              <i class="bi bi-box-arrow-right me-1"></i>Salir
            </button>
          </form>
        </div>
      </div>
    </div>
  </nav>
  {% endif %}

  <main class="{% if user.is_authenticated %}container-fluid px-4 py-4{% endif %}">
    {% block content %}{% endblock %}
  </main>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
  {% block extra_scripts %}{% endblock %}
</body>
</html>
```

**Cambios importantes:**

1. **`{% load static %}`** ahora está en base.html para que todas las plantillas hijas puedan usar `{% static %}` sin repetir
2. **Bootstrap Icons** CDN agregado para usar iconos como `bi-person-circle`, `bi-house`, etc.
3. **`app.css`** vinculado para estilos globales
4. **Navbar** más profesional con:
   - Marca "SIF" con icono de factura
   - Nombre de usuario con icono de persona
   - Botón "Salir" con estilo outline y icono
5. **Barra de navegación solo visible** cuando `user.is_authenticated` es `True`
6. **`main`** usa `container-fluid px-4 py-4` solo cuando hay sesión activa
7. **Blocks** `extra_head` y `extra_scripts` para que las plantillas hijas puedan agregar recursos adicionales

---

## Fase 9 — Actualizar la página de Inicio (index.html)

**Paso 9.1:** Abre el archivo `templates/index.html` y **reemplaza TODO su contenido**:

```html
{% extends "base.html" %}
{% load static %}
{% block title %}Inicio{% endblock %}
{% block content %}
<div class="row">
  <div class="col-12">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="h3 mb-0"><i class="bi bi-house-door me-2"></i>Panel Principal</h1>
      <span class="text-muted small"><i class="bi bi-calendar me-1"></i>{% now "d/m/Y" %}</span>
    </div>

    <div class="row g-4">
      <div class="col-12 col-lg-6">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body text-center p-5">
            <div class="display-6 mb-3">
              <i class="bi bi-person-circle text-primary"></i>
            </div>
            <h2 class="h4 fw-bold">Bienvenido, {{ user.first_name|default:user.username }}</h2>
            <p class="text-muted mb-1">{{ user.email }}</p>
            <p class="text-muted small mb-0">
              Último acceso: {{ user.last_login|date:"d/m/Y H:i"|default:"Primer ingreso" }}
            </p>
          </div>
        </div>
      </div>

      <div class="col-12 col-lg-6">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body text-center p-5">
            <div class="display-6 mb-3">
              <i class="bi bi-grid text-success"></i>
            </div>
            <h3 class="h5 fw-bold">Módulos Disponibles</h3>
            <p class="text-muted small mb-0">
              Los módulos de facturación estarán disponibles próximamente.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
{% endblock %}
```

**¿Qué mejoró?**

| Elemento | Antes | Ahora |
|----------|-------|-------|
| Título | "Bienvenido, Nombre" | "Panel Principal" + fecha actual |
| Tarjeta bienvenida | Sin tarjeta, solo texto | Card con icono, sombra, nombre, email, último acceso |
| Placeholder módulos | No existía | Card "Módulos Disponibles" para próximos labs |
| Diseño | Texto centrado simple | Grilla responsive con 2 columnas en lg |

---

## Fase 10 — Verificar el Token CSRF en la Vista de Login

**Paso 10.1:** Abre el archivo `security/views.py`. No necesita cambios, pero verifica que el método `post` maneje correctamente JSON (Axios envía JSON automáticamente):

```python
# security/views.py (NO MODIFICAR, solo verificar)
class LoginPageView(TemplateView):
    template_name = "security/login.html"
    http_method_names = ["get", "post"]

    def post(self, request, *args, **kwargs):
        # Si Axios envía JSON, request.content_type == "application/json"
        # Django procesa el cuerpo con json.loads()
```

**¿Cómo funciona el CSRF con Axios?**

1. El template genera: `<meta name="csrf-token" content="abc123...">`
2. `api-client.js` lee el token con `_getCsrfToken()`
3. Axios envía el token en el header `X-CSRFToken: abc123...`
4. Django CSRF middleware verifica el header y permite la petición

---

## Fase 11 — Verificar que Django encuentra los archivos estáticos

**Paso 11.1:** En la terminal (con el entorno virtual activado), ejecuta:

```bash
python manage.py findstatic security/css/login.css
```

Deberías ver:
```
Found 'security/css/login.css' here:
  ...\backend\security\static\security\css\login.css
```

**Paso 11.2:** Verifica que todos los archivos sean encontrados:

```bash
python manage.py findstatic security/css/login.css security/css/app.css security/js/api-client.js security/js/auth-service.js security/js/login.js
```

Todos deben mostrar la ruta completa. Si alguno falla, revisa que el archivo existe en la carpeta correcta.

---

## Fase 12 — Probar el Servidor

**Paso 12.1:** Inicia el servidor MySQL (XAMPP, WAMP, o el servicio correspondiente).

**Paso 12.2:** En la terminal, inicia Django:

```bash
python manage.py runserver
```

**Paso 12.3:** Abre el navegador en `http://localhost:8000/`

**Paso 12.4:** Sigue esta lista de verificación:

| # | Prueba | Resultado esperado |
|---|--------|-------------------|
| 1 | Abrir `localhost:8000` | Redirige a `/security/login/` |
| 2 | Pantalla ≥ 992px | Split-screen: branding izquierda (gradiente azul) + formulario derecha (fondo blanco) |
| 3 | Redimensionar a < 992px | Branding desaparece, formulario ocupa todo el ancho |
| 4 | Hacer clic en "Iniciar sesión" sin llenar campos | Aparece error: "El correo electrónico es requerido" |
| 5 | Escribir "correo-invalido" y enviar | Aparece error: "Ingrese un correo electrónico válido" |
| 6 | Escribir email correcto, contraseña corta (123) | Aparece error: "La contraseña debe tener al menos 4 caracteres" |
| 7 | Ingresar credenciales incorrectas | Aparece error: "Credenciales incorrectas" (del servidor) |
| 8 | Ingresar credenciales correctas | Redirige a `/` con el dashboard de bienvenida |
| 9 | Ver el navbar en el home | Barra oscura con "SIF", nombre de usuario, botón "Salir" |
| 10 | Hacer clic en "Salir" | Cierra sesión y redirige al login |
| 11 | Presionar Tab varias veces | El foco se mueve entre campos y el outline azul es visible |
| 12 | Hacer clic en el icono del ojo en contraseña | Muestra/oculta la contraseña |

---

## Resumen de principios SOLID aplicados

```
┌──────────────────────────────────────────────────────────┐
│                    login.html                             │
│  (Solo HTML + carga de scripts)                          │
├──────────────────────────────────────────────────────────┤
│  login.js ──── SRP: Orquestar DOM y eventos              │
│  │                                                       │
│  │  Depende de → AuthService (inyectado)                 │
│  ▼                                                       │
│  auth-service.js ──── SRP: Lógica de autenticación       │
│  │                                                       │
│  │  Depende de → ApiClient (inyectado)                   │
│  ▼                                                       │
│  api-client.js ──── SRP: Comunicación HTTP               │
│  │              OCP: Extensible por configuración         │
│  │              LSP: Interfaz consistente (post/get)      │
│  ▼                                                       │
│  Axios (librería externa, inyectable)                    │
└──────────────────────────────────────────────────────────┘
```

| Principio | Aplicación |
|-----------|------------|
| **SRP** | `ApiClient` → solo HTTP; `AuthService` → solo auth; `login.js` → solo DOM |
| **OCP** | `ApiClient` acepta `config` para extender sin modificar su clase |
| **LSP** | Todos los servicios retornan promesas con la misma estructura `{resp, user, error}` |
| **ISP** | `AuthService` expone solo `login()` y `logout()`, nada más |
| **DIP** | Las clases de alto nivel (`login.js`, `AuthService`) dependen de abstracciones inyectadas, no de implementaciones concretas |

---

## Posibles errores y soluciones

| Error | Causa | Solución |
|-------|-------|----------|
| `ModuleNotFoundError: No module named 'django'` | Entorno virtual no activado | Ejecuta `.venv\Scripts\activate` |
| `OperationalError: (2002, "Can't connect to server on 'localhost'")` | MySQL no está corriendo | Inicia XAMPP/WAMP o el servicio MySQL |
| El login no redirige, solo recarga la página | El JS no se cargó correctamente | Abre Consola del navegador (F12) y revisa errores |
| `403 Forbidden` al enviar login | Token CSRF incorrecto | Verifica que `<meta name="csrf-token">` existe en el HTML |
| Los estilos CSS no se ven | Static files no encontrados | Ejecuta `python manage.py findstatic security/css/login.css` |
| El branding se ve en mobile | La clase `d-none d-lg-flex` no está aplicada | Revisa que `d-none` esté en la columna del branding |

---

## Apéndice — Skeleton Loading System

Sistema de loading visual (skeleton) general y reutilizable para todas las vistas del proyecto. Sin librerías externas, solo CSS.

### Clases disponibles

| Clase | Para | Ejemplo |
|-------|------|---------|
| `.skeleton` | Genérica: cualquier elemento | `<div class="skeleton" style="width:200px;height:40px">` |
| `.skeleton-text` | Texto: párrafos | `<p class="skeleton skeleton-text"></p>` |
| `.skeleton-text-sm` | Texto corto | `<span class="skeleton skeleton-text-sm"></span>` |
| `.skeleton-heading` | Títulos | `<h3 class="skeleton skeleton-heading"></h3>` |
| `.skeleton-card` | Tarjetas placeholder | `<div class="skeleton skeleton-card"></div>` |
| `.skeleton-avatar` | Avatares o fotos | `<div class="skeleton skeleton-avatar"></div>` |
| `.skeleton-thumb` | Miniaturas | `<span class="skeleton skeleton-thumb"></span>` |
| `.skeleton-input` | Inputs/Selects | `<input class="form-control skeleton-input" disabled>` |
| `.skeleton-btn` | Botones | `<button class="btn btn-primary skeleton-btn" disabled>Guardar</button>` |

### Cómo usar

**Paso 1:** El CSS ya está en `app.css`. Se aplica globalmente.

**Paso 2:** En cualquier template, agrega `.skeleton` al elemento mientras carga:

```html
<!-- Antes de cargar datos -->
<div class="card">
  <div class="card-body">
    <h5 class="skeleton skeleton-heading"></h5>
    <p class="skeleton skeleton-text"></p>
    <p class="skeleton skeleton-text-sm"></p>
  </div>
</div>

<!-- Input en estado loading -->
<input class="form-control skeleton-input" disabled placeholder="Cargando...">

<!-- Botón procesando -->
<button class="btn btn-primary skeleton-btn" disabled>Guardar</button>

<!-- Tabla cargando datos -->
<tr class="skeleton-row">
  <td></td><td></td><td></td>
</tr>
```

**Paso 3:** Con JavaScript, intercambia clases al completar la carga:

```javascript
// Mostrar skeleton mientras se carga
card.classList.add('skeleton');

// Ocultar skeleton al cargar
fetch('/api/data/')
  .then(r => r.json())
  .then(data => {
    card.classList.remove('skeleton');
    renderData(data);
  });
```

### Efecto visual

```
┌──────────────────────────────────────┐
│  ░░░░░░░░  (skeleton-heading)        │
│  ░░░░░░░░░░░░░░░░░░░░░░░░  (text)   │
│  ░░░░░░░░░░░░              (text-sm) │
│                                      │
│  ┌────────────────────────┐          │
│  │ ░░░░░░░░░░░░░░░░░░░░░░ │ (input) │
│  └────────────────────────┘          │
│            ┌─────────┐              │
│            │ ░░░░░░░░ │ (button)    │
│            └─────────┘              │
└──────────────────────────────────────┘
```

El CSS usa `shimmer` (destello móvil) como animación. Sin JavaScript, sin dependencias.

---

## Próximo laboratorio

[**Laboratorio 04 — App Core: BaseModel + MenuItem + SoftDelete**](./guia-laboratorio-04.md)

Crearemos la app `core` con `BaseModel`, `SoftDeleteManager`, el modelo `MenuItem` auto-referencial con permisos, seed data y admin.

---

## Referencias

- [Bootstrap 5 Docs — Forms](https://getbootstrap.com/docs/5.3/forms/overview/)
- [Bootstrap Icons](https://icons.getbootstrap.com/)
- [Axios Docs](https://axios-http.com/docs/intro)
- [MDN — ARIA](https://developer.mozilla.org/es/docs/Web/Accessibility/ARIA)
- [Principios SOLID — Robert C. Martin](https://en.wikipedia.org/wiki/SOLID)
- [Django — Managing static files](https://docs.djangoproject.com/en/6.0/howto/static-files/)
- [Django — CSRF](https://docs.djangoproject.com/en/6.0/ref/csrf/)
