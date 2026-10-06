# 📄 Spec 001: Autenticación y Usuarios

**Estado:** Borrador
**Fecha:** 2026-10-06
**Módulo:** Usuarios / Auth

---

## 🎯 Objetivo y Contexto

Gestionar el registro, inicio de sesión y autorización de usuarios con roles `Cliente` y `Administrador`, garantizando seguridad mediante JWT de corta duración, rotación de refresh tokens y revocación en logout.

---

## 📋 Requisitos Funcionales (RF - Sintaxis EARS)

- **RF-01 (Ubicuidad):** El sistema DEBE emitir un `access_token` (15–30 min) y un `refresh_token` (7 días) firmados tras login exitoso.
- **RF-02 (Evento):** CUANDO un cliente se registra con email válido y contraseña segura, el sistema DEBE crear la cuenta con rol `Cliente` y hashear la contraseña (bcrypt/argon2).
- **RF-03 (Evento):** CUANDO llega una petición a una ruta protegida, el sistema DEBE validar firma y expiración del JWT; SI es inválido, ENTONCES responder 401.
- **RF-04 (Estado):** MIENTRAS exista un refresh token válido y no revocado, el sistema DEBE permitir obtener un nuevo access token rotando el refresh token.
- **RF-05 (Anomalía):** SI un refresh token ya rotado o revocado se presenta de nuevo, ENTONCES el sistema DEBE revocar la cadena completa y responder 401 (detección de reuso).
- **RF-06 (Evento):** CUANDO el usuario cierra sesión, el sistema DEBE revocar access y refresh tokens (lista negra en Redis).
- **RF-07 (Ubicuidad):** Las rutas de administración DEBEN requerir rol `Administrador` mediante la dependencia `require_role("Administrador")`.

---

## ⚠️ Casos Límite y Excepciones

- **CL-01:** Usuario con credenciales incorrectas → 401 genérico sin revelar si el email existe.
- **CL-02:** Refresh token expirado a los 7 días → el usuario DEBE reautenticarse.
- **CL-03:** Dos pestañas concurrentes refrescan con el mismo refresh token → solo la primera rota; la segunda recibe 401.

---

## ✅ Criterios de Aceptación (Hecho cuando)

- [ ] Flujo registro → login → refresh → logout funciona en tests de integración.
- [ ] Las condiciones de anomalía (SI... ENTONCES...) están validadas con pruebas.
- [ ] Las vistas de auth responden correctamente en móvil y escritorio.
