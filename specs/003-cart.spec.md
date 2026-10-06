# 📄 Spec 003: Carrito de Compras

**Estado:** Borrador
**Fecha:** 2026-10-06
**Módulo:** Carrito

---

## 🎯 Objetivo y Contexto

Permitir al cliente agregar, actualizar y eliminar productos del carrito, con recalculo de precios dinámicos y validación de stock.

---

## 📋 Requisitos Funcionales (RF - Sintaxis EARS)

- **RF-01 (Ubicuidad):** El sistema DEBE mantener un carrito asociado a cada usuario autenticado.
- **RF-02 (Evento):** CUANDO el cliente agrega un producto, el sistema DEBE validar stock disponible y responder 409 si es insuficiente.
- **RF-03 (Evento):** CUANDO el cliente actualiza la cantidad de una línea, el sistema DEBE recalcular subtotal, impuestos y total.
- **RF-04 (Opcional):** DONDE el carrito quede vacío, el sistema DEBE permitir el checkout únicamente tras agregar al menos un ítem.
- **RF-05 (Anomalía):** SI el stock de un producto baja entre el agregado y el checkout, ENTONCES el sistema DEBE ajustar la línea y notificar al usuario.

---

## ⚠️ Casos Límite y Excepciones

- **CL-01:** Cantidad 0 en una línea → la línea se elimina del carrito.
- **CL-02:** Usuario no autenticado intenta operar el carrito → 401.

---

## ✅ Criterios de Aceptación (Hecho cuando)

- [ ] Cálculo de totales validado con pruebas unitarias (`tests/`).
- [ ] Ediciones concurrentes de cantidades responden con estado consistente.
- [ ] La UI del carrito funciona en móvil y escritorio.
