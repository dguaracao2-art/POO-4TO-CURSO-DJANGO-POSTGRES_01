# POO-4TO-CURSO-DJANGO-POSTGRES-REACT

Laboratorio de **Programación Orientada a Objetos (4to curso)** — aplicación web con Django + MySQL + Bootstrap 5.

## Stack

| Capa | Tecnología |
|---|---|
| Backend | Django 6.0.6 · django-cors-headers |
| Frontend | Django Templates · Bootstrap 5 · JavaScript ES6 · Axios |
| Base de datos | MySQL 8 / MariaDB 10 (configurable por `.env`) |
| Lenguajes | Python 3.12 |

> **Nota:** El nombre del repositorio incluye "POSTGRES" por razones históricas. El proyecto actual usa MySQL.
| Documentación | PlantUML (diagramas UML) |

## Estructura del repositorio

```
.
├── backend/         # servidor Django
├── frontend/        # (reservado para frontend futuro)
├── docs/
│   ├── ROADMAP.md
│   ├── user-stories.md
│   ├── diseno-facturacion.md
│   ├── guia-laboratorio-01.md
│   ├── guia-laboratorio-02.md
│   ├── guia-laboratorio-03.md
│   ├── guia-laboratorio-03b.md
│   ├── guia-laboratorio-04.md
│   ├── guia-laboratorio-05.md
│   ├── caso-estudio-facturacion-analisis.md
│   ├── caso-estudio-facturacion-implementacion.md
│   ├── referencias-django.md
│   └── uml/         # diagramas PlantUML
└── scripts/         # automatización opcional
```

## Guías de laboratorio

| # | Guía | Estado |
|---|---|---|
| [01](./docs/guia-laboratorio-01.md) | **Configuración base y proyecto Django** | ✅ Implementado |
| [02](./docs/guia-laboratorio-02.md) | **App Security (User, Login, Admin)** | ✅ Implementado |
| [03](./docs/guia-laboratorio-03.md) | **Diagramas UML** | ✅ Implementado |
| [03b](./docs/guia-laboratorio-03b.md) | **Login Profesional (Bootstrap + Axios + SOLID)** | ✅ Implementado |
| [04](./docs/guia-laboratorio-04.md) | **App Core (BaseModel + MenuItem + SoftDelete)** | 📄 Pendiente |
| [05](./docs/guia-laboratorio-05.md) | **Panel Administrativo (Sidebar + Layout + Tags)** | 📄 Pendiente |
| [06](./docs/guia-laboratorio-06.md) | **CRUD Usuarios + Roles (CBVs, búsqueda, paginación)** | 📄 Pendiente |
| [07](./docs/guia-laboratorio-07.md) | **CRUD Catálogo (Categorías + Productos)** | 📄 Pendiente |
| [08](./docs/guia-laboratorio-08.md) | **CRUD Clientes (búsqueda, validación única)** | 📄 Pendiente |
| [09](./docs/guia-laboratorio-09.md) | **Facturación ACID (maestro-detalle, F(), IVA)** | 📄 Pendiente |
| [10](./docs/guia-laboratorio-10.md) | **Dashboard + Reportes (Chart.js)** | 📄 Pendiente |
| [11](./docs/guia-laboratorio-11.md) | **Verificación Final + Despliegue** | 📄 Pendiente |

> Cada guía termina con un *checkpoint*. Solo las marcadas como ✅ están implementadas en el repositorio.

## Documentación del proyecto

- [Roadmap completo](./docs/ROADMAP.md) — Planificación de 12 sprints con 46 User Stories
- [User Stories para Jira](./docs/user-stories.md) — 46 HU con criterios de aceptación formato Given/When/Then
- [Diseño del Módulo de Facturación](./docs/diseno-facturacion.md) — Modelo Maestro-Detalle ACID + UI profesional
- [Referencia del Framework Django](./docs/referencias-django.md) — Companion teórico MVT, ORM, CBVs, POO

## Caso de Estudio — Sistema de Facturación

Aplica **Análisis OO → SOLID → UML → DER → Django → Transacciones ACID** sobre un caso Maestro-Detalle real.

| Parte | Contenido | Duración |
|---|---|---|
| [Análisis y Diseño OO](./docs/caso-estudio-facturacion-analisis.md) | Análisis de dominio, 5 clases, 8 reglas de negocio, SOLID, UML, ER | 1 – 1.5 h |
| [Implementación Django](./docs/caso-estudio-facturacion-implementacion.md) | Modelos, servicios transaccionales, ViewSets, API, pruebas | 1.5 – 2 h |

## Requisitos

- Windows 10/11 con PowerShell 5.1+
- Python 3.12 (`python --version`)
- MySQL 8 / MariaDB 10
- Git, Visual Studio Code (extensiones: *Python*, *Pylance*, *PlantUML*)

> ¿Falta alguna herramienta? La guía 01 incluye los comandos `winget` para instalar todo lo necesario en Windows.
