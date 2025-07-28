# Agent System - Sistema de Agentes Configurable

Sistema completo de agentes configurables con FastAPI, LangChain, y SQL Server.

## 🚀 Características Principales

### ✨ Sistema de Agentes Dinámicos
- Agentes completamente configurables desde base de datos
- Personalidad/rol del agente configurable
- Prompt system templates dinámicos
- Tools HTTP configurables por agente
- Parámetros de modelo ajustables (temperatura, max_tokens, etc.)
- Rate limits configurables por agente

### 🔧 Sistema de Tools HTTP
- Tools únicamente para llamadas HTTP
- Estructura estándar de entrada y salida
- Soporte para autenticación (Bearer, API Key, Basic)
- Timeout y rate limiting configurables

### 📝 Constructor de Prompts
- Templates de prompts con variables dinámicas `{variable_name}`
- Versionado de prompts
- Validación de templates
- Sistema de renderizado con variables

### 💰 Tracking de Costos
- Seguimiento detallado por llamada individual
- Costos por usuario/agente/tool
- Métricas de tokens consumidos
- Reportes de gastos con filtros

### 🔐 Seguridad y Autenticación
- JWT tokens para autenticación
- API Keys por usuario
- Encriptación AES-256 para credenciales
- Rate limiting configurable
- Roles: Admin, User, Viewer

### 📊 Hot Reload Configuration
- Configuración 100% desde base de datos
- Cambios reflejados sin reiniciar servidor
- Sistema de cache con recarga automática

## 📋 Requisitos

- Python 3.11+
- SQL Server (localhost)
- OpenAI API Key

## ⚡ Instalación Rápida

### 1. Clonar y configurar

```bash
git clone <repository>
cd Agente
python setup.py
```

### 2. Configurar base de datos

```bash
# Configurar SQL Server con usuario sa
python database/setup.py
```

### 3. Configurar variables de entorno

Editar archivo `.env`:

```env
DATABASE_URL=mssql+pyodbc://usrmon:MonAplic01@@localhost/AgentSystem?driver=ODBC+Driver+17+for+SQL+Server
OPENAI_API_KEY=tu_api_key_aqui
SECRET_KEY=clave-jwt-generada-automaticamente
ENCRYPTION_KEY=clave-encriptacion-generada-automaticamente
```

### 4. Ejecutar aplicación

```bash
# Desarrollo
python -m uvicorn app.main:app --reload

# Producción
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 🐳 Docker

```bash
# Crear .env con tus variables
cp .env.example .env

# Levantar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f agent-api
```

## 📖 API Endpoints

### Autenticación
- `POST /api/v1/auth/register` - Registro de usuarios
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Info del usuario

### Agentes
- `GET /api/v1/agents` - Listar agentes
- `POST /api/v1/agents` - Crear agente
- `GET /api/v1/agents/{id}` - Obtener agente
- `PUT /api/v1/agents/{id}` - Actualizar agente
- `DELETE /api/v1/agents/{id}` - Eliminar agente
- `POST /api/v1/agents/{id}/execute` - Ejecutar agente

### Tools
- `GET /api/v1/tools` - Listar tools
- `POST /api/v1/tools` - Crear tool
- `PUT /api/v1/tools/{id}` - Actualizar tool
- `DELETE /api/v1/tools/{id}` - Eliminar tool

### Prompt Templates
- `GET /api/v1/prompts` - Listar templates
- `POST /api/v1/prompts` - Crear template
- `PUT /api/v1/prompts/{id}` - Actualizar template
- `POST /api/v1/prompts/{id}/render` - Renderizar template
- `POST /api/v1/prompts/{id}/validate` - Validar template

### Métricas y Costos
- `GET /api/v1/metrics/costs` - Reporte de costos
- `GET /api/v1/metrics/usage` - Métricas de uso
- `GET /api/v1/metrics/executions` - Historial de ejecuciones

### Configuración (Solo Admin)
- `GET /api/v1/config` - Obtener todas las configuraciones
- `POST /api/v1/config` - Crear configuración
- `PUT /api/v1/config/{key}` - Actualizar configuración
- `DELETE /api/v1/config/{key}` - Eliminar configuración
- `POST /api/v1/config/reload` - Forzar recarga

## 🔧 Uso del Sistema

### 1. Crear un Agente

```json
POST /api/v1/agents
{
  "name": "Asistente Virtual",
  "description": "Agente de propósito general",
  "system_prompt": "Eres un asistente virtual útil y amigable.",
  "personality": "Profesional pero cercano",
  "model_name": "gpt-3.5-turbo",
  "temperature": 0.7,
  "max_tokens": 1000,
  "tool_ids": [1, 2]
}
```

### 2. Crear una Tool HTTP

```json
POST /api/v1/tools
{
  "name": "API Weather",
  "description": "Obtiene información del clima",
  "endpoint_template": "https://api.openweathermap.org/data/2.5/weather",
  "method_allowed": "GET",
  "requires_auth": true,
  "default_headers": {"Content-Type": "application/json"}
}
```

### 3. Ejecutar Agente

```json
POST /api/v1/agents/1/execute
{
  "input_message": "¿Cuál es el clima en Madrid?",
  "context": {
    "user_location": "Spain",
    "language": "es"
  }
}
```

### 4. Crear Template de Prompt

```json
POST /api/v1/prompts
{
  "name": "Email Respuesta",
  "template_content": "Responde al email de {customer_name} sobre {topic}. Tono: {tone}",
  "description": "Template para respuestas automáticas de email"
}
```

## 🏗️ Arquitectura

```
├── app/
│   ├── api/          # Endpoints de la API
│   ├── core/         # Configuración central
│   ├── models/       # Modelos SQLAlchemy
│   ├── schemas/      # Schemas Pydantic
│   ├── services/     # Lógica de negocio
│   └── utils/        # Utilidades
├── database/         # Scripts de base de datos
├── requirements.txt  # Dependencias Python
└── docker-compose.yml # Configuración Docker
```

## 🔐 Seguridad

- JWT tokens para autenticación de sesiones
- API Keys para integraciones
- Encriptación AES-256 para credenciales sensibles
- Rate limiting por IP y usuario
- Validación de schemas en todos los endpoints
- Roles de usuario granulares

## 📊 Monitoring

- Logs detallados de todas las operaciones
- Métricas de performance y uso
- Tracking de costos en tiempo real
- Health checks para monitoreo

## 🚨 Producción

### Variables de Entorno Importantes

```env
# Base de datos
DATABASE_URL=mssql+pyodbc://usuario:password@servidor/bd

# Seguridad (CAMBIAR EN PRODUCCIÓN)
SECRET_KEY=clave-jwt-super-secreta-cambiar
ENCRYPTION_KEY=clave-aes-256-base64-cambiar

# OpenAI
OPENAI_API_KEY=tu-api-key-real

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

### Configuración de Base de Datos

- Usuario dedicado con permisos mínimos
- Conexiones SSL habilitadas
- Backups automáticos configurados
- Monitoreo de performance

## 🤝 Contribuir

1. Fork el proyecto
2. Crear feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT.

## 🆘 Soporte

Para soporte técnico:
1. Revisar la documentación de la API en `/docs`
2. Verificar logs del sistema
3. Consultar los health checks en `/health`