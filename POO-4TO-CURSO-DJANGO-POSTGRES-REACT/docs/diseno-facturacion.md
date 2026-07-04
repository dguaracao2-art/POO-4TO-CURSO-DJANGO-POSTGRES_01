# Diseño del Módulo de Facturación — Maestro-Detalle ACID

## 1. Modelo de Datos (Maestro-Detalle)

```
┌─────────────────────────────────────────────────────────────┐
│                        Factura (Maestro)                      │
├─────────────────────────────────────────────────────────────┤
│ id (PK, BigAutoField)                                        │
│ numero (CharField 20, unique, editable=False)                │
│   → Formato: "FAC-YYYYMMDD-XXXXX"                           │
│ fecha_emision (DateTimeField, default=timezone.now)          │
│ cliente (FK → Cliente, on_delete=PROTECT)                    │
│ usuario (FK → User, on_delete=PROTECT)                       │
│ subtotal (DecimalField 12,2)                                 │
│ iva_total (DecimalField 12,2)                                │
│ total (DecimalField 12,2)                                    │
│ metodo_pago (CharField 50, default='Efectivo')               │
│   → Choices: Efectivo, Tarjeta Débito, Tarjeta Crédito,     │
│              Transferencia, Crédito                          │
│ observaciones (TextField, blank=True)                        │
│ created_at | updated_at | deleted_at | is_active             │
└──────────────────────┬──────────────────────────────────────┘
                       │ 1
                       │
                       │ * (CASCADE)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   DetalleFactura (Detalle)                    │
├─────────────────────────────────────────────────────────────┤
│ id (PK, BigAutoField)                                        │
│ factura (FK → Factura, related_name='detalles')              │
│ producto (FK → Producto, on_delete=PROTECT)                  │
│ cantidad (IntegerField)                                      │
│ precio_unitario (DecimalField 10,2)                           │
│ descuento_pct (DecimalField 5,2, default=0)                  │
│   → % de descuento aplicado a este ítem                      │
│ subtotal (DecimalField 12,2)                                 │
│   → cantidad * precio_unitario * (1 - descuento_pct/100)    │
│ iva_porcentaje (DecimalField 4,2)                            │
│   → % de IVA del producto al momento de la venta             │
│ iva_valor (DecimalField 12,2)                                │
│   → subtotal * iva_porcentaje / 100                          │
│ total (DecimalField 12,2)                                    │
│   → subtotal + iva_valor                                     │
│ created_at | updated_at | deleted_at | is_active             │
└─────────────────────────────────────────────────────────────┘
```

### 1.1 Reglas de negocio (R1-R6)

| # | Regla | Descripción |
|---|-------|-------------|
| R1 | **Número secuencial** | Cada factura tiene un número único generado automáticamente con formato `FAC-YYYYMMDD-XXXXX` |
| R2 | **Stock suficiente** | Al agregar un producto, la cantidad no puede superar el stock actual |
| R3 | **Descuento atómico** | Al guardar la factura, el stock se descuenta usando `F()` para evitar condiciones de carrera |
| R4 | **Cálculo automático** | Subtotal, IVA y total se calculan en el backend, no en el frontend |
| R5 | **Transacción completa** | Si algo falla (stock insuficiente, error de BD), TODO se revierte (rollback) |
| R6 | **Anulación con restauración** | Al anular, el stock se restaura atómicamente y la factura se marca como inactiva |

### 1.2 Cálculos

```
SubtotalDetalle  = cantidad × precio_unitario × (1 - descuento_pct / 100)
IVADetalle       = SubtotalDetalle × iva_porcentaje / 100
TotalDetalle     = SubtotalDetalle + IVADetalle

SubtotalFactura  = SUM(SubtotalDetalle)
IVAFactura       = SUM(IVADetalle)
TotalFactura     = SubtotalFactura + IVAFactura
```

### 1.3 Justificación de atributos (vs diseño minimalista)

| Atributo | ¿Por qué es necesario en facturación real? |
|----------|-------------------------------------------|
| `precio_unitario` | Se almacena en el detalle, NO se lee del producto actual. El precio puede cambiar después de la venta. |
| `iva_porcentaje` | Se almacena por detalle. Productos pueden tener diferentes % de IVA (0%, 15%, exentos). |
| `descuento_pct` | Descuento por línea de producto, no solo global. Real en facturación ecuatoriana. |
| `subtotal`, `iva_valor`, `total` | Se almacenan calculados para auditoría SRI y reportes históricos. No se recalcula sobre precios actuales. |
| `numero` | Obligatorio por SRI (Servicio de Rentas Internas - Ecuador). Secuencial y único. |
| `metodo_pago` | Necesario para conciliación bancaria y cierre de caja. |

---

## 2. Servicio Transaccional (ACID)

### 2.1 Flujo de creación

```
POST /invoicing/invoices/create/
  │
  ├─ 1. Validar datos de entrada (cliente, productos, cantidades)
  │
  ├─ 2. INICIO TRANSACCIÓN (@transaction.atomic)
  │     │
  │     ├─ 3. Generar número secuencial (select_for_update on counter)
  │     │
  │     ├─ 4. Para cada producto:
  │     │     ├─ Verificar stock suficiente
  │     │     ├─ Calcular subtotal, IVA, total del detalle
  │     │     └─ Descontar stock: Producto.objects.filter(id=X, stock__gte=cant)
  │     │                             .update(stock=F('stock') - cant)
  │     │        → Si stock insuficiente → raise ValidationError → ROLLBACK
  │     │
  │     ├─ 5. Calcular totales de la factura (subtotal, IVA, total)
  │     │
  │     ├─ 6. Crear Factura con totales
  │     │
  │     └─ 7. Crear DetallesFactura en bulk
  │
  ├─ 8. FIN TRANSACCIÓN (commit automático)
  │
  └─ 9. Retornar Factura creada con número asignado
```

### 2.2 Flujo de anulación

```
POST /invoicing/invoices/<id>/annul/
  │
  ├─ 1. Validar que la factura NO esté ya anulada
  │
  ├─ 2. INICIO TRANSACCIÓN
  │     │
  │     ├─ 3. Para cada detalle:
  │     │     └─ Restaurar stock: Producto.objects.filter(id=X)
  │     │                             .update(stock=F('stock') + cantidad)
  │     │
  │     └─ 4. soft_delete() en Factura
  │
  ├─ 5. FIN TRANSACCIÓN
  │
  └─ 6. Retornar Factura anulada
```

### 2.3 Clase de servicio (separada de la vista — SRP)

```python
class FacturaService:
    """Servicio transaccional de facturación (SRP: lógica de negocio)."""

    @staticmethod
    @transaction.atomic
    def crear(cliente_id, usuario_id, productos_data, metodo_pago='Efectivo', observaciones=''):
        """
        productos_data = [
            {'producto_id': 1, 'cantidad': 2, 'descuento_pct': 0},
            {'producto_id': 3, 'cantidad': 5, 'descuento_pct': 10},
        ]
        """
        ...

    @staticmethod
    @transaction.atomic
    def anular(factura_id):
        ...
```

### 2.4 Producto.validar_stock()

Para evitar condiciones de carrera, el descuento de stock usa `F()`:

```python
# INCORRECTO (race condition):
producto = Producto.objects.get(id=X)
if producto.stock >= cantidad:
    producto.stock -= cantidad
    producto.save()

# CORRECTO (atómico):
rows = Producto.objects.filter(id=X, stock__gte=cantidad) \
                       .update(stock=F('stock') - cantidad)
if rows == 0:
    raise ValidationError(f'Stock insuficiente para {producto.nombre}')
```

---

## 3. Diseño UI/UX — Pantalla de Creación de Factura

### 3.1 Layout general

```
┌─────────────────────────────────────── ▲ ─────────────────────────────┐
│  HEADER: Logo | 📄 Nueva Factura              Usuario: Admin [Salir] │
├─────────────────────────────────────── │ ─────────────────────────────┤
│  ◀ Volver                               │                             │
│                                        │                             │
│  ┌─── DATOS DE FACTURA ───────────────┐ │                             │
│  │ N°: FAC-20260624-00001             │ │                             │
│  │ Fecha: 24/06/2026 14:30:25         │ │      SIDEBAR               │
│  │ Vendedor: Admin                    │ │      (oculto en            │
│  │ Cliente: [Buscar...] ▼ @@@        │ │       página de             │
│  │ Método Pago: [Efectivo ▼]          │ │       factura)              │
│  └────────────────────────────────────┘ │                             │
│                                        │                             │
│  ┌─── AGREGAR PRODUCTO ───────────────┐ │                             │
│  │ [Buscar producto por nombre...]   │ │                             │
│  │ Código │ Producto │ Stock │ Precio│ │                             │
│  │ ───────┼──────────┼───────┼───────│ │                             │
│  │ PRO-01 │ Laptop   │   10  │ 800.00│ │                             │
│  │ PRO-02 │ Mouse    │   50  │ 25.00 │ │                             │
│  │ PRO-03 │ Teclado  │   30  │ 45.00 │ │                             │
│  └────────────────────────────────────┘ │                             │
│                                        │                             │
│  ┌─── DETALLE DE FACTURA ─────────────┐ │                             │
│  │ # │ Código │ Producto │ Cant│ P/U  │ │                             │
│  │   │        │          │     │      │ │                             │
│  │ 1 │ PRO-01 │ Laptop   │  2  │800.00│ │                             │
│  │   │        │          │[🔻] │      │ │                             │
│  │   │        │          │Desc:│Subtot│ │                             │
│  │   │        │          │ 0%  │1600.0│ │                             │
│  │   │        │          │     │      │ │                             │
│  │ 2 │ PRO-02 │ Mouse    │  5  │ 25.00│ │                             │
│  │   │        │          │[🔻] │      │ │                             │
│  │   │        │          │Desc:│Subtot│ │                             │
│  │   │        │          │ 10% │ 112.5│ │                             │
│  │───┴────────┴──────────┴─────┴──────│ │                             │
│  │                                    │ │                             │
│  │         Subtotal:       1,712.50   │ │                             │
│  │         IVA 15%:          256.88   │ │                             │
│  │         ─────────────────────────  │ │                             │
│  │         TOTAL:          1,969.38   │ │                             │
│  └────────────────────────────────────┘ │                             │
│                                        │                             │
│  ┌─── OBSERVACIONES ──────────────────┐ │                             │
│  │ [Venta corporativa.....................]│                          │
│  └────────────────────────────────────┘ │                             │
│                                        │                             │
│        [🗑 Limpiar]       [💾 Guardar Factura]                       │
└─────────────────────────────────────── ▼ ─────────────────────────────┘
```

### 3.2 Funcionalidades UX clave

| Funcionalidad | Comportamiento |
|--------------|----------------|
| **Buscador de clientes** | Mientras escribes, filtra por nombre, cédula o email (AJAX). Seleccionas uno y se asigna |
| **Buscador de productos** | Lista en tiempo real con stock y precio. Al hacer clic en un producto, se agrega a la tabla de detalles |
| **Cantidad editable inline** | En la tabla de detalles, la cantidad es un input editable. Al cambiar, recalcula subtotal en vivo |
| **Descuento por línea** | Cada detalle tiene un campo de descuento % que actualiza el subtotal en tiempo real |
| **Totales en vivo** | Subtotal, IVA y TOTAL se actualizan automáticamente al agregar/quitar/modificar un detalle |
| **Botón eliminar detalle** | Cada fila tiene un botón ✕ para quitar el producto de la factura |
| **Stock warning** | Si la cantidad supera el stock, la fila se marca en rojo y no permite guardar |
| **Feedback visual** | Spinner en botón Guardar mientras se procesa. Toast de éxito/error al finalizar |
| **Responsive** | En mobile, la tabla se aplana (cada detalle es una tarjeta en lugar de fila) |

### 3.3 JavaScript SOLID

```
invoicing/js/
├── api-client.js         (SRP: comunicación HTTP — REUSADO del Lab 03b)
├── invoice-service.js    (SRP: lógica de negocio de facturación)
│     └── crear(), anular(), buscarCliente(), buscarProducto()
├── invoice-form.js       (SRP: controlador del formulario)
│     └── maneja eventos DOM, validación, UX dinámica
└── invoice-calculator.js (SRP: cálculos financieros)
      └── calcularSubtotal(), calcularIVA(), calcularTotal()
```

---

## 4. Vistas (CBVs — Simplicidad esencial)

```
invoicing/views.py
├── InvoiceListView(ListView)
│     → Lista paginada con filtros por fecha y cliente
│
├── InvoiceCreateView(TemplateView)
│     → GET: Renderiza formulario maestro-detalle
│     → POST: Llama a FacturaService.crear() y retorna resultado JSON
│
├── InvoiceDetailView(DetailView)
│     → Muestra factura completa con todos los detalles
│
└── InvoiceAnnulView(View)
      → POST: Llama a FacturaService.anular()
      → Retorna JSON con resultado
```

---

## 5. User Stories actualizadas (HU-34 a HU-38)

### HU-34 — Crear Factura (5 pts → 5 pts) ✅ sin cambios
### HU-35 — Descuento Automático de Stock (3 pts → 3 pts) ✅ sin cambios
### HU-36 — Cálculo Automático de IVA (2 pts → 2 pts) ✅ sin cambios
### HU-37 — Anular Factura (5 pts → 5 pts) ✅ sin cambios

### HU-38 — Historial de Facturas (3 pts → 3 pts) ✅ sin cambios

### NUEVA HU-38b — Interfaz Profesional de Facturación (3 pts)

**Historia:** Como **vendedor** quiero una interfaz de facturación con buscador de productos, tabla de detalles editable en vivo y totales automáticos para facturar de manera rápida y profesional.

**Pts:** 3

**Criterios de Aceptación:**
1. Dado el formulario de factura, cuando escribo en el buscador de productos, entonces se filtran en tiempo real mostrando código, nombre, stock y precio
2. Dado que selecciono un producto, cuando hago clic, entonces se agrega a la tabla de detalles con cantidad=1 y subtotal calculado
3. Dado la tabla de detalles, cuando cambio la cantidad de un ítem, entonces el subtotal de línea y los totales generales se actualizan automáticamente (sin recargar)
4. Dado la tabla de detalles, cuando hago clic en ✕, entonces el ítem se elimina y los totales se recalculan
5. Dado que intento guardar, cuando hay un ítem con cantidad > stock, entonces el botón Guardar está deshabilitado y la fila se marca en rojo

---

## 6. Total HU del Lab 09 actualizado

| ID | Historia | Pts |
|----|----------|:---:|
| HU-34 | Como **vendedor** quiero crear una factura seleccionando cliente, productos y cantidades | 5 |
| HU-35 | Como **vendedor** quiero que el stock se descuente automáticamente con F() | 3 |
| HU-36 | Como **vendedor** quiero que el IVA y subtotales se calculen automáticamente | 2 |
| HU-37 | Como **administrador** quiero anular una factura y restaurar el stock | 5 |
| HU-38 | Como **usuario** quiero ver el historial de facturas con filtros | 3 |
| HU-38b | Como **vendedor** quiero una interfaz profesional con tabla de detalles en vivo | 3 |
| | **Total Sprint 10** | **21 pts** |
