# 🗃️ Tutorial: Agente SQL con Consultas Automáticas

Este tutorial te guiará paso a paso para crear un agente inteligente que puede consultar automáticamente tu base de datos SQL Server, generar queries dinámicas y devolver respuestas basadas en los datos.

## 📋 Índice

1. [Resumen del Sistema](#resumen-del-sistema)
2. [Arquitectura del Agente SQL](#arquitectura-del-agente-sql)
3. [Paso 1: Crear la Tool SQL](#paso-1-crear-la-tool-sql)
4. [Paso 2: Implementar el Endpoint](#paso-2-implementar-el-endpoint)
5. [Paso 3: Configurar el Agente](#paso-3-configurar-el-agente)
6. [Paso 4: Prompt Engineering](#paso-4-prompt-engineering)
7. [Ejemplos Prácticos](#ejemplos-prácticos)
8. [Seguridad y Mejores Prácticas](#seguridad-y-mejores-prácticas)
9. [Troubleshooting](#troubleshooting)

## Resumen del Sistema

### ¿Qué hace este agente?

El agente SQL puede:
- 📊 Recibir preguntas en lenguaje natural sobre tus datos
- 🧠 Analizar el esquema de tu base de datos
- 🔍 Generar queries SQL apropiadas automáticamente  
- ⚡ Ejecutar las consultas de forma segura
- 📝 Interpretar y presentar los resultados en lenguaje natural
- 🔄 Manejar consultas complejas con JOINs, filtros y agregaciones

### Flujo de Trabajo

```
Usuario: "¿Cuántos usuarios activos tenemos este mes?"
    ↓
Agente: Analiza pregunta + esquema DB
    ↓
Agente: Genera SQL → SELECT COUNT(*) FROM users WHERE is_active=1 AND created_at >= '2024-01-01'
    ↓
Tool SQL: Ejecuta query en la base de datos
    ↓
Agente: "Tienes 1,247 usuarios activos este mes, un aumento del 15% respecto al mes anterior."
```

## Arquitectura del Agente SQL

### Componentes

1. **SQL Query Tool** - Herramienta HTTP que ejecuta queries
2. **Schema Service** - Servicio que proporciona información del esquema
3. **SQL Agent** - Agente inteligente con prompt especializado
4. **Security Layer** - Validación y sanitización de queries

### Diagrama de Arquitectura

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Usuario       │    │   SQL Agent      │    │   SQL Tool      │
│                 │    │                  │    │                 │
│ "¿Cuántos       │───▶│ 1. Analiza       │───▶│ 1. Valida query │
│  usuarios?"     │    │    pregunta      │    │ 2. Ejecuta      │
│                 │    │ 2. Genera SQL    │    │ 3. Retorna JSON │
│                 │◀───│ 3. Interpreta    │◀───│                 │
│ "1,247 usuarios"│    │    resultados    │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                ▲
                                │
                       ┌────────▼────────┐
                       │  Schema Service │
                       │                 │
                       │ • Table info    │
                       │ • Column info   │  
                       │ • Relationships │
                       └─────────────────┘
```

## Paso 1: Crear las Tools SQL

### 1.1 Tool 1: Database Schema Provider

Esta tool proporciona información del esquema de la base de datos con descripciones personalizables:

**Endpoint**: `POST /api/v1/tools`

```json
{
    "name": "Database Schema Provider",
    "description": "Provides detailed database schema information including table descriptions, column details, relationships, and business context. Essential for understanding what data is available for queries.",
    "endpoint_template": "http://localhost:5000/api/schema/info",
    "method_allowed": "GET",
    "requires_auth": true,
    "auth_type": "bearer",
    "default_headers": {
        "Content-Type": "application/json",
        "Accept": "application/json"
    },
    "timeout_seconds": 15,
    "rate_limit_per_minute": 30,
    "is_active": true
}
```

### 1.2 Tool 2: SQL Query Executor

Esta tool ejecuta las queries SQL generadas por el agente:

**Endpoint**: `POST /api/v1/tools`

```json
{
    "name": "SQL Query Executor",
    "description": "Executes SQL SELECT queries against the main database and returns results in JSON format. Includes safety validations and performance optimizations.",
    "endpoint_template": "http://localhost:5000/api/sql/execute",
    "method_allowed": "POST",
    "requires_auth": true,
    "auth_type": "bearer",
    "default_headers": {
        "Content-Type": "application/json",
        "Accept": "application/json"
    },
    "timeout_seconds": 30,
    "rate_limit_per_minute": 20,
    "is_active": true
}
```

## Paso 2: Implementar los Endpoints

### 2.1 Endpoint 1: Database Schema Provider

**URL**: `http://localhost:5000/api/schema/info`  
**Método**: `GET`  
**Autenticación**: Bearer Token  

#### Request Format

Sin parámetros requeridos. Opcionalmente puede incluir:

```
GET /api/schema/info?include_samples=true&include_relationships=true
```

#### Response Format

```json
{
    "success": true,
    "schema": {
        "database_name": "AgentSystem",
        "description": "Main application database containing user data, agent configurations, and execution history",
        "tables": [
            {
                "name": "users",
                "description": "System users with authentication and profile information",
                "business_context": "Contains all registered users including admins, regular users, and service accounts. Critical for user management and authentication.",
                "primary_key": "id",
                "row_count_estimate": 2543,
                "columns": [
                    {
                        "name": "id",
                        "type": "int",
                        "nullable": false,
                        "description": "Unique user identifier (auto-increment)",
                        "is_primary_key": true,
                        "sample_values": [1, 2, 3, 4, 5]
                    },
                    {
                        "name": "username",
                        "type": "varchar(50)",
                        "nullable": false,
                        "description": "Unique username for login (alphanumeric, 3-50 chars)",
                        "sample_values": ["admin", "john.doe", "data_analyst", "api_user"]
                    },
                    {
                        "name": "email",
                        "type": "varchar(255)",
                        "nullable": false,
                        "description": "User's email address, used for notifications",
                        "sample_values": ["admin@company.com", "john@company.com"]
                    },
                    {
                        "name": "role",
                        "type": "varchar(20)",
                        "nullable": false,
                        "description": "User role: Admin, User, or Viewer",
                        "sample_values": ["Admin", "User", "Viewer"],
                        "constraints": "CHECK (role IN ('Admin', 'User', 'Viewer'))"
                    },
                    {
                        "name": "is_active",
                        "type": "bit",
                        "nullable": false,
                        "description": "Whether user account is active (1) or disabled (0)",
                        "sample_values": [1, 0]
                    },
                    {
                        "name": "created_at",
                        "type": "datetime",
                        "nullable": false,
                        "description": "When the user account was created",
                        "sample_values": ["2024-01-15T10:30:00Z", "2024-02-01T14:20:00Z"]
                    }
                ],
                "relationships": [
                    {
                        "type": "one_to_many",
                        "related_table": "agents",
                        "foreign_key": "created_by",
                        "description": "Users can create multiple agents"
                    },
                    {
                        "type": "one_to_many", 
                        "related_table": "executions",
                        "foreign_key": "user_id",
                        "description": "Users can have multiple agent executions"
                    }
                ],
                "common_queries": [
                    "Find active users: WHERE is_active = 1",
                    "Find admins: WHERE role = 'Admin'",
                    "Recent users: WHERE created_at >= DATEADD(day, -30, GETDATE())"
                ]
            },
            {
                "name": "agents",
                "description": "AI agent configurations and settings",
                "business_context": "Stores all configured AI agents with their prompts, model settings, and associated tools. Each agent represents a specific AI assistant with defined capabilities.",
                "primary_key": "id",
                "row_count_estimate": 45,
                "columns": [
                    {
                        "name": "id",
                        "type": "int",
                        "nullable": false,
                        "description": "Unique agent identifier",
                        "is_primary_key": true
                    },
                    {
                        "name": "name",
                        "type": "varchar(100)",
                        "nullable": false,
                        "description": "Human-readable agent name",
                        "sample_values": ["SQL Assistant", "Data Analyzer", "Report Generator"]
                    },
                    {
                        "name": "model_name",
                        "type": "varchar(50)",
                        "nullable": false,
                        "description": "AI model used (gpt-4, gpt-3.5-turbo, etc.)",
                        "sample_values": ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"]
                    },
                    {
                        "name": "temperature",
                        "type": "decimal(3,2)",
                        "nullable": false,
                        "description": "Model creativity/randomness (0.0-1.0, lower = more focused)",
                        "sample_values": [0.1, 0.7, 0.9]
                    },
                    {
                        "name": "is_active",
                        "type": "bit",
                        "nullable": false,
                        "description": "Whether agent is available for use",
                        "sample_values": [1, 0]
                    },
                    {
                        "name": "created_by",
                        "type": "int",
                        "nullable": false,
                        "description": "ID of user who created this agent",
                        "is_foreign_key": true,
                        "references": "users.id"
                    }
                ]
            },
            {
                "name": "executions",
                "description": "History of agent execution requests and results",
                "business_context": "Tracks every time an agent is executed, including input, output, performance metrics, and costs. Essential for analytics, debugging, and billing.",
                "primary_key": "id",
                "row_count_estimate": 15678,
                "columns": [
                    {
                        "name": "id",
                        "type": "int",
                        "nullable": false,
                        "description": "Unique execution identifier",
                        "is_primary_key": true
                    },
                    {
                        "name": "agent_id",
                        "type": "int",
                        "nullable": false,
                        "description": "Which agent was executed",
                        "is_foreign_key": true,
                        "references": "agents.id"
                    },
                    {
                        "name": "user_id",
                        "type": "int",
                        "nullable": false,
                        "description": "Which user requested the execution",
                        "is_foreign_key": true,
                        "references": "users.id"
                    },
                    {
                        "name": "status",
                        "type": "varchar(20)",
                        "nullable": false,
                        "description": "Execution status: pending, running, completed, failed",
                        "sample_values": ["completed", "failed", "pending"]
                    },
                    {
                        "name": "tokens_used",
                        "type": "int",
                        "nullable": true,
                        "description": "Total tokens consumed (input + output)"
                    },
                    {
                        "name": "cost",
                        "type": "decimal(10,6)",
                        "nullable": true,
                        "description": "Execution cost in USD"
                    },
                    {
                        "name": "execution_time_ms",
                        "type": "int",
                        "nullable": true,
                        "description": "How long the execution took in milliseconds"
                    },
                    {
                        "name": "created_at",
                        "type": "datetime",
                        "nullable": false,
                        "description": "When the execution was started"
                    }
                ]
            }
        ],
        "generated_at": "2024-01-20T15:30:00Z",
        "version": "1.0"
    }
}
```

### 2.2 Endpoint 2: SQL Query Executor

**URL**: `http://localhost:5000/api/sql/execute`  
**Método**: `POST`  
**Autenticación**: Bearer Token  

#### Request Format

```json
{
    "query": "string",           // SQL query to execute
    "parameters": {
        "limit": 1000,          // Optional: max rows to return
        "safe_mode": true,      // Optional: enable safety checks
        "timeout": 30           // Optional: query timeout in seconds
    }
}
```

### 2.3 Response Format

#### Respuesta Exitosa (200 OK)

```json
{
    "success": true,
    "data": {
        "rows": [
            {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "created_at": "2024-01-15T10:30:00Z"
            },
            {
                "id": 2,
                "name": "Jane Smith", 
                "email": "jane@example.com",
                "created_at": "2024-01-16T14:20:00Z"
            }
        ],
        "columns": [
            {"name": "id", "type": "int"},
            {"name": "name", "type": "varchar"},
            {"name": "email", "type": "varchar"},
            {"name": "created_at", "type": "datetime"}
        ],
        "row_count": 2,
        "execution_time_ms": 45,
        "query_hash": "abc123..."
    },
    "metadata": {
        "query": "SELECT id, name, email, created_at FROM users LIMIT 2",
        "executed_at": "2024-01-20T15:30:00Z",
        "safe_mode": true
    }
}
```

#### Respuesta de Error (400/500)

```json
{
    "success": false,
    "error": {
        "code": "INVALID_QUERY",
        "message": "SQL syntax error near 'SELCT'",
        "details": "Line 1, Position 1: Expected SELECT, got SELCT"
    },
    "metadata": {
        "query": "SELCT * FROM users",
        "attempted_at": "2024-01-20T15:30:00Z"
    }
}
```

### 2.4 Códigos de Error

| Código | Descripción | HTTP Status |
|--------|-------------|-------------|
| `INVALID_QUERY` | Syntax error en SQL | 400 |
| `UNAUTHORIZED_OPERATION` | Query no permitida (INSERT/UPDATE/DELETE) | 403 |
| `TABLE_NOT_FOUND` | Tabla no existe | 404 |
| `QUERY_TIMEOUT` | Query excedió tiempo límite | 408 |
| `DATABASE_ERROR` | Error interno de BD | 500 |
| `CONNECTION_ERROR` | No se pudo conectar a BD | 503 |

### 2.5 Implementación del Endpoint (Python Flask)

```python
from flask import Flask, request, jsonify
import pyodbc
import json
import time
import re
from datetime import datetime

app = Flask(__name__)

# Configuración de la base de datos
DB_CONFIG = {
    'server': 'localhost',
    'database': 'AgentSystem',
    'username': 'usrmon',
    'password': 'MonAplic01@'
}

class SQLQueryExecutor:
    def __init__(self):
        self.connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_CONFIG['server']};DATABASE={DB_CONFIG['database']};UID={DB_CONFIG['username']};PWD={DB_CONFIG['password']}"
    
    def validate_query(self, query):
        """Valida que la query sea segura (solo SELECT)"""
        query_upper = query.upper().strip()
        
        # Solo permitir SELECT
        if not query_upper.startswith('SELECT'):
            return False, "Only SELECT queries are allowed"
        
        # Prohibir operaciones peligrosas
        dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE', 'EXEC', 'EXECUTE']
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                return False, f"Keyword '{keyword}' not allowed"
        
        return True, "Query is valid"
    
    def execute_query(self, query, limit=1000, safe_mode=True, timeout=30):
        """Ejecuta la query y retorna resultados"""
        try:
            # Validar query si está en modo seguro
            if safe_mode:
                is_valid, message = self.validate_query(query)
                if not is_valid:
                    return {
                        "success": False,
                        "error": {
                            "code": "UNAUTHORIZED_OPERATION",
                            "message": message
                        }
                    }
            
            # Agregar LIMIT si no existe
            if 'LIMIT' not in query.upper() and limit:
                query = f"SELECT TOP {limit} * FROM ({query}) as limited_query"
            
            start_time = time.time()
            
            # Conectar y ejecutar
            with pyodbc.connect(self.connection_string, timeout=timeout) as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                
                # Obtener columnas
                columns = [{"name": desc[0], "type": str(desc[1])} for desc in cursor.description]
                
                # Obtener filas
                rows = []
                for row in cursor.fetchall():
                    row_dict = {}
                    for i, value in enumerate(row):
                        if isinstance(value, datetime):
                            row_dict[columns[i]["name"]] = value.isoformat()
                        else:
                            row_dict[columns[i]["name"]] = value
                    rows.append(row_dict)
                
                execution_time = int((time.time() - start_time) * 1000)
                
                return {
                    "success": True,
                    "data": {
                        "rows": rows,
                        "columns": columns,
                        "row_count": len(rows),
                        "execution_time_ms": execution_time,
                        "query_hash": hash(query)
                    },
                    "metadata": {
                        "query": query,
                        "executed_at": datetime.now().isoformat(),
                        "safe_mode": safe_mode
                    }
                }
                
        except pyodbc.Error as e:
            return {
                "success": False,
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": str(e)
                },
                "metadata": {
                    "query": query,
                    "attempted_at": datetime.now().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": str(e)
                }
            }

@app.route('/api/sql/execute', methods=['POST'])
def execute_sql():
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                "success": False,
                "error": {
                    "code": "MISSING_QUERY",
                    "message": "Query parameter is required"
                }
            }), 400
        
        query = data['query']
        parameters = data.get('parameters', {})
        
        limit = parameters.get('limit', 1000)
        safe_mode = parameters.get('safe_mode', True)
        timeout = parameters.get('timeout', 30)
        
        executor = SQLQueryExecutor()
        result = executor.execute_query(query, limit, safe_mode, timeout)
        
        if result['success']:
            return jsonify(result), 200
        else:
            status_code = 400
            if result['error']['code'] == 'DATABASE_ERROR':
                status_code = 500
            elif result['error']['code'] == 'UNAUTHORIZED_OPERATION':
                status_code = 403
                
            return jsonify(result), status_code
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }), 500

@app.route('/api/sql/schema', methods=['GET'])
def get_schema():
    """Endpoint para obtener información del esquema de la base de datos"""
    try:
        executor = SQLQueryExecutor()
        
        # Query para obtener todas las tablas y sus columnas
        schema_query = """
        SELECT 
            t.TABLE_NAME,
            c.COLUMN_NAME,
            c.DATA_TYPE,
            c.IS_NULLABLE,
            c.COLUMN_DEFAULT,
            CASE 
                WHEN pk.COLUMN_NAME IS NOT NULL THEN 'YES'
                ELSE 'NO'
            END AS IS_PRIMARY_KEY
        FROM INFORMATION_SCHEMA.TABLES t
        LEFT JOIN INFORMATION_SCHEMA.COLUMNS c ON t.TABLE_NAME = c.TABLE_NAME
        LEFT JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE pk ON c.TABLE_NAME = pk.TABLE_NAME 
            AND c.COLUMN_NAME = pk.COLUMN_NAME
            AND pk.CONSTRAINT_NAME LIKE 'PK_%'
        WHERE t.TABLE_TYPE = 'BASE TABLE'
        ORDER BY t.TABLE_NAME, c.ORDINAL_POSITION
        """
        
        result = executor.execute_query(schema_query, limit=None, safe_mode=False)
        
        if result['success']:
            # Organizar por tablas
            tables = {}
            for row in result['data']['rows']:
                table_name = row['TABLE_NAME']
                if table_name not in tables:
                    tables[table_name] = {
                        'name': table_name,
                        'columns': []
                    }
                
                tables[table_name]['columns'].append({
                    'name': row['COLUMN_NAME'],
                    'type': row['DATA_TYPE'],
                    'nullable': row['IS_NULLABLE'] == 'YES',
                    'default': row['COLUMN_DEFAULT'],
                    'is_primary_key': row['IS_PRIMARY_KEY'] == 'YES'
                })
            
            return jsonify({
                "success": True,
                "schema": {
                    "tables": list(tables.values()),
                    "table_count": len(tables),
                    "generated_at": datetime.now().isoformat()
                }
            }), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {
                "code": "SCHEMA_ERROR",
                "message": str(e)
            }
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

## Paso 3: Configurar el Agente

### 3.1 Crear el Agente SQL

**Endpoint**: `POST /api/v1/agents`

```json
{
    "name": "SQL Database Assistant",
    "description": "Intelligent agent that can query the database using natural language questions and return human-readable answers with full context",
    "system_prompt": "You are an expert SQL Database Assistant with access to comprehensive database schema information and query execution capabilities.\n\n## Your Tools:\n1. **Database Schema Provider** - Get detailed schema information with business context\n2. **SQL Query Executor** - Execute SQL SELECT queries safely\n\n## Workflow for Every Query:\n1. **First, ALWAYS call the Database Schema Provider** to get current schema information\n2. **Understand the user's question** in business terms\n3. **Generate appropriate SQL** using the schema information\n4. **Execute the query** using the SQL Query Executor\n5. **Interpret and present results** in a business-friendly format\n\n## Key Capabilities:\n- Convert natural language questions into precise SQL queries\n- Understand business context from table and column descriptions\n- Execute queries with proper safety validations\n- Provide meaningful insights from query results\n- Suggest follow-up analyses and related questions\n\n## Query Generation Rules:\n1. **Always start with schema**: Call Database Schema Provider first\n2. **Safety first**: Only generate SELECT statements\n3. **Use descriptions**: Leverage table/column descriptions for context\n4. **Proper joins**: Use relationships information for accurate joins\n5. **Business logic**: Apply business context from schema descriptions\n6. **Performance**: Include appropriate LIMIT clauses\n7. **Clarity**: Use table aliases and descriptive column names\n\n## Response Format:\nFor each user question:\n1. **Schema Check**: \"Let me first check the current database schema...\"\n2. **Understanding**: Restate the question in business terms\n3. **Query Planning**: Explain which tables/columns you'll use and why\n4. **Query Execution**: Show and execute the SQL query\n5. **Results**: Present findings in natural language\n6. **Business Insights**: Provide relevant business insights\n7. **Follow-up**: Suggest related questions or deeper analyses\n\n## Error Handling:\n- If schema call fails, explain the limitation and ask for manual schema info\n- If query fails, analyze the error and provide corrected version\n- Always explain technical issues in business-friendly terms\n\n## Example Interaction:\nUser: \"How many active users do we have?\"\n\nResponse:\n\"Let me first check the database schema to understand our user data structure...\n\n[Calls Database Schema Provider]\n\nBased on the schema, I can see we have a 'users' table with an 'is_active' column that tracks user status. Let me query this information:\n\n```sql\nSELECT COUNT(*) as active_users \nFROM users \nWHERE is_active = 1\n```\n\n[Executes query]\n\nYou currently have 1,247 active users in your system. This represents users who can actively use the platform.\n\nWould you like me to analyze:\n- User growth trends over time\n- Active vs inactive user ratio\n- Recent user activity patterns\"\n\nRemember: Always use both tools appropriately and provide business value in your responses.",
    "personality": "Professional data analyst who explains technical concepts clearly and focuses on business value. Methodical in approach, always starts with understanding the data structure before querying.",
    "model_name": "gpt-4",
    "temperature": 0.1,
    "max_tokens": 3000,
    "is_active": true,
    "tool_ids": [1, 2]
}
```

### 3.2 Configuración de Parámetros

| Parámetro | Valor | Razón |
|-----------|-------|--------|
| `temperature` | 0.1 | Baja temperatura para respuestas precisas y consistentes |
| `max_tokens` | 2000 | Suficiente para queries complejas y explicaciones |
| `model_name` | gpt-4 | Mejor comprensión de SQL y razonamiento lógico |

## Paso 4: Prompt Engineering

### 4.1 Prompt System Avanzado

```
You are an expert SQL Database Assistant with deep knowledge of database systems and query optimization. Your role is to help users extract meaningful insights from their data through natural language interactions.

## Core Capabilities
- Convert natural language questions into efficient SQL queries
- Execute queries safely using the SQL Query Executor tool
- Interpret results and provide actionable business insights
- Suggest follow-up questions and related analyses

## Database Schema
{database_schema}

## Query Generation Rules
1. **Safety First**: Only generate SELECT statements
2. **Performance**: Always include appropriate LIMIT clauses (default: 100)
3. **Clarity**: Use table aliases and clear column names
4. **Validation**: Verify table and column names against schema
5. **Error Handling**: Provide clear explanations when queries fail

## Response Format
For each user question:
1. **Understanding**: Briefly restate what the user is asking
2. **Query**: Show the SQL query you'll execute
3. **Execution**: Use the SQL tool to run the query
4. **Results**: Present findings in natural language
5. **Insights**: Provide relevant business insights or patterns
6. **Follow-up**: Suggest related questions or analyses

## Example Interaction
User: "How many active users do we have?"

Understanding: You want to know the count of users who are currently active in the system.

Query: I'll execute this SQL query:
```sql
SELECT COUNT(*) as active_users 
FROM users 
WHERE is_active = 1
```

[Execute query using tool]

Results: Based on the database query, you currently have 1,247 active users in your system.

Insights: This represents your current active user base. To provide more context, would you like me to compare this with:
- User growth over time
- Active vs inactive user ratio  
- Recent user activity patterns

## Error Handling
If a query fails:
1. Explain the error in simple terms
2. Show the corrected query
3. Provide alternative approaches
4. Ask for clarification if needed

Remember: Always use the SQL Query Executor tool for any database operations. Never simulate or make up query results.
```

### 4.2 Prompt con Schema Dinámico

Para hacer el agente más inteligente, puedes incluir el schema dinámicamente:

```python
def get_enhanced_system_prompt():
    # Obtener schema actual
    schema_info = get_database_schema()  # Función que obtiene el schema
    
    schema_text = ""
    for table in schema_info['tables']:
        columns = ", ".join([f"{col['name']} ({col['type']})" for col in table['columns']])
        schema_text += f"- {table['name']}: {columns}\n"
    
    base_prompt = """
    You are a SQL Database Assistant...
    
    ## Current Database Schema
    {schema}
    
    ## Query Generation Rules
    ...
    """
    
    return base_prompt.format(schema=schema_text)
```

## Ejemplos Prácticos

### Ejemplo 1: Consulta Simple

**Usuario**: "¿Cuántos usuarios tenemos en total?"

**Agente**:
```
Entiendo que quieres saber el número total de usuarios en el sistema.

Ejecutaré esta consulta SQL:
```sql
SELECT COUNT(*) as total_users FROM users
```

*[Usa la herramienta SQL Query Executor]*

Según los datos de la base de datos, tienes **2,543 usuarios** registrados en total.

**Insights adicionales:**
- ¿Te gustaría ver cuántos de estos están activos actualmente?
- ¿O prefieres analizar el crecimiento de usuarios por mes?
```

### Ejemplo 2: Consulta con JOIN

**Usuario**: "¿Qué agentes han tenido más ejecuciones exitosas?"

**Agente**:
```
Quieres conocer qué agentes tienen mejor rendimiento basado en ejecuciones completadas exitosamente.

Ejecutaré esta consulta que une las tablas de agentes y ejecuciones:

```sql
SELECT 
    a.name as agent_name,
    a.description,
    COUNT(*) as successful_executions,
    AVG(CAST(e.execution_time_ms as FLOAT)) as avg_execution_time
FROM agents a
JOIN executions e ON a.id = e.agent_id
WHERE e.status = 'completed'
GROUP BY a.id, a.name, a.description
ORDER BY successful_executions DESC
LIMIT 10
```

*[Usa la herramienta SQL Query Executor]*

**Top 3 Agentes más exitosos:**
1. **Virtual Assistant** - 456 ejecuciones exitosas (promedio: 1,234ms)
2. **Data Analyzer** - 234 ejecuciones exitosas (promedio: 2,156ms)  
3. **Content Generator** - 189 ejecuciones exitosas (promedio: 987ms)

**Insights:**
- El Virtual Assistant es claramente el más utilizado
- Content Generator es el más rápido en promedio
- ¿Te interesa analizar los costos asociados a estos agentes?
```

### Ejemplo 3: Análisis Temporal

**Usuario**: "¿Cómo ha sido el crecimiento de usuarios en los últimos 6 meses?"

**Agente**:
```
Analizaré el crecimiento de usuarios mes a mes durante los últimos 6 meses.

```sql
SELECT 
    FORMAT(created_at, 'yyyy-MM') as month,
    COUNT(*) as new_users,
    SUM(COUNT(*)) OVER (ORDER BY FORMAT(created_at, 'yyyy-MM')) as cumulative_users
FROM users
WHERE created_at >= DATEADD(month, -6, GETDATE())
GROUP BY FORMAT(created_at, 'yyyy-MM')
ORDER BY month
```

*[Usa la herramienta SQL Query Executor]*

**Crecimiento de Usuarios (últimos 6 meses):**
- **2024-08**: 145 nuevos usuarios (Total: 1,890)
- **2024-09**: 189 nuevos usuarios (Total: 2,079)
- **2024-10**: 234 nuevos usuarios (Total: 2,313)
- **2024-11**: 156 nuevos usuarios (Total: 2,469)
- **2024-12**: 178 nuevos usuarios (Total: 2,647)
- **2025-01**: 89 nuevos usuarios (Total: 2,736)

**Insights:**
- El mejor mes fue octubre con 234 nuevos registros
- Crecimiento promedio: 165 usuarios/mes
- Tendencia general positiva con una pequeña desaceleración en enero
- ¿Quieres que analice qué factores pudieron influir en estos picos?
```

## Seguridad y Mejores Prácticas

### 5.1 Validaciones de Seguridad

```python
class SQLSecurityValidator:
    ALLOWED_KEYWORDS = ['SELECT', 'FROM', 'WHERE', 'JOIN', 'GROUP BY', 'ORDER BY', 'HAVING', 'LIMIT', 'TOP']
    FORBIDDEN_KEYWORDS = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE', 'EXEC', 'EXECUTE', 'GRANT', 'REVOKE']
    FORBIDDEN_FUNCTIONS = ['xp_cmdshell', 'sp_configure', 'openrowset', 'opendatasource']
    
    @staticmethod
    def validate_query(query):
        query_upper = query.upper()
        
        # Verificar palabras prohibidas
        for keyword in SQLSecurityValidator.FORBIDDEN_KEYWORDS:
            if keyword in query_upper:
                return False, f"Keyword '{keyword}' is not allowed"
        
        # Verificar funciones peligrosas
        for func in SQLSecurityValidator.FORBIDDEN_FUNCTIONS:
            if func.upper() in query_upper:
                return False, f"Function '{func}' is not allowed"
        
        # Verificar que comience con SELECT
        if not query_upper.strip().startswith('SELECT'):
            return False, "Only SELECT queries are allowed"
        
        # Verificar comentarios SQL maliciosos
        if '--' in query or '/*' in query:
            return False, "SQL comments are not allowed"
        
        return True, "Query is valid"
```

### 5.2 Rate Limiting y Monitoreo

```python
from collections import defaultdict
from datetime import datetime, timedelta
import time

class QueryRateLimiter:
    def __init__(self):
        self.user_queries = defaultdict(list)
        self.max_queries_per_minute = 10
        self.max_queries_per_hour = 100
    
    def can_execute_query(self, user_id):
        now = datetime.now()
        user_history = self.user_queries[user_id]
        
        # Limpiar queries antiguas
        user_history[:] = [q for q in user_history if now - q < timedelta(hours=1)]
        
        # Verificar límites
        recent_queries = [q for q in user_history if now - q < timedelta(minutes=1)]
        
        if len(recent_queries) >= self.max_queries_per_minute:
            return False, "Rate limit exceeded: too many queries per minute"
        
        if len(user_history) >= self.max_queries_per_hour:
            return False, "Rate limit exceeded: too many queries per hour"
        
        # Registrar nueva query
        user_history.append(now)
        return True, "OK"
```

### 5.3 Logging y Auditoría

```python
import logging
import json

class SQLQueryLogger:
    def __init__(self):
        self.logger = logging.getLogger('sql_queries')
        handler = logging.FileHandler('sql_queries.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_query(self, user_id, agent_id, query, success, execution_time, row_count=None, error=None):
        log_data = {
            'user_id': user_id,
            'agent_id': agent_id,
            'query': query,
            'success': success,
            'execution_time_ms': execution_time,
            'row_count': row_count,
            'error': error,
            'timestamp': datetime.now().isoformat()
        }
        
        if success:
            self.logger.info(f"Query executed successfully: {json.dumps(log_data)}")
        else:
            self.logger.error(f"Query failed: {json.dumps(log_data)}")
```

## Troubleshooting

### Errores Comunes

#### 1. "Connection timeout"
**Causa**: La base de datos no responde  
**Solución**: 
- Verificar que SQL Server esté ejecutándose
- Comprobar la cadena de conexión
- Revisar configuración de firewall

```python
# Test de conexión
def test_connection():
    try:
        with pyodbc.connect(connection_string, timeout=5) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            return True, "Connection successful"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"
```

#### 2. "Invalid object name 'tabla'"
**Causa**: Tabla no existe o nombre incorrecto  
**Solución**: Actualizar el schema en el prompt del agente

```sql
-- Query para verificar tablas existentes
SELECT TABLE_NAME 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_TYPE = 'BASE TABLE'
```

#### 3. "Query too complex"  
**Causa**: Query excede límites de tiempo/memoria  
**Solución**: Implementar límites más estrictos

```python
def add_query_limits(query):
    # Agregar TOP si no existe
    if 'TOP' not in query.upper() and 'LIMIT' not in query.upper():
        query = query.replace('SELECT', 'SELECT TOP 100', 1)
    return query
```

### Debugging del Agente

#### 1. Verificar configuración de la tool
```bash
curl -X GET "http://localhost:8000/api/v1/tools/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 2. Test directo del endpoint SQL
```bash
curl -X POST "http://localhost:5000/api/sql/execute" \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT TOP 5 * FROM users"}'
```

#### 3. Monitorear logs del agente
```python
# En el agente, agregar logging detallado
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def execute_agent(query):
    logger.debug(f"Received query: {query}")
    # ... resto del código
    logger.debug(f"Generated SQL: {sql_query}")
    logger.debug(f"Tool response: {tool_response}")
```

### Performance Optimization

#### 1. Cachear schema information
```python
from functools import lru_cache
from datetime import datetime, timedelta

class SchemaCache:
    def __init__(self):
        self._schema = None
        self._last_update = None
        self._cache_duration = timedelta(hours=1)
    
    @lru_cache(maxsize=1)
    def get_schema(self):
        now = datetime.now()
        if (self._schema is None or 
            self._last_update is None or 
            now - self._last_update > self._cache_duration):
            self._schema = self._fetch_schema_from_db()
            self._last_update = now
        return self._schema
```

#### 2. Query optimization hints
```python
def optimize_query(query):
    # Agregar hints de optimización
    optimized = query
    
    # Forzar uso de índices si es apropiado
    if 'WHERE' in query.upper():
        optimized += " OPTION (RECOMPILE)"
    
    return optimized
```

## Próximos Pasos

### Mejoras Sugeridas

1. **Schema Auto-Discovery**: Actualización automática del schema del agente
2. **Query Caching**: Cache de queries frecuentes para mejor performance
3. **Visual Analytics**: Integración con herramientas de visualización
4. **Natural Language**: Mejores prompts para comprensión de lenguaje natural
5. **Query Suggestions**: Sugerencias inteligentes basadas en historial

### Integraciones Adicionales

1. **Business Intelligence**: Conexión con Power BI / Tableau
2. **Alertas**: Notificaciones basadas en umbrales de datos
3. **Exports**: Exportación automática a Excel/CSV
4. **Scheduling**: Queries programadas y reportes automáticos

¡Tu agente SQL está listo para consultar inteligentemente tu base de datos! 🎉