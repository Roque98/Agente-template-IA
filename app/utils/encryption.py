import base64
from cryptography.fernet import Fernet
from app.core.config import settings

class EncryptionUtil:
    def __init__(self):
        self.cipher_suite = Fernet(settings.encryption_key.encode())
    
    def encrypt(self, plain_text: str) -> str:
        encrypted_text = self.cipher_suite.encrypt(plain_text.encode())
        return base64.b64encode(encrypted_text).decode()
    
    def decrypt(self, encrypted_text: str) -> str:
        encrypted_bytes = base64.b64decode(encrypted_text.encode())
        decrypted_text = self.cipher_suite.decrypt(encrypted_bytes)
        return decrypted_text.decode()

encryption_util = EncryptionUtil()