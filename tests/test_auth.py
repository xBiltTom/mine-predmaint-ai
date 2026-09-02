"""
Pruebas automatizadas de Seguridad, Criptografía (bcrypt, JWT) y Matriz RBAC.
"""
import pytest
from auth.security import hash_password, verify_password, create_access_token, decode_access_token
from config.permissions import has_permission, ROLE_PERMISSIONS_MATRIX

def test_bcrypt_hashing_and_verification():
    raw_password = "SecretPassword123!"
    hashed = hash_password(raw_password)
    assert hashed != raw_password
    assert verify_password(raw_password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_jwt_generation_and_decoding():
    payload = {"sub": "ingeniero", "rol": "Ingeniero de Mantenimiento", "user_id": 2}
    token = create_access_token(payload)
    assert isinstance(token, str)
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "ingeniero"
    assert decoded["rol"] == "Ingeniero de Mantenimiento"

def test_rbac_permissions():
    # Administrador debe tener permisos de gestión de usuarios
    assert has_permission("Administrador", "USERS_MANAGE") is True
    assert has_permission("Administrador", "AUDIT_VIEW") is True
    
    # Operador de Planta NO debe tener permisos de gestión de usuarios ni de auditoría
    assert has_permission("Operador de Planta", "USERS_MANAGE") is False
    assert has_permission("Operador de Planta", "AUDIT_VIEW") is False
    assert has_permission("Operador de Planta", "TELEMETRY_SIMULATE") is True

    # Ingeniero de Mantenimiento debe tener permisos de entrenamiento IA
    assert has_permission("Ingeniero de Mantenimiento", "ML_TRAIN_EVALUATE") is True
    assert has_permission("Ingeniero de Mantenimiento", "WORK_ORDERS_MANAGE") is True
