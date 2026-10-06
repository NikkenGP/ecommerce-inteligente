# 📄 Spec 005: Pedidos e Inventario

**Estado:** Borrador
**Fecha:** 2026-10-06
**Módulo:** Pedidos / Inventario

---

## 🎯 Objetivo y Contexto

Gestionar la creación de pedidos a partir del carrito, el descuento transaccional de stock y el historial/seguimiento de pedidos.

---

## 📋 Requisitos Funcionales (RF - Sintaxis EARS)

- **RF-01 (Evento):** CUANDO el pago es `approved`, el sistema DEBE crear el pedido con estado `PAID` y descontar stock en la misma transacción.
- **RF-02 (Estado):** MIENTRAS un pedido esté en `PENDING`, el sistema DEBE permitir cancelarlo restituyendo stock reservado.
- **RF-03 (Ubicuidad):** El sistema DEBE garantizar consistencia de inventario incluso con compras concurrentes (bloqueo pesimista por fila).
- **RF-04 (Evento):** CUANDO el administrador actualiza stock, el sistema DEBE registrar la operación en auditoría (`product_id`, `delta`, `admin_id`, `timestamp`).
- **RF-05 (Anomalía):** SI el stock es insuficiente en el momento del checkout, ENTONCES el sistema DEBE responder 409 y no cobrar.

---

## ⚠️ Casos Límite y Excepciones

- **CL-01:** Dos pedidos compiten por la última unidad → solo uno se confirma.
- **CL-02:** Fallo de base de datos a mitad de la transacción → rollback completo: ni pedido ni cargo.
- **CL-03:** Consulta de historial de un usuario con muchos pedidos → paginación obligatoria.

---

## ✅ Criterios de Aceptación (Hecho cuando)

- [ ] Flujo creación de pedido + descuento de stock validado en integración.
- [ ] Condiciones de anomalía validadas con pruebas (incl. concurrencia simulada).
- [ ] El historial de pedidos es usable en móvil y escritorio.
