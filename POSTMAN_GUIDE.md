# 📮 Guía de Postman - Agent System API

Esta guía te ayudará a configurar y usar la colección de Postman para la API del Sistema de Agentes.

## 📁 Archivos Incluidos

- `Agent_System_API.postman_collection.json` - Colección principal con todos los endpoints
- `Agent_System.postman_environment.json` - Entorno de desarrollo
- `Agent_System_Production.postman_environment.json` - Entorno de producción

## 🚀 Configuración Inicial

### 1. Importar en Postman

1. Abre Postman
2. Clic en **Import** > **Files**
3. Selecciona los 3 archivos JSON
4. Confirma la importación

### 2. Configurar Entorno

1. En Postman, selecciona el entorno **"Agent System - Development"**
2. Edita las variables según tu configuración:

```
base_url: http://localhost:8000 (tu URL local)
username: tu_usuario
password: tu_contraseña
```

## 🔐 Flujo de Autenticación

### Paso 1: Registrar Usuario (Opcional)
- Usar endpoint: `Authentication > Register User`
- Cambiar datos en el body según necesites

### Paso 2: Login
- Usar endpoint: `Authentication > Login (JSON)`
- El token se guardará automáticamente en `access_token`

### Paso 3: Usar Endpoints Protegidos
- Todos los demás endpoints usarán automáticamente el token

## 📋 Estructura de la Colección

### 🔑 Authentication
- **Register User** - Registro de nuevos usuarios
- **Login (Form Data)** - Login OAuth2 estándar
- **Login (JSON)** - Login con JSON payload
- **Refresh Token** - Renovar token JWT
- **Get Current User Info** - Información del usuario actual

### 🤖 Agents
- **Get All Agents** - Listar agentes
- **Create Agent** - Crear nuevo agente
- **Get Agent by ID** - Obtener agente específico
- **Update Agent** - Actualizar agente
- **Delete Agent** - Eliminar agente  
- **Execute Agent** - Ejecutar agente con mensaje

### 🔧 Tools
- **Get All Tools** - Listar herramientas HTTP
- **Create Tool** - Crear nueva herramienta
- **Get Tool by ID** - Obtener herramienta específica
- **Update Tool** - Actualizar herramienta
- **Delete Tool** - Eliminar herramienta

### 📝 Prompt Templates
- **Get All Templates** - Listar templates de prompts
- **Create Template** - Crear nuevo template
- **Get Template by ID** - Obtener template específico
- **Update Template** - Actualizar template
- **Delete Template** - Eliminar template
- **Render Template** - Renderizar template con variables
- **Validate Template** - Validar sintaxis del template

### 📊 Metrics & Analytics
- **Get Cost Summary** - Resumen de costos con filtros
- **Get Usage Metrics** - Métricas de uso del sistema
- **Get Execution History** - Historial de ejecuciones
- **Get Detailed Costs** - Desglose detallado de costos

### ⚙️ System Configuration (Admin)
- **Get All Configs** - Todas las configuraciones
- **Get Specific Config** - Configuración específica
- **Create Config** - Nueva configuración
- **Update Config** - Actualizar configuración
- **Delete Config** - Eliminar configuración
- **Force Reload Config** - Recargar cache de config
- **Get Hot Reload Status** - Estado del hot reload

### 🏥 Health & Utility
- **Health Check** - Verificar estado de la API
- **API Documentation** - Acceder a Swagger UI
- **OpenAPI Schema** - Esquema OpenAPI en JSON

## 🔧 Variables de Entorno

### Variables Automáticas
- `access_token` - Se llena automáticamente al hacer login
- `user_id` - ID del usuario (se puede llenar manualmente)

### Variables Configurables
- `base_url` - URL base de tu API
- `username` - Tu nombre de usuario
- `password` - Tu contraseña
- `agent_id` - ID de agente por defecto para pruebas
- `tool_id` - ID de herramienta por defecto
- `template_id` - ID de template por defecto

## 📝 Ejemplos de Uso

### Crear un Agente
```json
{
    "name": "Asistente Virtual",
    "description": "Agente de propósito general",
    "system_prompt": "Eres un asistente virtual útil y amigable.",
    "personality": "Profesional pero cercano",
    "model_name": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 1000,
    "is_active": true,
    "tool_ids": []
}
```

### Crear una Herramienta HTTP
```json
{
    "name": "Weather API",
    "description": "Get current weather information",
    "endpoint_template": "https://api.openweathermap.org/data/2.5/weather",
    "method_allowed": "GET",
    "requires_auth": true,
    "auth_type": "api_key",
    "default_headers": {
        "Content-Type": "application/json"
    },
    "timeout_seconds": 30,
    "rate_limit_per_minute": 60,
    "is_active": true
}
```

### Ejecutar un Agente
```json
{
    "input_message": "¿Cuál es el clima en Madrid?",
    "context": {
        "user_location": "Spain",
        "language": "es",
        "timezone": "Europe/Madrid"
    }
}
```

## 🌟 Scripts Automáticos

La colección incluye scripts que:

- **Guardan automáticamente el token** después del login
- **Logging de respuestas** en la consola de Postman
- **Validación básica** de respuestas exitosas

## 🔍 Troubleshooting

### Error 401 (Unauthorized)
- Verifica que el token esté presente en las variables
- Haz login nuevamente si el token expiró

### Error 404 (Not Found)
- Verifica que la `base_url` sea correcta
- Asegúrate de que la API esté ejecutándose

### Error 403 (Forbidden)
- Verifica que tengas permisos suficientes
- Algunos endpoints requieren rol Admin

### Error de Conexión
- Verifica que la API esté ejecutándose en el puerto correcto
- Revisa configuración de firewall/proxy

## 🚀 Producción

Para usar en producción:

1. Cambia al entorno **"Agent System - Production"**
2. Actualiza `base_url` con tu dominio real
3. Usa credenciales de producción
4. Considera usar variables secretas para datos sensibles

## 📞 Soporte

Para problemas con la API:
1. Revisa logs del servidor
2. Usa el endpoint `/health` para verificar estado
3. Consulta la documentación en `/docs`

¡Listo para comenzar a probar tu API del Sistema de Agentes! 🎉