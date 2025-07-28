import json
import httpx
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.tool import Tool
from app.models.encrypted_credentials import EncryptedCredentials
from app.utils.encryption import encryption_util

class ToolService:
    def __init__(self, db: Session):
        self.db = db
    
    async def execute_tool(
        self, 
        tool_id: int, 
        user_id: int,
        endpoint: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Dict[str, Any]] = None,
        auth_config: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute an HTTP tool call
        
        Args:
            tool_id: ID of the tool to execute
            user_id: ID of the user making the request
            endpoint: The endpoint URL to call
            method: HTTP method (GET, POST, PUT, DELETE)
            headers: Additional headers to include
            body: Request body for POST/PUT requests
            auth_config: Name of encrypted credentials to use for auth
            
        Returns:
            Dict containing status_code, data, execution_time, and cost
        """
        
        tool = self.db.query(Tool).filter(Tool.id == tool_id).first()
        if not tool:
            raise ValueError(f"Tool with id {tool_id} not found")
        
        if not tool.is_active:
            raise ValueError(f"Tool {tool.name} is not active")
        
        # Validate method is allowed
        allowed_methods = [m.strip().upper() for m in tool.method_allowed.split(",")]
        if method.upper() not in allowed_methods:
            raise ValueError(f"Method {method} not allowed for tool {tool.name}")
        
        # Prepare headers
        request_headers = {}
        if tool.default_headers:
            try:
                default_headers = json.loads(tool.default_headers)
                request_headers.update(default_headers)
            except json.JSONDecodeError:
                pass
        
        if headers:
            request_headers.update(headers)
        
        # Handle authentication
        if tool.requires_auth and auth_config:
            auth_data = self._get_decrypted_credentials(user_id, auth_config)
            if auth_data:
                # Apply authentication based on type
                auth_type = auth_data.get("type", "bearer")
                if auth_type == "bearer":
                    request_headers["Authorization"] = f"Bearer {auth_data.get('token')}"
                elif auth_type == "api_key":
                    key_name = auth_data.get("key_name", "X-API-Key")
                    request_headers[key_name] = auth_data.get("api_key")
                elif auth_type == "basic":
                    import base64
                    credentials = f"{auth_data.get('username')}:{auth_data.get('password')}"
                    encoded = base64.b64encode(credentials.encode()).decode()
                    request_headers["Authorization"] = f"Basic {encoded}"
        
        # Execute HTTP request
        import time
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=tool.timeout_seconds) as client:
                if method.upper() == "GET":
                    response = await client.get(endpoint, headers=request_headers)
                elif method.upper() == "POST":
                    response = await client.post(endpoint, headers=request_headers, json=body)
                elif method.upper() == "PUT":
                    response = await client.put(endpoint, headers=request_headers, json=body)
                elif method.upper() == "DELETE":
                    response = await client.delete(endpoint, headers=request_headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                execution_time = time.time() - start_time
                
                # Parse response
                try:
                    response_data = response.json()
                except:
                    response_data = response.text
                
                return {
                    "status_code": response.status_code,
                    "data": response_data,
                    "execution_time": execution_time,
                    "cost": float(tool.cost_per_request)
                }
                
        except httpx.TimeoutException:
            return {
                "status_code": 408,
                "data": {"error": "Request timeout"},
                "execution_time": time.time() - start_time,
                "cost": float(tool.cost_per_request)
            }
        except Exception as e:
            return {
                "status_code": 500,
                "data": {"error": str(e)},
                "execution_time": time.time() - start_time,
                "cost": float(tool.cost_per_request)
            }
    
    def _get_decrypted_credentials(self, user_id: int, credential_name: str) -> Optional[Dict[str, Any]]:
        """Get and decrypt stored credentials for a user"""
        credential = self.db.query(EncryptedCredentials).filter(
            EncryptedCredentials.user_id == user_id,
            EncryptedCredentials.credential_name == credential_name
        ).first()
        
        if not credential:
            return None
        
        try:
            decrypted_data = encryption_util.decrypt(credential.encrypted_data)
            return json.loads(decrypted_data)
        except Exception:
            return None
    
    def store_encrypted_credentials(
        self, 
        user_id: int, 
        credential_name: str, 
        credential_data: Dict[str, Any],
        credential_type: str = "api"
    ) -> EncryptedCredentials:
        """Store encrypted credentials for a user"""
        
        # Delete existing credential with same name
        existing = self.db.query(EncryptedCredentials).filter(
            EncryptedCredentials.user_id == user_id,
            EncryptedCredentials.credential_name == credential_name
        ).first()
        
        if existing:
            self.db.delete(existing)
        
        # Encrypt and store new credential
        encrypted_data = encryption_util.encrypt(json.dumps(credential_data))
        
        credential = EncryptedCredentials(
            user_id=user_id,
            credential_name=credential_name,
            encrypted_data=encrypted_data,
            credential_type=credential_type
        )
        
        self.db.add(credential)
        self.db.commit()
        self.db.refresh(credential)
        
        return credential