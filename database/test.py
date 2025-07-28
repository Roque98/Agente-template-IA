import pyodbc
import os

def test_sql_server_connections():
    """
    Prueba diferentes configuraciones de conexión para SQL Server local
    """
    
    # Configuraciones comunes para instancia local
    connection_configs = [
        {
            "name": "SQLEXPRESS con Named Pipes",
            "string": (
                "DRIVER={ODBC Driver 17 for SQL Server};"
                "SERVER=localhost\\SQLEXPRESS;"
                "DATABASE=master;"
                "UID=usrmon;"
                "PWD=MonAplic01@;"
                "Encrypt=no;"
                "TrustServerCertificate=yes;"
            )
        },
        {
            "name": "SQLEXPRESS con TCP/IP",
            "string": (
                "DRIVER={ODBC Driver 17 for SQL Server};"
                "SERVER=.\\SQLEXPRESS;"
                "DATABASE=master;"
                "UID=usrmon;"
                "PWD=MonAplic01@;"
                "Encrypt=no;"
                "TrustServerCertificate=yes;"
            )
        },
        {
            "name": "SQL Server por defecto",
            "string": (
                "DRIVER={ODBC Driver 17 for SQL Server};"
                "SERVER=localhost;"
                "DATABASE=master;"
                "UID=usrmon;"
                "PWD=MonAplic01@;"
                "Encrypt=no;"
                "TrustServerCertificate=yes;"
            )
        },
        {
            "name": "LocalDB",
            "string": (
                "DRIVER={ODBC Driver 17 for SQL Server};"
                "SERVER=(localdb)\\MSSQLLocalDB;"
                "DATABASE=master;"
                "UID=usrmon;"
                "PWD=MonAplic01@;"
                "Encrypt=no;"
                "TrustServerCertificate=yes;"
            )
        },
        {
            "name": "Con puerto específico",
            "string": (
                "DRIVER={ODBC Driver 17 for SQL Server};"
                "SERVER=localhost,1433;"
                "DATABASE=master;"
                "UID=usrmon;"
                "PWD=MonAplic01@;"
                "Encrypt=no;"
                "TrustServerCertificate=yes;"
            )
        }
    ]
    
    print("🔍 Probando conexiones a SQL Server local...\n")
    
    for i, config in enumerate(connection_configs, 1):
        print(f"{i}. Probando: {config['name']}")
        
        try:
            # Intenta conectar
            conn = pyodbc.connect(config['string'], timeout=10)
            
            # Prueba una consulta básica
            cursor = conn.cursor()
            cursor.execute("SELECT @@SERVERNAME, @@VERSION")
            server_name, version = cursor.fetchone()
            
            print(f"   ✅ ¡CONEXIÓN EXITOSA!")
            print(f"   📊 Servidor: {server_name}")
            print(f"   📋 Versión: {version.split(chr(10))[0]}")
            
            cursor.close()
            conn.close()
            
            print(f"\n🎉 CONFIGURACIÓN QUE FUNCIONA:")
            print(f"STRING DE CONEXIÓN EXITOSA:\n{config['string']}\n")
            
            return config['string']
            
        except pyodbc.Error as e:
            print(f"   ❌ Error: {e}")
        except Exception as e:
            print(f"   ❌ Error inesperado: {e}")
        
        print()
    
    print("❌ Ninguna configuración funcionó. Revisa los pasos adicionales.")
    return None

def create_database_class():
    """
    Clase para manejar conexiones a SQL Server
    """
    return '''
class SQLServerConnection:
    def __init__(self):
        # CAMBIA ESTA STRING POR LA QUE FUNCIONÓ EN EL TEST
        self.connection_string = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost\\\\SQLEXPRESS;"  # Doble backslash en strings
            "DATABASE=tu_database;"  # Cambia por tu base de datos real
            "UID=usrmon;"
            "PWD=tu_password;"  # Cambia por tu password real
            "Encrypt=no;"
            "TrustServerCertificate=yes;"
        )
    
    def get_connection(self):
        """Obtiene una conexión a la base de datos"""
        try:
            return pyodbc.connect(self.connection_string, timeout=30)
        except pyodbc.Error as e:
            print(f"Error de conexión: {e}")
            raise
    
    def test_connection(self):
        """Prueba la conexión"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                print("✅ Conexión exitosa!")
                return True
        except Exception as e:
            print(f"❌ Error en test: {e}")
            return False
    
    def execute_query(self, query, params=None):
        """Ejecuta una consulta SELECT"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error ejecutando query: {e}")
            raise
    
    def execute_non_query(self, query, params=None):
        """Ejecuta INSERT, UPDATE, DELETE"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            print(f"Error ejecutando comando: {e}")
            raise

# Ejemplo de uso
if __name__ == "__main__":
    db = SQLServerConnection()
    
    # Probar conexión
    if db.test_connection():
        # Ejecutar consulta de ejemplo
        try:
            results = db.execute_query("SELECT name FROM sys.databases")
            print("\\nBases de datos disponibles:")
            for row in results:
                print(f"- {row[0]}")
        except Exception as e:
            print(f"Error: {e}")
'''

def check_drivers():
    """Verifica los drivers ODBC disponibles"""
    print("🔍 Verificando drivers ODBC disponibles:\n")
    
    try:
        drivers = pyodbc.drivers()
        sql_drivers = [d for d in drivers if 'SQL Server' in d]
        
        if sql_drivers:
            print("✅ Drivers SQL Server encontrados:")
            for driver in sql_drivers:
                print(f"   - {driver}")
            print()
            return sql_drivers[0]  # Retorna el primer driver encontrado
        else:
            print("❌ No se encontraron drivers de SQL Server")
            print("💡 Instala: Microsoft ODBC Driver 17 for SQL Server")
            return None
            
    except Exception as e:
        print(f"❌ Error verificando drivers: {e}")
        return None

# EJECUTAR DIAGNÓSTICO COMPLETO
if __name__ == "__main__":
    print("🚀 DIAGNÓSTICO SQL SERVER + PYTHON\n")
    print("=" * 50)
    
    # 1. Verificar drivers
    driver = check_drivers()
    
    if driver:
        # 2. Probar conexiones
        working_config = test_sql_server_connections()
        
        if working_config:
            print("\n" + "=" * 50)
            print("📝 CÓDIGO PARA TU APLICACIÓN:")
            print("=" * 50)
            print(create_database_class())
        else:
            print("\n🛠️  PASOS ADICIONALES:")
            print("1. Verifica que SQL Server esté corriendo")
            print("2. Habilita TCP/IP en SQL Server Configuration Manager")
            print("3. Reinicia el servicio SQL Server")
            print("4. Verifica el usuario 'usrmon' en SSMS")
    else:
        print("\n📥 INSTALAR DRIVER:")
        print("Descarga: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server")