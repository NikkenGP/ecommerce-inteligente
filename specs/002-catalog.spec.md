# 📄 Spec 002: Catálogo de Productos

**Estado:** Borrador
**Fecha:** 2026-10-06
**Módulo:** Catálogo

---

## 🎯 Objetivo y Contexto

Exponer el catálogo de productos navegable por categoría, marca y promoción, consumido por el frontend con JavaScript asíncrono.

---

## 📋 Requisitos Funcionales (RF - Sintaxis EARS)

- **RF-01 (Ubicuidad):** El sistema DEBE soportar `GET /api/v1/products` con filtros `category`, `brand`, `on_sale` y paginación (`page`, `page_size`).
- **RF-02 (Evento):** CUANDO el cliente solicita el detalle de un producto existente, el sistema DEBE responder 200 con `id`, `name`, `price`, `stock`, `category`, `brand`, `rating`.
- **RF-03 (Opcional):** DONDE se habilite `on_sale=true`, el sistema DEBE devolver solo productos con precio promocional vigente.
- **RF-04 (Anomalía):** SI el `product_id` no existe, ENTONCES el sistema DEBE responder 404 con error estándar `{code, message}`.
- **RF-05 (Evento):** CUANDO un administrador crea/actualiza un producto, el sistema DEBE validar precio > 0 y stock ≥ 0 antes de persistir.

---

## ⚠️ Casos Límite y Excepciones

- **CL-01:** Página fuera de rango → 200 con lista vacía y metadatos de paginación.
- **CL-02:** Producto con stock 0 → visible pero no agregable al carrito.

---

## ✅ Criterios de Aceptación (Hecho cuando)

- [ ] Filtros y paginación validados con pruebas de integración.
- [ ] Las anomalías 404/422 están cubiertas con pruebas.
- [ ] El listado renderiza en Tailwind en móvil y escritorio.
