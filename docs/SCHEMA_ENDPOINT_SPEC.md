# 📊 Database Schema Endpoint - Especificación Técnica

Este documento define la especificación técnica del endpoint para proporcionar información del esquema de la base de datos con descripciones de negocio personalizables.

## 🎯 Propósito

El endpoint de esquema permite al agente SQL obtener información detallada sobre:
- **Estructura de tablas** con descripciones de negocio
- **Columnas** con contexto y ejemplos
- **Relaciones** entre tablas
- **Constraints** y reglas de negocio
- **Consultas comunes** sugeridas

## 📡 Especificación del Endpoint

### URL y Método
```
GET http://localhost:5000/api/schema/info
```

### Headers Requeridos
```
Authorization: Bearer {token}
Content-Type: application/json
Accept: application/json
```

### Parámetros Query (Opcionales)

| Parámetro | Tipo | Descripción | Default |
|-----------|------|-------------|---------|
| `include_samples` | boolean | Incluir valores de ejemplo en columnas | `true` |
| `include_relationships` | boolean | Incluir información de relaciones FK | `true` |
| `include_stats` | boolean | Incluir estadísticas de tabla (row count) | `false` |
| `table_filter` | string | Filtrar por nombres de tabla (regex) | `null` |

### Ejemplo de Request
```bash
curl -X GET "http://localhost:5000/api/schema/info?include_samples=true&include_stats=true" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json"
```

## 📄 Formato de Respuesta

### Respuesta Exitosa (200 OK)

```json
{
    "success": true,
    "schema": {
        "database_name": "AgentSystem",
        "description": "Sistema principal de agentes con gestión de usuarios, configuraciones y métricas",
        "version": "1.2",
        "last_updated": "2024-01-20T15:30:00Z",
        "tables": [
            {
                "name": "users",
                "description": "Usuarios del sistema con información de autenticación y perfil",
                "business_context": "Almacena todos los usuarios registrados incluyendo administradores, usuarios regulares y cuentas de servicio. Crítico para gestión de usuarios y autenticación. Los usuarios activos pueden crear y ejecutar agentes.",
                "category": "Authentication",
                "primary_key": "id",
                "row_count_estimate": 2543,
                "avg_row_size_kb": 0.8,
                "last_modified": "2024-01-20T10:15:00Z",
                "columns": [
                    {
                        "name": "id",
                        "type": "int",
                        "nullable": false,
                        "description": "Identificador único del usuario (auto-incremento)",
                        "business_meaning": "Clave primaria que identifica de forma única cada cuenta de usuario",
                        "is_primary_key": true,
                        "is_foreign_key": false,
                        "auto_increment": true,
                        "sample_values": [1, 2, 3, 4, 5],
                        "value_range": "1 - 9999"
                    },
                    {
                        "name": "username",
                        "type": "varchar(50)",
                        "nullable": false,
                        "description": "Nombre de usuario único para login (alfanumérico, 3-50 caracteres)",
                        "business_meaning": "Identificador de usuario para autenticación, debe ser único en el sistema",
                        "is_primary_key": false,
                        "is_foreign_key": false,
                        "unique": true,
                        "sample_values": ["admin", "john.doe", "data_analyst", "api_user", "report_viewer"],
                        "validation_rules": "Alfanumérico, puntos y guiones permitidos, 3-50 caracteres",
                        "common_patterns": ["nombre.apellido", "rol_usuario", "departamento_usuario"]
                    },
                    {
                        "name": "email",
                        "type": "varchar(255)",
                        "nullable": false,
                        "description": "Dirección de email del usuario, utilizada para notificaciones",
                        "business_meaning": "Email corporativo o personal para comunicaciones del sistema",
                        "is_primary_key": false,
                        "is_foreign_key": false,
                        "unique": true,
                        "sample_values": ["admin@company.com", "john.doe@company.com", "analyst@external.com"],
                        "validation_rules": "Formato de email válido, máximo 255 caracteres"
                    },
                    {
                        "name": "full_name",
                        "type": "varchar(100)",
                        "nullable": true,
                        "description": "Nombre completo del usuario para visualización",
                        "business_meaning": "Nombre real del usuario mostrado en la interfaz",
                        "sample_values": ["Administrador Sistema", "John Doe", "Ana García", "API Service"],
                        "common_usage": "Mostrar en saludos personalizados y reportes"
                    },
                    {
                        "name": "role",
                        "type": "varchar(20)",
                        "nullable": false,
                        "description": "Rol del usuario: Admin, User, o Viewer",
                        "business_meaning": "Define permisos y capacidades del usuario en el sistema",
                        "sample_values": ["Admin", "User", "Viewer"],
                        "constraints": "CHECK (role IN ('Admin', 'User', 'Viewer'))",
                        "role_permissions": {
                            "Admin": "Acceso completo, gestión de usuarios y configuración",
                            "User": "Crear y ejecutar agentes, ver métricas propias",
                            "Viewer": "Solo lectura, reportes básicos"
                        }
                    },
                    {
                        "name": "is_active",
                        "type": "bit",
                        "nullable": false,
                        "description": "Indica si la cuenta está activa (1) o deshabilitada (0)",
                        "business_meaning": "Control de acceso: solo usuarios activos pueden hacer login",
                        "sample_values": [1, 0],
                        "default_value": 1,
                        "business_rules": "Usuarios inactivos mantienen datos pero no pueden acceder"
                    },
                    {
                        "name": "last_login",
                        "type": "datetime",
                        "nullable": true,
                        "description": "Última fecha y hora de login del usuario",
                        "business_meaning": "Para auditoría y análisis de actividad de usuarios",
                        "sample_values": ["2024-01-20T09:30:00Z", "2024-01-19T16:45:00Z", null],
                        "common_usage": "Identificar usuarios inactivos, reportes de actividad"
                    },
                    {
                        "name": "created_at",
                        "type": "datetime",
                        "nullable": false,
                        "description": "Fecha y hora de creación de la cuenta",
                        "business_meaning": "Registro histórico de cuándo se creó cada usuario",
                        "sample_values": ["2024-01-15T10:30:00Z", "2024-02-01T14:20:00Z"],
                        "default_value": "GETDATE()",
                        "indexed": true
                    }
                ],
                "relationships": [
                    {
                        "type": "one_to_many",
                        "related_table": "agents",
                        "foreign_key": "created_by",
                        "description": "Un usuario puede crear múltiples agentes",
                        "business_impact": "Rastrear qué usuario creó cada agente para auditoría y permisos"
                    },
                    {
                        "type": "one_to_many",
                        "related_table": "executions",
                        "foreign_key": "user_id",
                        "description": "Un usuario puede tener múltiples ejecuciones de agentes",
                        "business_impact": "Tracking de uso por usuario para facturación y análisis"
                    },
                    {
                        "type": "one_to_many",
                        "related_table": "costs",
                        "foreign_key": "user_id",
                        "description": "Un usuario puede generar múltiples registros de costos",
                        "business_impact": "Cálculo de costos por usuario para billing"
                    }
                ],
                "indexes": [
                    {
                        "name": "IX_users_username",
                        "columns": ["username"],
                        "type": "unique",
                        "purpose": "Login rápido por username"
                    },
                    {
                        "name": "IX_users_email",
                        "columns": ["email"],
                        "type": "unique",
                        "purpose": "Búsqueda rápida por email"
                    },
                    {
                        "name": "IX_users_active_created",
                        "columns": ["is_active", "created_at"],
                        "type": "composite",
                        "purpose": "Reportes de usuarios activos por fecha"
                    }
                ],
                "common_queries": [
                    {
                        "description": "Usuarios activos",
                        "sql": "SELECT * FROM users WHERE is_active = 1",
                        "business_use": "Lista de usuarios que pueden acceder al sistema"
                    },
                    {
                        "description": "Administradores del sistema",
                        "sql": "SELECT username, email, full_name FROM users WHERE role = 'Admin' AND is_active = 1",
                        "business_use": "Contactos para soporte técnico y administración"
                    },
                    {
                        "description": "Usuarios recién registrados",
                        "sql": "SELECT * FROM users WHERE created_at >= DATEADD(day, -30, GETDATE()) ORDER BY created_at DESC",
                        "business_use": "Análisis de crecimiento de usuarios nuevos"
                    },
                    {
                        "description": "Usuarios inactivos por tiempo",
                        "sql": "SELECT username, email, last_login FROM users WHERE last_login < DATEADD(day, -90, GETDATE()) OR last_login IS NULL",
                        "business_use": "Identificar cuentas para limpieza o reactivación"
                    }
                ],
                "business_metrics": {
                    "kpis": [
                        "Total de usuarios activos",
                        "Nuevos registros por mes",
                        "Tasa de retención de usuarios",
                        "Distribución por roles"
                    ],
                    "alerts": [
                        "Usuarios admin inactivos por más de 30 días",
                        "Spike inusual en nuevos registros",
                        "Ratio admin/user fuera de rango normal"
                    ]
                }
            },
            {
                "name": "agents",
                "description": "Configuraciones de agentes de IA y sus parámetros",
                "business_context": "Almacena todos los agentes de IA configurados con sus prompts, configuraciones de modelo y herramientas asociadas. Cada agente representa un asistente de IA específico con capacidades definidas para tareas particulares.",
                "category": "AI Configuration",
                "primary_key": "id",
                "row_count_estimate": 45,
                "columns": [
                    {
                        "name": "id",
                        "type": "int",
                        "nullable": false,
                        "description": "Identificador único del agente",
                        "is_primary_key": true,
                        "sample_values": [1, 2, 3, 4, 5]
                    },
                    {
                        "name": "name",
                        "type": "varchar(100)",
                        "nullable": false,
                        "description": "Nombre legible del agente",
                        "business_meaning": "Nombre descriptivo que identifica el propósito del agente",
                        "sample_values": ["SQL Assistant", "Data Analyzer", "Report Generator", "Customer Support Bot"],
                        "naming_conventions": "Descriptivo del propósito, en inglés, máximo 100 caracteres"
                    },
                    {
                        "name": "description",
                        "type": "text",
                        "nullable": true,
                        "description": "Descripción detallada del agente y sus capacidades",
                        "business_meaning": "Explicación de qué hace el agente y cuándo usarlo",
                        "sample_values": [
                            "Asistente especializado en consultas SQL automáticas",
                            "Analiza datos y genera reportes ejecutivos",
                            "Bot de soporte que responde preguntas frecuentes"
                        ]
                    },
                    {
                        "name": "system_prompt",
                        "type": "text",
                        "nullable": false,
                        "description": "Prompt del sistema que define el comportamiento del agente",
                        "business_meaning": "Instrucciones técnicas que determinan cómo responde el agente",
                        "sensitive": true,
                        "max_length": 10000
                    },
                    {
                        "name": "model_name",
                        "type": "varchar(50)",
                        "nullable": false,
                        "description": "Modelo de IA utilizado (gpt-4, gpt-3.5-turbo, etc.)",
                        "business_meaning": "Determina capacidades y costos del agente",
                        "sample_values": ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"],
                        "cost_impact": {
                            "gpt-4": "Alto costo, máxima calidad",
                            "gpt-3.5-turbo": "Costo medio, buena calidad",
                            "gpt-4-turbo": "Costo alto, velocidad optimizada"
                        }
                    },
                    {
                        "name": "temperature",
                        "type": "decimal(3,2)",
                        "nullable": false,
                        "description": "Creatividad/aleatoriedad del modelo (0.0-1.0, menor = más enfocado)",
                        "business_meaning": "Controla qué tan creativas vs consistentes son las respuestas",
                        "sample_values": [0.1, 0.7, 0.9],
                        "recommendations": {
                            "0.0-0.2": "Tareas analíticas, SQL, matemáticas",
                            "0.3-0.7": "Conversación general, explicaciones",
                            "0.8-1.0": "Creatividad, brainstorming, escritura"
                        }
                    },
                    {
                        "name": "max_tokens",
                        "type": "int",
                        "nullable": false,
                        "description": "Máximo número de tokens en la respuesta",
                        "business_meaning": "Controla longitud y costo de las respuestas",
                        "sample_values": [500, 1000, 2000, 4000],
                        "cost_impact": "Más tokens = mayor costo por ejecución"
                    },
                    {
                        "name": "is_active",
                        "type": "bit",
                        "nullable": false,
                        "description": "Si el agente está disponible para uso",
                        "business_meaning": "Control de disponibilidad sin eliminar configuración",
                        "sample_values": [1, 0],
                        "default_value": 1
                    },
                    {
                        "name": "created_by",
                        "type": "int",
                        "nullable": false,
                        "description": "ID del usuario que creó este agente",
                        "is_foreign_key": true,
                        "references": "users.id",
                        "business_meaning": "Auditoría y permisos: quién puede modificar el agente"
                    },
                    {
                        "name": "created_at",
                        "type": "datetime",
                        "nullable": false,
                        "description": "Cuándo fue creado el agente",
                        "default_value": "GETDATE()",
                        "indexed": true
                    },
                    {
                        "name": "updated_at",
                        "type": "datetime",
                        "nullable": true,
                        "description": "Última modificación del agente",
                        "business_meaning": "Tracking de cambios para auditoría"
                    }
                ],
                "relationships": [
                    {
                        "type": "many_to_one",
                        "related_table": "users",
                        "foreign_key": "created_by",
                        "description": "Cada agente tiene un usuario creador",
                        "business_impact": "Permisos y ownership de agentes"
                    },
                    {
                        "type": "one_to_many",
                        "related_table": "executions",
                        "foreign_key": "agent_id",
                        "description": "Un agente puede tener múltiples ejecuciones",
                        "business_impact": "Métricas de uso y performance por agente"
                    },
                    {
                        "type": "many_to_many",
                        "related_table": "tools",
                        "through_table": "agent_tools",
                        "description": "Los agentes pueden usar múltiples herramientas",
                        "business_impact": "Define capacidades específicas de cada agente"
                    }
                ],
                "common_queries": [
                    {
                        "description": "Agentes activos por usuario",
                        "sql": "SELECT a.name, a.description, u.username FROM agents a JOIN users u ON a.created_by = u.id WHERE a.is_active = 1",
                        "business_use": "Ver qué agentes están disponibles y quién los creó"
                    },
                    {
                        "description": "Agentes más costosos",
                        "sql": "SELECT name, model_name, max_tokens FROM agents WHERE model_name = 'gpt-4' AND is_active = 1",
                        "business_use": "Identificar agentes que pueden generar costos altos"
                    },
                    {
                        "description": "Agentes sin uso reciente",
                        "sql": "SELECT a.name FROM agents a LEFT JOIN executions e ON a.id = e.agent_id WHERE e.created_at < DATEADD(day, -30, GETDATE()) OR e.id IS NULL",
                        "business_use": "Identificar agentes subutilizados para optimización"
                    }
                ]
            }
        ],
        "relationships_summary": [
            {
                "from_table": "users",
                "to_table": "agents", 
                "relationship": "one_to_many",
                "description": "Los usuarios crean y poseen agentes"
            },
            {
                "from_table": "agents",
                "to_table": "executions",
                "relationship": "one_to_many", 
                "description": "Los agentes generan múltiples ejecuciones"
            },
            {
                "from_table": "users",
                "to_table": "executions",
                "relationship": "one_to_many",
                "description": "Los usuarios solicitan ejecuciones de agentes"
            }
        ],
        "business_glossary": {
            "agent": "Programa de IA configurado para realizar tareas específicas",
            "execution": "Una instancia de uso de un agente para procesar una solicitud",
            "temperature": "Parámetro que controla la creatividad vs consistencia de las respuestas de IA",
            "tokens": "Unidades de texto procesadas por los modelos de IA, base para cálculo de costos",
            "system_prompt": "Instrucciones que definen el comportamiento y personalidad del agente"
        },
        "metadata": {
            "total_tables": 2,
            "total_columns": 23,
            "total_relationships": 6,
            "database_size_mb": 145.7,
            "last_analyzed": "2024-01-20T15:30:00Z",
            "schema_version": "1.2.0"
        }
    }
}
```

### Respuestas de Error

#### Error de Autenticación (401)
```json
{
    "success": false,
    "error": {
        "code": "UNAUTHORIZED",
        "message": "Invalid or missing authentication token"
    }
}
```

#### Error de Base de Datos (500)
```json
{
    "success": false,
    "error": {
        "code": "DATABASE_ERROR", 
        "message": "Could not connect to database",
        "details": "Connection timeout after 30 seconds"
    },
    "retry_after": 60
}
```

## 🔧 Implementación del Endpoint

### Estructura de Archivos de Configuración

El endpoint debe leer la información del esquema desde archivos de configuración personalizables:

```
schema_config/
├── database.json          # Configuración general de la BD
├── tables/
│   ├── users.json        # Configuración específica de tabla users
│   ├── agents.json       # Configuración específica de tabla agents
│   └── executions.json   # Configuración específica de tabla executions
└── relationships.json    # Definición de relaciones entre tablas
```

### Ejemplo: database.json
```json
{
    "name": "AgentSystem",
    "description": "Sistema principal de agentes con gestión de usuarios, configuraciones y métricas",
    "version": "1.2.0",
    "categories": {
        "Authentication": "Tablas relacionadas con usuarios y autenticación",
        "AI Configuration": "Configuración de agentes y herramientas de IA",
        "Execution": "Historial y métricas de ejecuciones",
        "Billing": "Tracking de costos y facturación"
    },
    "business_glossary": {
        "agent": "Programa de IA configurado para realizar tareas específicas",
        "execution": "Una instancia de uso de un agente para procesar una solicitud",
        "temperature": "Parámetro que controla la creatividad vs consistencia de las respuestas de IA"
    }
}
```

### Ejemplo: tables/users.json
```json
{
    "name": "users",
    "description": "Usuarios del sistema con información de autenticación y perfil",
    "business_context": "Almacena todos los usuarios registrados incluyendo administradores, usuarios regulares y cuentas de servicio. Crítico para gestión de usuarios y autenticación.",
    "category": "Authentication",
    "columns": {
        "id": {
            "description": "Identificador único del usuario (auto-incremento)",
            "business_meaning": "Clave primaria que identifica de forma única cada cuenta de usuario",
            "sample_values": [1, 2, 3, 4, 5]
        },
        "username": {
            "description": "Nombre de usuario único para login (alfanumérico, 3-50 caracteres)",
            "business_meaning": "Identificador de usuario para autenticación, debe ser único en el sistema",
            "sample_values": ["admin", "john.doe", "data_analyst"],
            "validation_rules": "Alfanumérico, puntos y guiones permitidos, 3-50 caracteres"
        },
        "role": {
            "description": "Rol del usuario: Admin, User, o Viewer",
            "business_meaning": "Define permisos y capacidades del usuario en el sistema",
            "sample_values": ["Admin", "User", "Viewer"],
            "role_permissions": {
                "Admin": "Acceso completo, gestión de usuarios y configuración",
                "User": "Crear y ejecutar agentes, ver métricas propias", 
                "Viewer": "Solo lectura, reportes básicos"
            }
        }
    },
    "common_queries": [
        {
            "description": "Usuarios activos",
            "sql": "SELECT * FROM users WHERE is_active = 1",
            "business_use": "Lista de usuarios que pueden acceder al sistema"
        },
        {
            "description": "Administradores del sistema",
            "sql": "SELECT username, email, full_name FROM users WHERE role = 'Admin' AND is_active = 1",
            "business_use": "Contactos para soporte técnico y administración"
        }
    ],
    "business_metrics": {
        "kpis": [
            "Total de usuarios activos",
            "Nuevos registros por mes",
            "Tasa de retención de usuarios"
        ],
        "alerts": [
            "Usuarios admin inactivos por más de 30 días",
            "Spike inusual en nuevos registros"
        ]
    }
}
```

## 🚀 Casos de Uso

### 1. Inicialización del Agente
```javascript
// El agente llama al endpoint al iniciar una conversación
const schemaInfo = await fetch('/api/schema/info');
// Usa la información para entender qué datos están disponibles
```

### 2. Generación de Queries Contextuales
```javascript
// Basado en el schema, el agente sabe que:
// users.role tiene valores ["Admin", "User", "Viewer"]
// users.is_active es boolean (0/1)
// Puede generar queries más precisas
```

### 3. Explicaciones de Negocio
```javascript
// El agente puede explicar:
// "La tabla 'executions' rastrea cada vez que un agente procesa una solicitud,
//  incluyendo métricas de performance y costos para facturación"
```

## 🔒 Seguridad

### Validaciones Requeridas
- ✅ Autenticación JWT válida
- ✅ Rate limiting (30 requests/min por usuario)
- ✅ No exponer información sensible (passwords, secrets)
- ✅ Sanitizar sample_values si contienen datos reales

### Información Sensible
```json
{
    "columns": [
        {
            "name": "password_hash",
            "description": "Hash de contraseña (SHA-256)",
            "sensitive": true,
            "sample_values": ["*** HIDDEN ***"]
        }
    ]
}
```

## 🎯 Mejores Prácticas

### Para el Endpoint
1. **Cache**: Cachear respuesta por 30 minutos
2. **Compresión**: Usar gzip para respuestas grandes
3. **Versionado**: Incluir version en respuesta para compatibilidad
4. **Monitoreo**: Log de accesos para auditoría
5. **Documentación**: Mantener archivos de configuración actualizados

### Para los Archivos de Configuración
1. **Versionado**: Usar control de versiones para cambios
2. **Validación**: Validar JSON al arrancar el servicio
3. **Backup**: Backup automático antes de cambios
4. **Review**: Proceso de revisión para cambios de schema
5. **Testing**: Tests automáticos para verificar consistencia

## 📊 Métricas y Monitoreo

### Métricas a Trackear
- Requests por minuto al endpoint
- Tiempo de respuesta promedio
- Errores por tipo
- Tablas más consultadas
- Usuarios más activos

### Logs Recomendados
```json
{
    "timestamp": "2024-01-20T15:30:00Z",
    "user_id": "user123",
    "endpoint": "/api/schema/info",
    "response_time_ms": 145,
    "status": "success",
    "tables_requested": ["users", "agents"],
    "include_samples": true
}
```

Este endpoint será fundamental para que el agente SQL tenga contexto completo sobre los datos disponibles y pueda generar queries más precisas y explicaciones más claras. 🚀