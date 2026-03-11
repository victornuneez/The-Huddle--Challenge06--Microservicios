# Sistemas de Logging y Ecosistema de Microservicios

Este repositorio incluye dos proyectos completos:

1. **Sistema de Logging Distribuido (SLD)**: centralización de logs de múltiples microservicios.  
2. **Task Manager Pro**: ecosistema de microservicios con autenticación JWT, Circuit Breaker y bases de datos independientes.  

---

## Sistema de Logging Distribuido (SLD)

Este proyecto es una solución robusta y modular para la centralización de registros (logs) procedentes de múltiples microservicios. Utiliza una arquitectura Cliente-Servidor sobre HTTP para recolectar, validar y almacenar eventos de sistema en tiempo real.

### 📁 Estructura del Proyecto

#### `/servidor`
- **app.py**: Servidor Flask y Endpoints.  
- **basededatos.py**: Gestión de SQLite3.  
- **tokensvalidos.py**: Sistema de seguridad y autenticación.  

#### `/servicios`
- **auth_service.py**: Gestión de sesiones y accesos.  
- **email_service.py**: Notificaciones y eventos SMTP.  
- **payment_service.py**: Transacciones y estados financieros.  

### 🚀 Funcionalidades Principales

#### 1. Servidor Central de Logging
- **Autenticación**: Solo acepta logs de servicios con un Token de Autorización válido (Header `Authorization`).  
- **Procesamiento Inteligente**: Puede recibir un solo log o un batch de logs en una sola petición.  
- **Persistencia**: Almacenamiento automático en SQLite con registro de `received_at`.  
- **Consulta Avanzada**: Endpoint GET con filtros por rango de fechas.  

#### 2. Microservicios (Simuladores)
- **Generación Aleatoria**: Eventos (`INFO`, `WARNING`, `ERROR`, `CRITICAL`) con mensajes específicos.  
- **Independencia**: Cada servicio corre en su propio proceso e intervalo.  
- **Resiliencia**: Manejo de errores y timeouts al conectar con el servidor.  

### 🛠️ Tecnologías Utilizadas
- **Python 3**  
- **Flask**  
- **SQLite3**  
- **Requests**  
- **JSON**  

### 📊 Flujo de Datos
1. Un servicio genera un evento (ej: `"Pago rechazado"`).  
2. Lo empaqueta en un JSON con su Token y lo envía vía POST a `/logs`.  
3. El Servidor valida el token.  
4. Si es válido, guarda el log en la base de datos.  
5. Un administrador puede consultar los logs vía GET desde cualquier navegador o cliente API.  

### 🚦 Cómo Ejecutar el Proyecto
```bash
# Iniciar servidor
cd servidor
python app.py

# Iniciar servicios (en terminales separadas)
python servicios/auth_service.py
python servicios/email_service.py
python servicios/payment_service.py
