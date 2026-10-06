# 🧪 Plan de Pruebas — E-Commerce Intelligent Platform

**Fecha:** 2026-10-06
**Framework:** PyTest
**Cobertura mínima:** 80% (`pytest --cov=src --cov-report=term-missing`)

---

## Herramientas y Configuración

- `pytest`, `pytest-asyncio`, `httpx`, `pytest-cov`, `pytest-benchmark` (opcional).
- Markers registrados: `@pytest.mark.unit`, `@pytest.mark.integration`.
- Base de datos de pruebas: PostgreSQL de test (o SQLite solo si el comportamiento SQL lo permite) con fixtures de sesión.
- Redis mockeado con `fakeredis` o fixture que simule TTL.

## Estructura de `tests/`

```
tests/
├── conftest.py
├── mocks/
│   └── payment_gateway.py   # approved | declined | timeout
├── unit/
│   ├── test_auth_service.py
│   ├── test_cart_totals.py
│   ├── test_recommendation_engine.py
│   └── test_rules.py
└── integration/
    ├── test_auth_flow.py
    ├── test_checkout_flow.py
    └── test_recommendations_api.py
```

## Mock de Pasarela de Pagos

`tests/mocks/payment_gateway.py` debe implementar la interfaz `PaymentGateway` con tres escenarios deterministas:

| Escenario | Resultado | Código HTTP esperado |
|-----------|-----------|----------------------|
| `approved` | `PaymentResult(status="approved")` | 201 / 200 |
| `declined` | `PaymentResult(status="declined")` | 402 |
| `timeout` | excepción `PaymentTimeout` | 504 |

**Prohibido:** integrar APIs reales de Stripe/PayPal en cualquier fase.

## Matriz de Casos por Módulo

| Módulo | Unit | Integración |
|--------|------|-------------|
| Auth (001) | hash de contraseña, emisión/validación JWT, rotación refresh | registro → login → refresh → logout; revocación |
| Catálogo (002) | validaciones de filtros y paginación | listados 200, detalle 404 |
| Carrito (003) | cálculo de totales, actualización de líneas | agregar/actualizar/eliminar con stock |
| Pagos (004) | mapping de escenarios mock | checkout con approved/declined/timeout |
| Pedidos/Inventario (005) | descuento de stock, estados de pedido | compra concurrente (última unidad), rollback |
| Recomendador (006) | fusión α/β, cold start, fallback, exclusión stock 0 | endpoint 200/404/500, caché TTL, p95 < 300 ms |

## Criterios de Aceptación del Plan

- [ ] Markers `unit`/`integration` configurados en `pytest.ini`/`pyproject.toml`.
- [ ] `pytest --cov=src --cov-report=term-missing` reporta ≥ 80%.
- [ ] Ninguna llamada saliente real a pasarelas de pago (revisado en CI).
- [ ] Casos de anomalía (SI... ENTONCES...) de cada spec tienen prueba asociada.
- [ ] Frontend validado manualmente: campos, navegación, mensajes de error, responsivo.
