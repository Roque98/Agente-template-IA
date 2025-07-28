import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db, Base

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_register_user():
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_login_user():
    # First register a user
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "logintest",
            "email": "login@example.com",
            "password": "testpassword123",
            "full_name": "Login Test"
        }
    )
    
    # Then login
    response = client.post(
        "/api/v1/auth/login-json",
        json={
            "username": "logintest",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_get_current_user():
    # Register and login
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "currentuser",
            "email": "current@example.com",
            "password": "testpassword123"
        }
    )
    
    login_response = client.post(
        "/api/v1/auth/login-json",
        json={
            "username": "currentuser",
            "password": "testpassword123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Get current user info
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "currentuser"