# 🔧 Guía de Parámetros de Tools y Gestión de Contexto

Esta guía explica cómo declarar, gestionar y usar parámetros en las tools, incluyendo el manejo de contexto conversacional.

## 📋 Índice

1. [Tipos de Parámetros](#tipos-de-parámetros)
2. [Declaración en el Modelo](#declaración-en-el-modelo)
3. [Configuración de Tools](#configuración-de-tools)
4. [Gestión de Contexto](#gestión-de-contexto)
5. [Ejemplos Prácticos](#ejemplos-prácticos)
6. [Implementación](#implementación)

## Tipos de Parámetros

### 1. **Parámetros Fijos** 🔒
Valores constantes definidos al crear la tool:
- **API Keys, tokens, passwords**
- **URLs base, puertos** 
- **Configuraciones técnicas**
- **Credenciales de autenticación**

### 2. **Parámetros Variables** 🔄
Valores que cambian con cada ejecución:
- **Datos del usuario** (user_id, preferences)
- **Contexto de conversación** (historial, mensaje actual)
- **Parámetros de query** (fechas, filtros, límites)
- **Variables deducidas** por el agente

### 3. **Parámetros Opcionales** ❓
Valores con defaults que pueden sobrescribirse:
- **Límites de resultados** (default: 100)
- **Timeouts** (default: 30s)
- **Formatos de respuesta** (default: JSON)

## Declaración en el Modelo

### Extensión del Modelo Tool

```python
# app/models/tool.py - Versión extendida

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Numeric, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Tool(Base):
    __tablename__ = "tools"
    
    # Campos existentes
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(500))
    endpoint_template = Column(Text, nullable=False)
    method_allowed = Column(String(100), default="GET,POST,PUT,DELETE")
    
    # NUEVOS CAMPOS PARA PARÁMETROS
    parameter_schema = Column(JSON)  # Esquema de parámetros esperados
    fixed_parameters = Column(JSON)  # Parámetros fijos (encriptados si es necesario)
    default_parameters = Column(JSON)  # Valores por defecto
    parameter_mapping = Column(JSON)  # Mapeo de parámetros del agente a la API
    
    # Campos de autenticación
    auth_type = Column(String(50))  # bearer, api_key, basic, oauth
    auth_parameters = Column(JSON)  # Parámetros de autenticación encriptados
    
    # Otros campos existentes
    default_headers = Column(JSON)
    requires_auth = Column(Boolean, default=False)
    timeout_seconds = Column(Integer, default=30)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.getutcdate())
    updated_at = Column(DateTime, server_default=func.getutcdate(), onupdate=func.getutcdate())
    
    # Relationships
    created_by_user = relationship("User", back_populates="tools")
    agent_tools = relationship("AgentTool", back_populates="tool", cascade="all, delete-orphan")

class ToolExecution(Base):
    """Nuevo modelo para almacenar ejecuciones de tools con parámetros"""
    __tablename__ = "tool_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    tool_id = Column(Integer, ForeignKey("tools.id"), nullable=False)
    execution_id = Column(Integer, ForeignKey("executions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Parámetros y resultados
    input_parameters = Column(JSON)  # Parámetros enviados
    resolved_parameters = Column(JSON)  # Parámetros después de resolución
    request_data = Column(JSON)  # Datos enviados a la API
    response_data = Column(JSON)  # Respuesta de la API
    
    # Métricas
    status = Column(String(20))  # success, error, timeout
    execution_time_ms = Column(Integer)
    error_message = Column(Text)
    
    created_at = Column(DateTime, server_default=func.getutcdate())
    
    # Relationships
    tool = relationship("Tool")
    execution = relationship("Execution")
    user = relationship("User")
```

### Modelo de Contexto Conversacional

```python
# app/models/conversation.py - Nuevo modelo

class Conversation(Base):
    """Almacena conversaciones completas por usuario"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    
    # Identificación de conversación
    conversation_uuid = Column(String(36), unique=True, nullable=False)  # UUID único
    title = Column(String(200))  # Título generado automáticamente
    
    # Metadatos
    status = Column(String(20), default="active")  # active, archived, deleted
    context_summary = Column(Text)  # Resumen del contexto para el agente
    
    # Timestamps
    started_at = Column(DateTime, server_default=func.getutcdate())
    last_message_at = Column(DateTime, server_default=func.getutcdate())
    
    # Relationships
    user = relationship("User")
    agent = relationship("Agent") 
    messages = relationship("ConversationMessage", back_populates="conversation", cascade="all, delete-orphan")

class ConversationMessage(Base):
    """Mensajes individuales dentro de una conversación"""  
    __tablename__ = "conversation_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    execution_id = Column(Integer, ForeignKey("executions.id"), nullable=True)
    
    # Contenido del mensaje
    message_type = Column(String(20))  # user, assistant, system, tool_call, tool_response
    content = Column(Text, nullable=False)
    
    # Metadatos del mensaje
    message_order = Column(Integer, nullable=False)  # Orden en la conversación
    context_variables = Column(JSON)  # Variables extraídas del mensaje
    tool_calls = Column(JSON)  # Llamadas a tools realizadas
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.getutcdate())
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    execution = relationship("Execution")
```

## Configuración de Tools

### 1. Ejemplo: Tool SQL Query Executor

```json
{
    "name": "SQL Query Executor",
    "description": "Executes SQL queries against the database with user context",
    "endpoint_template": "http://localhost:5000/api/sql/execute",
    "method_allowed": "POST",
    
    "parameter_schema": {
        "required": ["query"],
        "optional": ["limit", "timeout", "safe_mode"],
        "properties": {
            "query": {
                "type": "string",
                "description": "SQL query to execute",
                "source": "agent_generated",
                "validation": "sql_select_only"
            },
            "limit": {
                "type": "integer", 
                "description": "Maximum rows to return",
                "source": "default",
                "default": 1000,
                "min": 1,
                "max": 10000
            },
            "timeout": {
                "type": "integer",
                "description": "Query timeout in seconds", 
                "source": "default",
                "default": 30
            },
            "safe_mode": {
                "type": "boolean",
                "description": "Enable safety validations",
                "source": "fixed",
                "value": true
            },
            "user_id": {
                "type": "string",
                "description": "Current user identifier",
                "source": "context",
                "context_path": "user.id"
            }
        }
    },
    
    "fixed_parameters": {
        "database_connection": "main_db",
        "api_version": "v1"
    },
    
    "auth_type": "bearer",
    "auth_parameters": {
        "token_source": "system_token",
        "encrypted_token": "eyJ0eXAiOiJKV1QiLCJ..."
    },
    
    "parameter_mapping": {
        "query": "sql_query",
        "limit": "max_rows", 
        "user_id": "requesting_user"
    },
    
    "default_headers": {
        "Content-Type": "application/json",
        "X-API-Version": "1.0"
    }
}
```

### 2. Ejemplo: Tool Schema Provider

```json
{
    "name": "Database Schema Provider",
    "description": "Provides database schema with business context",
    "endpoint_template": "http://localhost:5000/api/schema/info",
    "method_allowed": "GET",
    
    "parameter_schema": {
        "optional": ["include_samples", "include_relationships", "table_filter"],
        "properties": {
            "include_samples": {
                "type": "boolean",
                "description": "Include sample values",
                "source": "default",
                "default": true
            },
            "include_relationships": {
                "type": "boolean", 
                "description": "Include foreign key relationships",
                "source": "default",
                "default": true
            },
            "table_filter": {
                "type": "string",
                "description": "Filter specific tables",
                "source": "agent_optional",
                "validation": "table_name_regex"
            },
            "user_access_level": {
                "type": "string",
                "description": "User permission level for schema filtering",
                "source": "context",
                "context_path": "user.role"
            }
        }
    },
    
    "fixed_parameters": {
        "schema_version": "1.0",
        "cache_enabled": true
    }
}
```

### 3. Ejemplo: Tool Weather API

```json
{
    "name": "Weather API",
    "description": "Gets weather information for specified locations",
    "endpoint_template": "https://api.openweathermap.org/data/2.5/weather",
    "method_allowed": "GET",
    
    "parameter_schema": {
        "required": ["location"],
        "optional": ["units", "lang"],
        "properties": {
            "location": {
                "type": "string",
                "description": "City name or coordinates",
                "source": "user_input",
                "prompt": "¿Para qué ciudad quieres consultar el clima?",
                "validation": "non_empty"
            },
            "units": {
                "type": "string",
                "description": "Temperature units",
                "source": "user_preference",
                "preference_key": "weather_units",
                "default": "metric",
                "enum": ["metric", "imperial", "kelvin"]
            },
            "lang": {
                "type": "string", 
                "description": "Response language",
                "source": "context",
                "context_path": "user.language",
                "default": "es"
            },
            "appid": {
                "type": "string",
                "description": "API key for weather service",
                "source": "encrypted_config",
                "config_key": "weather_api_key"
            }
        }
    },
    
    "parameter_mapping": {
        "location": "q",
        "units": "units",
        "lang": "lang", 
        "appid": "appid"
    }
}
```

## Gestión de Contexto

### 1. Servicio de Contexto

```python
# app/services/context_service.py

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.models.conversation import Conversation, ConversationMessage
from app.models.user import User

class ContextService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_conversation(self, user_id: int, agent_id: int, 
                                 conversation_uuid: Optional[str] = None) -> Conversation:
        """Obtiene o crea una conversación"""
        if conversation_uuid:
            conversation = self.db.query(Conversation).filter(
                Conversation.conversation_uuid == conversation_uuid,
                Conversation.user_id == user_id
            ).first()
            if conversation:
                return conversation
        
        # Crear nueva conversación
        import uuid
        conversation = Conversation(
            user_id=user_id,
            agent_id=agent_id,
            conversation_uuid=str(uuid.uuid4()),
            status="active"
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation
    
    def add_message(self, conversation_id: int, message_type: str, 
                   content: str, context_variables: Dict = None,
                   execution_id: Optional[int] = None) -> ConversationMessage:
        """Agrega un mensaje a la conversación"""
        
        # Obtener el siguiente número de orden
        last_message = self.db.query(ConversationMessage).filter(
            ConversationMessage.conversation_id == conversation_id
        ).order_by(ConversationMessage.message_order.desc()).first()
        
        next_order = (last_message.message_order + 1) if last_message else 1
        
        message = ConversationMessage(
            conversation_id=conversation_id,
            execution_id=execution_id,
            message_type=message_type,
            content=content,
            message_order=next_order,
            context_variables=context_variables or {}
        )
        
        self.db.add(message)
        
        # Actualizar timestamp de la conversación
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        if conversation:
            conversation.last_message_at = func.getutcdate()
        
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def get_conversation_context(self, conversation_id: int, 
                               max_messages: int = 10) -> Dict[str, Any]:
        """Obtiene el contexto de una conversación"""
        
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if not conversation:
            return {}
        
        # Obtener mensajes recientes
        messages = self.db.query(ConversationMessage).filter(
            ConversationMessage.conversation_id == conversation_id
        ).order_by(ConversationMessage.message_order.desc()).limit(max_messages).all()
        
        # Construir contexto
        context = {
            "conversation_id": conversation.conversation_uuid,
            "user_id": conversation.user_id,
            "agent_id": conversation.agent_id,
            "messages": [],
            "extracted_variables": {},
            "conversation_summary": conversation.context_summary
        }
        
        # Procesar mensajes
        for msg in reversed(messages):  # Orden cronológico
            context["messages"].append({
                "type": msg.message_type,
                "content": msg.content,
                "timestamp": msg.created_at.isoformat(),
                "variables": msg.context_variables
            })
            
            # Combinar variables extraídas
            if msg.context_variables:
                context["extracted_variables"].update(msg.context_variables)
        
        return context
    
    def extract_variables_from_message(self, content: str) -> Dict[str, Any]:
        """Extrae variables relevantes de un mensaje"""
        import re
        from datetime import datetime
        
        variables = {}
        
        # Extraer fechas
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+\d{1,2}',
            r'(ayer|hoy|mañana)',
            r'(esta\s+semana|semana\s+pasada|próxima\s+semana)',
            r'(este\s+mes|mes\s+pasado|próximo\s+mes)'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                variables['mentioned_dates'] = matches
        
        # Extraer números/cantidades
        number_patterns = [
            r'(\d+)\s*(usuarios?|agentes?|ejecuciones?)',
            r'(más|menos|mayor|menor)\s+(?:de\s+)?(\d+)',
            r'(\d+)\s*(días?|semanas?|meses?|años?)'
        ]
        
        for pattern in number_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                if 'mentioned_quantities' not in variables:
                    variables['mentioned_quantities'] = []
                variables['mentioned_quantities'].extend(matches)
        
        # Extraer nombres de tablas/entidades
        entity_patterns = [
            r'(tabla|tablas)\s+(\w+)',
            r'(usuarios?|agentes?|ejecuciones?|costos?)',
            r'(activos?|inactivos?|administradores?)'
        ]
        
        for pattern in entity_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                if 'mentioned_entities' not in variables:
                    variables['mentioned_entities'] = []
                variables['mentioned_entities'].extend([m[1] if isinstance(m, tuple) else m for m in matches])
        
        return variables
```

### 2. Resolución de Parámetros

```python
# app/services/parameter_resolver.py

class ParameterResolver:
    def __init__(self, db: Session, context_service: ContextService):
        self.db = db
        self.context_service = context_service
    
    async def resolve_parameters(self, tool: Tool, agent_context: Dict, 
                               conversation_id: int, user: User) -> Dict[str, Any]:
        """Resuelve todos los parámetros de una tool"""
        
        resolved = {}
        schema = tool.parameter_schema or {}
        properties = schema.get('properties', {})
        
        # Obtener contexto de conversación
        conversation_context = self.context_service.get_conversation_context(conversation_id)
        
        for param_name, param_config in properties.items():
            value = await self._resolve_single_parameter(
                param_name, param_config, tool, agent_context, 
                conversation_context, user
            )
            
            if value is not None:
                resolved[param_name] = value
        
        # Agregar parámetros fijos
        if tool.fixed_parameters:
            resolved.update(tool.fixed_parameters)
        
        return resolved
    
    async def _resolve_single_parameter(self, param_name: str, config: Dict,
                                      tool: Tool, agent_context: Dict,
                                      conversation_context: Dict, user: User) -> Any:
        """Resuelve un parámetro individual"""
        
        source = config.get('source', 'default')
        
        if source == 'fixed':
            return config.get('value')
        
        elif source == 'default':
            return config.get('default')
        
        elif source == 'context':
            # Obtener del contexto usando path
            context_path = config.get('context_path', '')
            return self._get_nested_value(agent_context, context_path)
        
        elif source == 'user_input':
            # Parámetro requiere input del usuario
            return await self._request_user_input(param_name, config, conversation_context)
        
        elif source == 'user_preference':
            # Obtener de preferencias del usuario
            preference_key = config.get('preference_key')
            return self._get_user_preference(user, preference_key, config.get('default'))
        
        elif source == 'agent_generated':
            # El agente debe generar este valor
            return agent_context.get(param_name)
        
        elif source == 'encrypted_config':
            # Obtener de configuración encriptada
            config_key = config.get('config_key')
            return self._get_encrypted_config(config_key)
        
        elif source == 'conversation_variable':
            # Extraer de variables de conversación
            var_name = config.get('variable_name', param_name)
            return conversation_context.get('extracted_variables', {}).get(var_name)
        
        return None
    
    async def _request_user_input(self, param_name: str, config: Dict,
                                conversation_context: Dict) -> Optional[str]:
        """Solicita input del usuario para un parámetro"""
        
        # Verificar si ya tenemos el valor en el contexto
        extracted_vars = conversation_context.get('extracted_variables', {})
        if param_name in extracted_vars:
            return extracted_vars[param_name]
        
        # Si no tenemos el valor, el agente debe preguntarlo
        prompt = config.get('prompt', f"Necesito el valor para {param_name}")
        
        # Esto se manejará en el flujo del agente
        # El agente verá que falta este parámetro y preguntará al usuario
        return None
    
    def _get_nested_value(self, data: Dict, path: str) -> Any:
        """Obtiene un valor usando dot notation (user.id, user.preferences.language)"""
        keys = path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
```

## Ejemplos Prácticos

### 1. Flujo Completo de Ejecución de Tool

```python
# app/services/tool_execution_service.py

class ToolExecutionService:
    def __init__(self, db: Session):
        self.db = db
        self.context_service = ContextService(db)
        self.parameter_resolver = ParameterResolver(db, self.context_service)
    
    async def execute_tool(self, tool_id: int, agent_context: Dict,
                          conversation_id: int, user: User) -> Dict[str, Any]:
        """Ejecuta una tool con resolución completa de parámetros"""
        
        # 1. Obtener configuración de la tool
        tool = self.db.query(Tool).filter(Tool.id == tool_id).first()
        if not tool:
            raise Exception(f"Tool {tool_id} not found")
        
        # 2. Resolver parámetros
        resolved_params = await self.parameter_resolver.resolve_parameters(
            tool, agent_context, conversation_id, user
        )
        
        # 3. Verificar parámetros requeridos
        missing_params = self._check_required_parameters(tool, resolved_params)
        if missing_params:
            return {
                "success": False,
                "error": "missing_parameters",
                "missing_parameters": missing_params,
                "message": f"Faltan parámetros requeridos: {', '.join(missing_params)}"
            }
        
        # 4. Mapear parámetros según configuración
        mapped_params = self._map_parameters(tool, resolved_params)
        
        # 5. Ejecutar llamada HTTP
        try:
            result = await self._execute_http_call(tool, mapped_params)
            
            # 6. Registrar ejecución exitosa
            self._log_tool_execution(tool, user, resolved_params, mapped_params, result, "success")
            
            return {
                "success": True,
                "data": result,
                "parameters_used": resolved_params
            }
            
        except Exception as e:
            # 7. Registrar error
            self._log_tool_execution(tool, user, resolved_params, mapped_params, str(e), "error")
            
            return {
                "success": False,
                "error": "execution_failed",
                "message": str(e)
            }
```

### 2. Ejemplo de Conversación con Context

```python
# Ejemplo de flujo de conversación

# Usuario: "¿Cuántos usuarios activos tenemos de enero?"
conversation_id = context_service.get_or_create_conversation(user_id=1, agent_id=1)

# El agente procesa y extrae variables
extracted_vars = context_service.extract_variables_from_message(
    "¿Cuántos usuarios activos tenemos de enero?"
)
# → {'mentioned_dates': ['enero'], 'mentioned_entities': ['usuarios', 'activos']}

# 1. El agente llama a Schema Provider (no necesita parámetros del usuario)
schema_result = await tool_service.execute_tool(
    tool_id=1,  # Schema Provider
    agent_context={},
    conversation_id=conversation_id.id,
    user=current_user
)

# 2. El agente genera la query SQL basado en el esquema y contexto
query = "SELECT COUNT(*) as active_users FROM users WHERE is_active = 1 AND MONTH(created_at) = 1"

# 3. El agente llama a Query Executor
query_result = await tool_service.execute_tool(
    tool_id=2,  # SQL Query Executor  
    agent_context={
        "query": query,  # Generado por el agente
        "limit": 1000    # Default
    },
    conversation_id=conversation_id.id,
    user=current_user
)

# El sistema resuelve automáticamente:
# - user_id: del contexto del usuario actual
# - database_connection: de parámetros fijos
# - auth_token: de configuración encriptada
# - safe_mode: true (fijo)
```

### 3. Ejemplo con Parámetros Faltantes

```python
# Usuario: "Consulta el clima"
# El agente identifica que necesita la ubicación

# 1. El agente intenta ejecutar Weather API
weather_result = await tool_service.execute_tool(
    tool_id=3,  # Weather API
    agent_context={},
    conversation_id=conversation_id.id, 
    user=current_user
)

# Resultado:
# {
#     "success": False,
#     "error": "missing_parameters", 
#     "missing_parameters": ["location"],
#     "message": "Faltan parámetros requeridos: location"
# }

# 2. El agente responde solicitando el parámetro faltante
# "Para consultar el clima, necesito saber la ubicación. ¿Para qué ciudad quieres consultar?"

# 3. Usuario responde: "Madrid"
# El agente extrae la variable location = "Madrid" y reintenta la ejecución
```

## Implementación

### 1. Migración de Base de Datos

```sql
-- Agregar nuevas columnas al modelo Tool
ALTER TABLE tools ADD COLUMN parameter_schema JSON;
ALTER TABLE tools ADD COLUMN fixed_parameters JSON;
ALTER TABLE tools ADD COLUMN default_parameters JSON;
ALTER TABLE tools ADD COLUMN parameter_mapping JSON;
ALTER TABLE tools ADD COLUMN auth_type VARCHAR(50);
ALTER TABLE tools ADD COLUMN auth_parameters JSON;

-- Crear tabla de conversaciones
CREATE TABLE conversations (
    id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT NOT NULL FOREIGN KEY REFERENCES users(id),
    agent_id INT NOT NULL FOREIGN KEY REFERENCES agents(id),
    conversation_uuid VARCHAR(36) UNIQUE NOT NULL,
    title VARCHAR(200),
    status VARCHAR(20) DEFAULT 'active',
    context_summary TEXT,
    started_at DATETIME DEFAULT GETUTCDATE(),
    last_message_at DATETIME DEFAULT GETUTCDATE()
);

-- Crear tabla de mensajes de conversación
CREATE TABLE conversation_messages (
    id INT PRIMARY KEY IDENTITY(1,1),
    conversation_id INT NOT NULL FOREIGN KEY REFERENCES conversations(id),
    execution_id INT FOREIGN KEY REFERENCES executions(id),
    message_type VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    message_order INT NOT NULL,
    context_variables JSON,
    tool_calls JSON,
    created_at DATETIME DEFAULT GETUTCDATE()
);

-- Crear tabla de ejecuciones de tools
CREATE TABLE tool_executions (
    id INT PRIMARY KEY IDENTITY(1,1),
    tool_id INT NOT NULL FOREIGN KEY REFERENCES tools(id),
    execution_id INT FOREIGN KEY REFERENCES executions(id),
    user_id INT NOT NULL FOREIGN KEY REFERENCES users(id),
    input_parameters JSON,
    resolved_parameters JSON,
    request_data JSON,
    response_data JSON,
    status VARCHAR(20),
    execution_time_ms INT,
    error_message TEXT,
    created_at DATETIME DEFAULT GETUTCDATE()
);
```

### 2. Endpoints API Actualizados

```python
# app/api/tools.py - Actualizado

@router.post("/", response_model=ToolSchema)
def create_tool(tool_data: ToolCreateExtended, db: Session = Depends(get_db)):
    """Crear tool con configuración de parámetros completa"""
    
    # Validar parameter_schema
    if tool_data.parameter_schema:
        validate_parameter_schema(tool_data.parameter_schema)
    
    # Encriptar parámetros sensibles
    if tool_data.auth_parameters:
        tool_data.auth_parameters = encrypt_parameters(tool_data.auth_parameters)
    
    if tool_data.fixed_parameters:
        tool_data.fixed_parameters = encrypt_sensitive_params(tool_data.fixed_parameters)
    
    tool = Tool(**tool_data.dict())
    db.add(tool)
    db.commit()
    db.refresh(tool)
    
    return tool

@router.post("/{tool_id}/execute")
async def execute_tool(
    tool_id: int,
    execution_data: ToolExecutionRequest,
    conversation_id: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Ejecutar tool con resolución automática de parámetros"""
    
    tool_service = ToolExecutionService(db)
    
    # Obtener o crear conversación
    if conversation_id:
        conversation = context_service.get_conversation_by_uuid(conversation_id)
    else:
        conversation = context_service.get_or_create_conversation(
            current_user.id, execution_data.agent_id
        )
    
    # Ejecutar tool
    result = await tool_service.execute_tool(
        tool_id=tool_id,
        agent_context=execution_data.parameters,
        conversation_id=conversation.id,
        user=current_user
    )
    
    return result
```

Con este sistema, las tools pueden:

✅ **Declarar parámetros** con tipos y fuentes  
✅ **Resolver automáticamente** valores de contexto, usuario, configuración  
✅ **Solicitar input** cuando faltan parámetros requeridos  
✅ **Mantener historial** de conversaciones por usuario  
✅ **Extraer variables** del contexto conversacional  
✅ **Mapear parámetros** a diferentes nombres de API  
✅ **Encriptar credenciales** sensibles de forma segura  

¿Te gustaría que implemente alguna parte específica o necesitas más detalles sobre algún aspecto? 🚀