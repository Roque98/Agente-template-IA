#!/usr/bin/env python3
"""
Database setup script for Agent System
Connects to SQL Server and executes the initialization script
"""

import pyodbc
import sys
import os

def setup_database():
    """Execute the database initialization script"""
    
    # Connection parameters
    server = 'localhost\\SQLEXPRESS'
    database = 'master'  # Connect to master first to create the database
    username = 'usrmon'  # Use sa account to create database and user
    
    # Get password from environment or prompt
    password = os.environ.get('SA_PASSWORD')
    if not password:
        password = input("Enter SQL Server usrmon password: ")
    
    try:
        # Connection string for initial setup
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};Encrypt=no;TrustServerCertificate=yes;'
        
        print("Connecting to SQL Server...")
        print(conn_str)
        conn = pyodbc.connect(conn_str)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Read and execute the SQL script
        script_path = os.path.join(os.path.dirname(__file__), 'init.sql')
        with open(script_path, 'r', encoding='utf-8') as file:
            sql_script = file.read()
        
        # Split script by GO statements
        statements = sql_script.split('GO')
        
        print("Executing database setup script...")
        for statement in statements:
            statement = statement.strip()
            if statement:
                try:
                    cursor.execute(statement)
                    print(f"✓ Executed statement successfully")
                except Exception as e:
                    print(f"✗ Error executing statement: {e}")
                    print(f"Statement: {statement[:100]}...")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Database setup completed successfully!")
        print("Database: AgentSystem")
        print("User: usrmon")
        print("Password: MonAplic01@")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_database()