import json
import threading
import time
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.system_config import SystemConfig
from app.core.database import SessionLocal
from app.utils.encryption import encryption_util

class ConfigService:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ConfigService, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._config_cache: Dict[str, Any] = {}
            self._last_reload = 0
            self._reload_interval = 30  # seconds
            self._running = False
            self._reload_thread = None
            self._initialized = True
    
    def start_hot_reload(self):
        """Start the hot reload background thread"""
        if not self._running:
            self._running = True
            self._reload_thread = threading.Thread(target=self._reload_loop, daemon=True)
            self._reload_thread.start()
            print("Hot reload configuration system started")
    
    def stop_hot_reload(self):
        """Stop the hot reload background thread"""
        self._running = False
        if self._reload_thread:
            self._reload_thread.join()
            print("Hot reload configuration system stopped")
    
    def _reload_loop(self):
        """Background thread that periodically reloads configuration"""
        while self._running:
            try:
                self.reload_config()
                time.sleep(self._reload_interval)
            except Exception as e:
                print(f"Error in config reload loop: {e}")
                time.sleep(self._reload_interval)
    
    def reload_config(self):
        """Reload configuration from database"""
        db = SessionLocal()
        try:
            configs = db.query(SystemConfig).all()
            new_cache = {}
            
            for config in configs:
                value = config.config_value
                
                # Decrypt if encrypted
                if config.is_encrypted and value:
                    try:
                        value = encryption_util.decrypt(value)
                    except Exception as e:
                        print(f"Failed to decrypt config {config.config_key}: {e}")
                        continue
                
                # Try to parse as JSON
                try:
                    value = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    # Keep as string if not valid JSON
                    pass
                
                new_cache[config.config_key] = value
            
            self._config_cache = new_cache
            self._last_reload = time.time()
            
        except Exception as e:
            print(f"Error reloading configuration: {e}")
        finally:
            db.close()
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key"""
        # Reload if cache is empty or if it's been too long
        if not self._config_cache or (time.time() - self._last_reload) > self._reload_interval:
            self.reload_config()
        
        return self._config_cache.get(key, default)
    
    def set_config(self, key: str, value: Any, description: str = None, encrypt: bool = False) -> bool:
        """Set a configuration value"""
        db = SessionLocal()
        try:
            # Get existing config or create new
            config = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
            
            if not config:
                config = SystemConfig(
                    config_key=key,
                    description=description,
                    is_encrypted=encrypt
                )
                db.add(config)
            
            # Prepare value
            if isinstance(value, (dict, list)):
                value_str = json.dumps(value)
            else:
                value_str = str(value)
            
            # Encrypt if needed
            if encrypt:
                value_str = encryption_util.encrypt(value_str)
            
            config.config_value = value_str
            config.is_encrypted = encrypt
            if description:
                config.description = description
            
            db.commit()
            
            # Update cache immediately
            self._config_cache[key] = value
            
            return True
            
        except Exception as e:
            print(f"Error setting configuration {key}: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    def delete_config(self, key: str) -> bool:
        """Delete a configuration value"""
        db = SessionLocal()
        try:
            config = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
            if config:
                db.delete(config)
                db.commit()
                
                # Remove from cache
                self._config_cache.pop(key, None)
                return True
            return False
            
        except Exception as e:
            print(f"Error deleting configuration {key}: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    def get_all_configs(self) -> Dict[str, Any]:
        """Get all configuration values"""
        if not self._config_cache or (time.time() - self._last_reload) > self._reload_interval:
            self.reload_config()
        
        return self._config_cache.copy()
    
    def is_hot_reload_enabled(self) -> bool:
        """Check if hot reload is enabled"""
        value = self.get_config("hot_reload_enabled", "true")
        if isinstance(value, bool):
            return value
        return str(value).lower() == "true"

# Global instance
config_service = ConfigService()