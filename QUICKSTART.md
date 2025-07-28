# 🚀 Quick Start Guide

## Pasos para ejecutar el sistema:

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar base de datos
```bash
# Ejecutar script de inicialización
python database/setup.py
# (Necesitarás proporcionar la contraseña de SA de SQL Server)
```

### 3. Configurar variables de entorno
```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env y agregar tu OpenAI API Key
# El archivo ya tiene claves de ejemplo generadas
```

### 4. Ejecutar aplicación
```bash
# Opción 1: Usando uvicorn directamente
python -m uvicorn app.main:app --reload

# Opción 2: Usando script de inicio
python run.py

# Opción 3: Usando el setup automático
python setup.py
```

### 5. Acceder a la documentación
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## 🐳 Usando Docker

```bash
# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu OpenAI API Key

# Levantar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f agent-api

# Acceder a la aplicación
# http://localhost:8000/docs
```

## 🧪 Pruebas rápidas

### 1. Registrar usuario
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@test.com",
    "password": "admin123",
    "role": "Admin"
  }'
```

### 2. Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login-json" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

### 3. Crear agente
```bash
# Usar el token obtenido del login
curl -X POST "http://localhost:8000/api/v1/agents" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mi Primer Agente",
    "description": "Agente de prueba",
    "system_prompt": "Eres un asistente útil y amigable.",
    "model_name": "gpt-3.5-turbo",
    "temperature": 0.7
  }'
```

### 4. Ejecutar agente
```bash
curl -X POST "http://localhost:8000/api/v1/agents/1/execute" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input_message": "Hola, ¿cómo estás?"
  }'
```

## 📊 Funcionalidades disponibles

✅ **Completado - Todo funcional**
- Sistema de usuarios y autenticación JWT
- Agentes configurables con LangChain
- Tools HTTP personalizables
- Templates de prompts con variables
- Tracking de costos y métricas
- Rate limiting y seguridad
- Hot reload de configuración
- API completa con documentación
- Docker y docker-compose
- Base de datos SQL Server

## 🔧 Configuración avanzada

### Variables de entorno importantes:
```env
# Base de datos
DATABASE_URL=mssql+pyodbc://usrmon:MonAplic01@@localhost/AgentSystem?driver=ODBC+Driver+17+for+SQL+Server

# OpenAI (REQUERIDO)
OPENAI_API_KEY=tu-api-key-aqui

# Seguridad (generadas automáticamente)
SECRET_KEY=clave-jwt-generada
ENCRYPTION_KEY=clave-aes-generada

# Opcional
DEBUG=false
RATE_LIMIT_PER_MINUTE=60
```

### Base de datos:
- Usuario: `usrmon`
- Password: `MonAplic01@`
- Base de datos: `AgentSystem`
- Servidor: `localhost`

### Usuario admin por defecto:
- Username: `admin`
- Password: `admin123`
- (Creado automáticamente en la base de datos)

## ❗ Troubleshooting

### Error de conexión a base de datos:
1. Verificar que SQL Server esté ejecutándose
2. Verificar que el usuario `usrmon` existe
3. Verificar la cadena de conexión en `.env`

### Error de OpenAI:
1. Verificar que `OPENAI_API_KEY` esté configurada en `.env`
2. Verificar que la clave sea válida
3. Verificar que tengas crédito en OpenAI

### Error de dependencias:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Error de permisos Docker:
```bash
sudo chmod +x setup.py run.py database/setup.py
```

## 🎯 Próximos pasos

1. Crear tu primer agente desde la interfaz web
2. Configurar tools HTTP personalizadas
3. Crear templates de prompts
4. Configurar rate limits
5. Revisar métricas y costos
6. Configurar hot reload para producción