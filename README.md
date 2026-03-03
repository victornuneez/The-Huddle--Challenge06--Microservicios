Ecosistema de Microservicios: Task Manager Pro

Este proyecto es una implementación avanzada de Arquitectura de Microservicios que utiliza un patrón de comunicación inter-servicio. Incluye seguridad basada en tokens (JWT), persistencia de datos independiente y tolerancia a fallos mediante el patrón Circuit Breaker.

🏗️ Arquitectura del Sistema

El sistema se compone de tres microservicios que trabajan de forma coordinada:

1. Auth Service (Puerto 5000)

Es el "Portero" del sistema.

Responsabilidad: Registro de usuarios, hashing de contraseñas con werkzeug y generación/validación de JSON Web Tokens (JWT).

Seguridad: Utiliza variables de entorno (.env) para proteger la clave secreta.

2. Task Service (Puerto 5001)

Es el "Gestor de Contenido".

Responsabilidad: Permite crear, listar, marcar como completadas y eliminar tareas.

Validación: Antes de procesar cualquier acción, consulta internamente al Auth Service para confirmar que el token del usuario es válido.

3. Notification Service (Puerto 5002)

Es el "Orquestador Inteligente".

Responsabilidad: Genera recordatorios basados en las tareas pendientes del usuario.

Resiliencia: Utiliza un Circuit Breaker propio para monitorear la salud de los otros servicios. Si el Auth Service o el Task Service fallan, este servicio corta la comunicación temporalmente para evitar colapsar el sistema.

🛡️ El Circuit Breaker (Tolerancia a Fallos)

Es la pieza clave de este proyecto. Funciona como un interruptor de luz con tres estados:

🟢 CLOSED (Cerrado): Todo funciona bien. Las peticiones fluyen normalmente.

🔴 OPEN (Abierto): El servicio externo falló repetidamente. El sistema bloquea las peticiones automáticamente durante un tiempo (ej: 10-20 segundos) para dejar que el servicio se recupere.

🟡 HALF_OPEN (Semi-Abierto): Se realiza una petición de prueba. Si tiene éxito, vuelve a CLOSED; si falla, vuelve a OPEN.

📂 Estructura de Datos (SQLite)

Cada servicio tiene su propia base de datos, cumpliendo con el principio de Database per Service:

auth_service.db: Tabla Usuarios (id, username, password_hash, fecha).

tasks.db: Tabla Tareas (id, user_id, tarea, completada, fechas).

notificacion.db: Tabla Recordatorios (id, user_id, mensaje, fecha).

🚀 Cómo ponerlo en marcha

Instalar dependencias: pip install flask requests pyjwt python-dotenv werkzeug

Configurar .env: Crear un archivo .env en auth_service/ con JWT_CLAVE_SECRETA=tu_clave_super_secreta.

Ejecutar en orden:

Terminal 1: python auth_service/app.py

Terminal 2: python task_service/app.py

Terminal 3: python notification_service/app.py
