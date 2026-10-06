# 🏛️ Arquitectura — Modelo 4+1 (Krutchen)

**Fecha:** 2026-10-06
**Estado:** Borrador

---

## 1. Vista de Escenarios (+1)

Casos de uso principales que guían el diseño:

```mermaid
---
title: Escenarios Clave
---
flowchart LR
    Cliente((Cliente)) --> S1["Buscar y filtrar productos"]
    Cliente --> S2["Agregar al carrito"]
    Cliente --> S3["Checkout con pago simulado"]
    Cliente --> S4["Ver recomendaciones"]
    Admin((Administrador)) --> S5["Gestionar inventario"]
    Admin --> S6["Ver historial y reportes"]
```

## 2. Vista Lógica

Módulos del dominio y sus relaciones principales:

```mermaid
---
title: Vista Lógica — Dominio
---
classDiagram
    class User {
      +UUID id
      +String email
      +String role
    }
    class Product {
      +UUID id
      +String name
      +Decimal price
      +Integer stock
      +String category
    }
    class Cart {
      +UUID id
      +UUID userId
      +Decimal total
    }
    class CartItem {
      +UUID productId
      +Integer quantity
    }
    class Order {
      +UUID id
      +UUID userId
      +OrderStatus status
      +Decimal total
    }
    class Payment {
      +UUID id
      +Decimal amount
      +PaymentStatus status
    }
    User "1" --> "1" Cart
    Cart "1" --> "*" CartItem
    User "1" --> "*" Order
    Order "1" --> "1" Payment
    Product "1" <-- "*" CartItem
```

## 3. Vista de Procesos

Flujo del negocio de compra (async request/response, workers opcionales):

```mermaid
---
title: Vista de Procesos — Compra
---
sequenceDiagram
    actor C as Cliente
    participant API as API FastAPI
    participant PAY as PaymentGateway (mock)
    participant DB as PostgreSQL
    C->>API: POST /checkout (cart_id)
    API->>PAY: charge(total)
    alt approved
        PAY-->>API: approved
        API->>DB: Crear Order + descontar stock (transacción)
        API-->>C: 201 Order creada
    else declined/timeout
        API-->>C: 402/504, Order en PAYMENT_FAILED
    end
```

## 4. Vista de Desarrollo

Organización del código (módulos, capas, tests):

```mermaid
---
title: Vista de Desarrollo — Paquetes
---
flowchart TB
    subgraph src
        api["src/api (routers)"]
        svc_auth["src/services/auth"]
        svc_cat["src/services/catalog"]
        svc_cart["src/services/cart"]
        svc_pay["src/services/payments"]
        svc_ord["src/services/orders"]
        svc_rec["src/services/recommendation"]
        models["src/models (SQLAlchemy)"]
        schemas["src/schemas (Pydantic)"]
    end
    subgraph tests
        unit["tests/unit"]
        integ["tests/integration"]
        mocks["tests/mocks/payment_gateway.py"]
    end
    api --> svc_auth & svc_cat & svc_cart & svc_pay & svc_ord & svc_rec
    svc_auth --> models & schemas
    svc_pay --> mocks
    unit --> src
    integ --> src
```

## 5. Vista Física

Despliegue cloud único:

```mermaid
---
title: Vista Física — Despliegue
---
flowchart LR
    Browser["Navegador (Tailwind + Vanilla JS)"] -->|HTTPS| LB["FastAPI + Uvicorn"]
    LB --> PG[(PostgreSQL)]
    LB --> R[(Redis)]
    LB -.->|mock interno| PGW["PaymentGateway simulado"]
```

---

## Decisiones Clave

| Decisión | Justificación |
|----------|---------------|
| FastAPI + Pydantic | Tipado, validación y OpenAPI automático |
| PostgreSQL | Consistencia ACID para pedidos e inventario |
| Redis | Caché de recomendaciones (TTL 5 min) y lista negra JWT |
| Pasarela mockeada | Restricción del proyecto: `tests/mocks/payment_gateway.py` |
| Vanilla JS + Tailwind | Sin frameworks pesados de frontend |

Diagramas UML de referencia: `docs/uml/use-cases.md`, `checkout-sequence.md`, `components-mvc.md`, `deployment.md`.
