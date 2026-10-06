# 📄 Spec 000: Documento Maestro SDD — E-Commerce Intelligent Platform

**Estado:** Borrador
**Fecha:** 2026-10-06
**Módulo:** Todos

---

## 🎯 Objetivo y Contexto

Documento maestro de Spec-Driven Development que consolida la visión, el alcance y las restricciones de la plataforma. Sirve como índice para las specs de módulo (`001`–`006`) y como contrato frente a los subagentes de implementación (`@02_backend_ia`, `@03_frontend_ui`, `@04_qa_testing`).

---

## 🏗️ Stack y Arquitectura Objetivo

| Capa | Tecnología |
|------|------------|
| Backend | Python + FastAPI + Uvicorn |
| Frontend | HTML/CSS + Tailwind CSS v4 + Vanilla JS ES6+ asíncrono (sin React/Angular/Bootstrap) |
| Persistencia | PostgreSQL (relacional) + Redis (caché y revocación de tokens JWT) |
| Autenticación | JWT: access token 15–30 min, refresh token 7 días con rotación y revocación en logout |
| Pruebas | PyTest (`unit` / `integration`), mock de pasarela de pagos, cobertura ≥ 80% |
| Motor de recomendación | Híbrido item-based CF + reglas; `score = 0.7*CF + 0.3*rules` |
| Despliegue | Cloud único: API + PostgreSQL + Redis; pasarela de pagos siempre simulada |

Estructura de código objetivo:

```
src/
├── api/            # routers FastAPI (v1)
├── services/
│   ├── auth/
│   ├── catalog/
│   ├── cart/
│   ├── payments/
│   ├── orders/
│   └── recommendation/
├── models/         # SQLAlchemy
├── schemas/        # Pydantic
└── utils/
tests/
├── mocks/payment_gateway.py
└── unit|integration/
```

---

## 📋 Requisitos Funcionales (RF - Sintaxis EARS)

- **RF-01 (Ubicuidad):** El sistema DEBE exponer una API REST versionada bajo `/api/v1/` con esquemas OpenAPI generados por FastAPI.
- **RF-02 (Evento):** CUANDO un cliente se registra o inicia sesión, el sistema DEBE emitir tokens JWT firmados HS256/RS256.
- **RF-03 (Estado):** MIENTRAS existan tokens válidos, el sistema DEBE autorizar las rutas según el rol (`Cliente` / `Administrador`) mediante `require_role(...)`.
- **RF-04 (Opcional):** DONDE el motor de recomendación no disponga de historial del usuario, el sistema DEBE responder con estrategia basada en reglas (cold start).
- **RF-05 (Anomalía):** SI la pasarela de pagos mockeada devuelve `decline` o `timeout`, ENTONCES el sistema DEBE dejar el pedido en estado `PAYMENT_FAILED` sin descontar stock.
- **RF-06 (Ubicuidad):** Toda decisión de recomendación DEBE ser trazable en logs estructurados (`user_id`, `strategy`, `latency_ms`, `result_count`).

---

## ⚠️ Casos Límite Globales

- **CL-01:** Dos usuarios compran simultáneamente la última unidad → control de concurrencia en inventario (transacción + `SELECT ... FOR UPDATE`).
- **CL-02:** Sesión expirada durante el checkout → el carrito persiste y el flujo puede reanudarse tras refrescar el token.
- **CL-03:** Caída de Redis → el sistema DEBE degradar sin caché y sin revocación distribuida, manteniendo el servicio principal.
- **CL-04:** Catálogo sin productos en una categoría → endpoints de listado responden 200 con lista vacía, nunca 500.

---

## ✅ Criterios de Aceptación Globales

- [ ] Todas las specs `NNN-*.spec.md` están aprobadas antes de escribir código.
- [ ] Cobertura de pruebas ≥ 80% con `pytest --cov=src --cov-report=term-missing`.
- [ ] p95 del endpoint de recomendaciones < 300 ms con caché TTL 5 min.
- [ ] No existe ninguna integración real con pasarelas de pago (Stripe/PayPal).
- [ ] Diagramas 4+1 rederan correctamente (`docs/uml/`).

---

## 📚 Índice de Especificaciones

| Spec | Módulo |
|------|--------|
| `001-auth.spec.md` | Autenticación y Usuarios (JWT, roles) |
| `002-catalog.spec.md` | Catálogo de Productos |
| `003-cart.spec.md` | Carrito de Compras |
| `004-payments.spec.md` | Pagos (mock estricto) |
| `005-orders-inventory.spec.md` | Pedidos e Inventario |
| `006-recommendation-engine.spec.md` | Motor de Recomendación Híbrido |
