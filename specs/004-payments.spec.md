# 📄 Spec 004: Pagos (Mock Estricto)

**Estado:** Borrador
**Fecha:** 2026-10-06
**Módulo:** Pagos

---

## 🎯 Objetivo y Contexto

Simular la pasarela de pagos con escenarios controlados (`approved`, `declined`, `timeout`), sin ninguna integración real con Stripe/PayPal. La simulación vive en `tests/mocks/payment_gateway.py` y en `src/services/payments/`.

---

## 📋 Requisitos Funcionales (RF - Sintaxis EARS)

- **RF-01 (Ubicuidad):** El sistema DEBE invocar la pasarela únicamente a través de la interfaz `PaymentGateway.charge(amount, currency) -> PaymentResult`.
- **RF-02 (Evento):** CUANDO el escenario sea `approved`, el sistema DEBE devolver `{status: "approved", transaction_id}`.
- **RF-03 (Anomalía):** SI el escenario sea `declined`, ENTONCES el sistema DEBE devolver `{status: "declined", reason}` y no crear pedido.
- **RF-04 (Anomalía):** SI el escenario sea `timeout`, ENTONCES el sistema DEBE responder 504 y permitir reintento idempotente mediante `idempotency_key`.
- **RF-05 (Ubicuidad):** El código DEBE ser agnóstico al proveedor real; ninguna referencia a APIs externas de pago.

---

## ⚠️ Casos Límite y Excepciones

- **CL-01:** Reintento tras `timeout` con la misma `idempotency_key` → no duplicar cargos.
- **CL-02:** Monto ≤ 0 → 422 antes de contactar la pasarela.

---

## ✅ Criterios de Aceptación (Hecho cuando)

- [ ] Los tres escenarios (`approved`, `declined`, `timeout`) están cubiertos en pruebas.
- [ ] No se realizan llamadas HTTP salientes a proveedores reales.
- [ ] El flujo de pago está en el diagrama `checkout-sequence.md`.
