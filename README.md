# 🛒 E-Commerce Intelligent Platform

Plataforma de comercio electrónico desarrollada como proyecto académico, enfocada en arquitectura escalable, modular y basada en buenas prácticas de ingeniería de software. Incluye funcionalidades de navegación de productos, carrito de compras, gestión de pedidos, roles de usuario (cliente y administrador), sugerencias inteligentes basadas en historial, y visualización de stock.

---

## 🚀 Características Principales

✔️ Registro e inicio de sesión de usuarios (Cliente y Administrador)  
✔️ Navegación de productos por categoría, marca y promociones  
✔️ Carrito de compras con actualización de cantidades y precios dinámicos  
✔️ Pasarela de pago simulada con estados del pedido  
✔️ Gestión de inventario (Admin)  
✔️ Historial de pedidos y seguimiento  
✔️ Recomendaciones inteligentes basadas en IA (historial y preferencias)  
✔️ Arquitectura modular, escalable y mantenible  
✔️ Documentación UML y vistas arquitectónicas  

---

## 🏗️ Arquitectura del Proyecto

El sistema se diseñó aplicando las **vistas arquitectónicas de 4+1**:

| Vista | Descripción | En este proyecto |
|-------|-------------|------------------|
| **Lógica** | Funcionalidad principal del sistema | Módulos: usuario, producto, carrito, pago, pedido |
| **Desarrollo** | Organización del código | Arquitectura modular + MVC + repositorios |
| **Procesos de negocio** | Flujo y reglas del negocio | Compra, pago, registro, stock, pedidos |
| **Física** | Infraestructura y despliegue | Cliente ← API ← Servidor cloud con BD |

---

## 📂 Estructura del Repositorio

```
/ecommerce-intelligent-platform
│── src/
│   ├── controllers/
│   ├── models/
│   ├── services/
│   ├── views/
│   ├── utils/
│── docs/
│   ├── uml/
│   ├── arquitectura.pdf
│   ├── mockups/
│── tests/
│── requirements.txt
│── README.md
│── .gitignore
```

---

## 🧪 Testing

Se implementaron pruebas automáticas bajo **PyTest** y pruebas manuales funcionales.

| Tipo de Prueba | Descripción |
|----------------|------------|
| Unitarias | Servicios, controladores, cálculo total del carrito |
| Integración | Flujo de compra, stock + pedidos |
| UI Testing | Validación de campos, navegación, mensajes de error |
| Mock Testing | Simulación de respuesta de pasarela de pago |

---

## 📈 Tecnologías Utilizadas

| Tecnología | Uso |
|------------|-----|
| Python / Flask o Django | Backend del sistema |
| HTML, CSS, JavaScript, Bootstrap | Frontend responsive |
| SQLite / MySQL | Base de datos |
| PyTest | Testing |
| UML con StarUML / Draw.io | Modelado |
| Git y GitHub | Control de versiones |
| IA (recomendador) | Sugerencias de productos |

---

## 🧠 Inteligencia Artificial Aplicada

Se implementa un módulo de IA que analiza:

🟢 Historial de compras  
🟢 Productos agregados al carrito  
🟢 Categorías más visitadas  

Generando recomendaciones personalizadas (collaborative filtering / rule-based).

---

## ⚙️ Instalación y Ejecución

```bash
# Clonar el repositorio
git clone https://github.com/usuario/ecommerce-intelligent-platform.git
cd ecommerce-intelligent-platform

# Crear entorno virtual
python -m venv env
source env/Scripts/activate  # Windows
source env/bin/activate      # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar proyecto
python main.py
```

---

## 🗺️ Diagramas UML Incluidos (Ubicados en /docs/uml)

✔️ Diagrama de casos de uso  
✔️ Diagrama de clases  
✔️ Diagrama de secuencia (Flujo de compra)  
✔️ Diagrama de componentes  
✔️ Diagrama de despliegue  

---

## 📌 Futuras Implementaciones

- [ ] Integración con pasarela de pagos real (PayPal, Stripe)  
- [ ] Token JWT para seguridad y autenticación  
- [ ] Panel avanzado de administrador con gráficas estadísticas  
- [ ] Implementación de microservicios  
- [ ] App móvil Android con consumo de API  

---

## 👥 Integrantes del Proyecto

| Nombre | Rol |
|--------|-----|
| Sebastián Moreno Acosta | Arquitectura, Backend, IA |
| Compañero 2 (agregar) | Frontend, Testing, Documentación |

---

## 📄 Licencia

Este proyecto se distribuye bajo licencia MIT.  
Libre para uso académico y mejora con créditos correspondientes.
