# 📄 Spec 006: Motor de Recomendación Híbrido

**Estado:** Borrador
**Fecha:** 2026-10-06
**Módulo:** IA Recomendador

---

## 🎯 Objetivo y Contexto

Ofrecer recomendaciones personalizadas combinando filtrado colaborativo item-based y reglas de negocio, con degradación elegante y latencia controlada. Detalle técnico ampliado en `docs/modules/recommendation-engine.md`.

---

## 📋 Requisitos Funcionales (RF - Sintaxis EARS)

- **RF-01 (Ubicuidad):** El sistema DEBE exponer `GET /api/v1/recommendations/{user_id}` con `limit` opcional (default 10).
- **RF-02 (Ubicuidad):** Cada recomendación DEBE incluir `product_id`, `score` normalizado [0.0, 1.0] y `source` (`collaborative|rules|hybrid`).
- **RF-03 (Evento):** CUANDO el usuario tenga ≥ 3 interacciones, el sistema DEBE combinar estrategias con `score = 0.7*CF + 0.3*rules`.
- **RF-04 (Evento):** CUANDO el usuario tenga < 3 interacciones (cold start), el sistema DEBE delegar en la estrategia basada en reglas.
- **RF-05 (Anomalía):** SI el filtrado colaborativo falla, ENTONCES el sistema DEBE responder solo con reglas (fallback) sin errores 5xx.
- **RF-06 (Estado):** MIENTRAS los resultados estén en caché (TTL 5 min, clave `user_id`), el sistema DEBE servirlos sin recalcular.
- **RF-07 (Ubicuidad):** El p95 del endpoint DEBE ser < 300 ms con catálogo de hasta 100k productos; nunca debe incluir productos con `stock = 0` ni comprados en los últimos 30 días.

---

## ⚠️ Casos Límite y Excepciones

- **CL-01:** Usuario inexistente → 404.
- **CL-02:** Caída de Redis → recalcular sin caché (degradar, no fallar).
- **CL-03:** Empates de score → desempate por `rating` descendente y luego `product_id`.

---

## ✅ Criterios de Aceptación (Hecho cuando)

- [ ] Estrategia híbrida probada con datos controlados (α*CF + β*rules verificable).
- [ ] Cold start, fallback y caching validados con mocks de Redis.
- [ ] Benchmark p95 < 300 ms documentado en `docs/modules/recommendation-engine.md`.
