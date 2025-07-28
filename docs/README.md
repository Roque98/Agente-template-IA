# 📚 Documentación del Sistema de Agentes

Esta carpeta contiene la documentación completa para implementar agentes SQL inteligentes con gestión avanzada de parámetros y contexto conversacional.

## 📋 Archivos Incluidos

### 🤖 [SQL_AGENT_TUTORIAL.md](./SQL_AGENT_TUTORIAL.md)
**Tutorial completo para crear agentes SQL inteligentes**

- **Arquitectura de 2 tools**: Schema Provider + Query Executor
- **Configuración del agente** con workflow inteligente
- **Ejemplos prácticos** de conversaciones naturales
- **Seguridad y mejores prácticas**
- **Troubleshooting** y optimización de performance

**Casos de uso:**
- "¿Cuántos usuarios activos tenemos este mes?"
- "¿Qué agentes han costado más dinero?"
- "¿Cuáles son los errores más comunes en las ejecuciones?"

### 📊 [SCHEMA_ENDPOINT_SPEC.md](./SCHEMA_ENDPOINT_SPEC.md)
**Especificación técnica del endpoint de esquema de base de datos**

- **Formato detallado** del endpoint `/api/schema/info`
- **Descripciones de negocio** personalizables por tabla/columna
- **Archivos de configuración** JSON organizados por tabla
- **Ejemplos completos** con contexto empresarial
- **Métricas y monitoreo** del uso del esquema

**Características:**
- Schema con descripciones de negocio
- Valores de ejemplo por columna
- Relaciones entre tablas explicadas
- Queries comunes sugeridas
- KPIs y alertas de negocio

### 🔧 [TOOL_PARAMETERS_GUIDE.md](./TOOL_PARAMETERS_GUIDE.md)
**Guía completa de gestión de parámetros y contexto conversacional**

- **Tipos de parámetros**: Fijos, variables, opcionales
- **Fuentes de datos**: Contexto, usuario, preferencias, configuración
- **Gestión de conversaciones** con historial por usuario
- **Extracción automática** de variables del lenguaje natural
- **Modelos de base de datos** extendidos
- **Servicios de contexto** y resolución de parámetros

**Tipos de parámetros soportados:**
- 🔒 **Fijos**: API keys, tokens, configuraciones
- 🔄 **Variables**: Datos del usuario, contexto, queries dinámicas
- ❓ **Opcionales**: Límites, timeouts, formatos con defaults

### ⚙️ [SQL_TOOLS_WITH_PARAMETERS.md](./SQL_TOOLS_WITH_PARAMETERS.md) 
**Configuración práctica de las tools SQL con parámetros avanzados**

- **Configuración JSON completa** de ambas tools SQL
- **Flujos de ejecución** paso a paso con ejemplos reales
- **Resolución automática** de parámetros desde múltiples fuentes
- **Manejo de errores** y parámetros faltantes
- **Casos de uso avanzados** con contexto conversacional

**Flujo de ejecución:**
1. Usuario pregunta en lenguaje natural
2. Sistema extrae variables del contexto
3. Agente llama Schema Provider (automático)
4. Agente genera SQL inteligente
5. Agente ejecuta Query Executor (con parámetros resueltos)
6. Sistema responde con insights de negocio

## 🚀 Implementación Rápida

### 1. **Crear las Tools** (10 min)
```bash
# Usar Postman con las configuraciones JSON de SQL_TOOLS_WITH_PARAMETERS.md
POST /api/v1/tools  # Schema Provider
POST /api/v1/tools  # Query Executor
```

### 2. **Implementar Endpoints** (30 min)
```bash
# Crear los servicios HTTP según especificaciones
GET  /api/schema/info      # Schema con descripciones  
POST /api/sql/execute      # Ejecución segura de SQL
```

### 3. **Configurar Agente** (5 min)
```bash
# Usar configuración JSON de SQL_AGENT_TUTORIAL.md
POST /api/v1/agents  # Agente SQL con ambas tools
```

### 4. **Extender Base de Datos** (15 min)
```sql
-- Aplicar migraciones de TOOL_PARAMETERS_GUIDE.md
ALTER TABLE tools ADD COLUMN parameter_schema JSON;
CREATE TABLE conversations (...);
CREATE TABLE conversation_messages (...);
CREATE TABLE tool_executions (...);
```

### 5. **Probar** (5 min)
```bash
# Ejecutar agente con preguntas naturales
POST /api/v1/agents/1/execute
{
    "input_message": "¿Cuántos usuarios administrativos tenemos?"
}
```

## 🎯 Funcionalidades Principales

### ✅ **Agente SQL Inteligente**
- Convierte preguntas naturales en SQL preciso
- Usa contexto de negocio para generar queries relevantes
- Explica resultados en términos empresariales
- Sugiere análisis adicionales

### ✅ **Sistema de Parámetros Avanzado**
- Resolución automática desde múltiples fuentes
- Encriptación segura de credenciales
- Validación y sanitización de inputs
- Manejo inteligente de parámetros faltantes

### ✅ **Gestión de Contexto Conversacional**
- Historial completo por usuario y conversación
- Extracción automática de variables del texto
- Continuidad contextual entre mensajes
- Persistencia de preferencias de usuario

### ✅ **Seguridad y Auditoría**
- Validación estricta de queries SQL (solo SELECT)
- Rate limiting por usuario y herramienta
- Logging completo de todas las operaciones
- Encriptación de datos sensibles

### ✅ **Performance y Monitoreo**
- Cache inteligente de schema de base de datos
- Métricas detalladas de uso y performance
- Timeouts configurables por herramienta
- Optimización automática de queries

## 📊 Arquitectura del Sistema

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Usuario       │    │   SQL Agent      │    │   Tools Layer   │
│                 │    │                  │    │                 │
│ "¿Cuántos       │───▶│ 1. Get Schema    │───▶│ Schema Provider │
│  usuarios?"     │    │ 2. Generate SQL  │    │ Query Executor  │
│                 │    │ 3. Execute Query │    │                 │
│                 │◀───│ 4. Explain Results│◀───│                 │
│ "1,247 usuarios"│    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                ▲
                                │
                    ┌───────────▼──────────┐
                    │  Context & Parameters│
                    │                      │
                    │ • Conversation History│
                    │ • Variable Extraction│  
                    │ • Parameter Resolution│
                    │ • User Preferences   │
                    └──────────────────────┘
```

## 🔄 Flujos de Conversación

### Flujo Básico
```
Usuario: "¿Cuántos usuarios activos tenemos?"
    ↓
Sistema: Extrae variables [usuarios, activos, count]
    ↓ 
Agente: Llama Schema Provider → Obtiene info tabla users
    ↓
Agente: Genera SQL → SELECT COUNT(*) FROM users WHERE is_active = 1
    ↓
Agente: Llama Query Executor → Ejecuta query
    ↓
Agente: "Tienes 1,247 usuarios activos. ¿Te gustaría analizar el crecimiento mensual?"
```

### Flujo con Contexto
```
Usuario: "Analiza usuarios de enero"
    ↓
Sistema: Extrae [usuarios, enero] → Guarda en contexto
    ↓
Usuario: "¿Cuántos están activos?"  
    ↓
Sistema: Usa contexto previo [usuarios + enero] + nueva consulta [activos]
    ↓
Agente: Genera SQL contextual → WHERE created_at LIKE '2024-01%' AND is_active = 1
```

### Flujo con Parámetros Faltantes
```
Usuario: "Consulta el clima"
    ↓
Tool Weather: Necesita parámetro "location" 
    ↓
Sistema: "Para consultar el clima, ¿para qué ciudad?"
    ↓
Usuario: "Madrid"
    ↓
Sistema: Guarda location="Madrid" → Ejecuta tool
```

## 📈 Casos de Uso Empresariales

### 🏢 **Reporting Ejecutivo**
- "¿Cuál es nuestro crecimiento de usuarios trimestral?"
- "¿Qué agentes están generando más costos?"
- "¿Cuáles son nuestros KPIs principales este mes?"

### 📊 **Análisis Operacional**  
- "¿Qué errores son más frecuentes en las ejecuciones?"
- "¿Cuándo tenemos picos de uso del sistema?"
- "¿Qué usuarios consumen más recursos?"

### 🔍 **Investigación de Datos**
- "Muéstrame patrones de uso por hora del día"
- "¿Hay correlación entre tipo de agente y tiempo de respuesta?"
- "¿Cuáles son las queries más lentas?"

### ⚡ **Monitoreo en Tiempo Real**
- "¿Cuántas ejecuciones fallaron en la última hora?"
- "¿Hay usuarios con comportamiento anómalo?"
- "¿El sistema está funcionando correctamente?"

## 🛠️ Próximos Pasos

1. **Implementar los endpoints** HTTP según especificaciones
2. **Aplicar migraciones** de base de datos para parámetros y contexto
3. **Configurar las tools** con los JSONs proporcionados
4. **Crear el agente SQL** con el prompt optimizado
5. **Probar con casos de uso** reales de tu organización
6. **Monitorear métricas** y optimizar performance
7. **Escalar** agregando más tools especializadas

## 📞 Soporte

Para implementación:
1. Revisar cada archivo de documentación paso a paso
2. Usar las configuraciones JSON exactas proporcionadas  
3. Probar cada componente individualmente antes de integrar
4. Monitorear logs durante las primeras ejecuciones
5. Ajustar parámetros según patrones de uso

¡Tu sistema de agentes SQL inteligente está listo para revolucionar cómo tu organización consulta y analiza datos! 🚀

---

**Generado con [Claude Code](https://claude.ai/code)**