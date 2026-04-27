"""
test_p1_auth.py — Tests de autenticación y usuarios (CU1-CU4).
"""

import pytest

from tests.conftest import _register, _login, _auth_headers


class TestCU3_Register:
    def test_registro_exitoso(self, client):
        r = client.post("/auth/register", json={
            "nombre": "Juan",
            "email": "juan@test.com",
            "password": "Test1234!",
            "rol": "cliente",
        })
        assert r.status_code == 201
        data = r.json()
        assert data["email"] == "juan@test.com"
        assert data["rol"] == "cliente"
        assert "hashed_password" not in data

    def test_registro_email_duplicado(self, client):
        _register(client, "dup@test.com", "Primero")
        r = client.post("/auth/register", json={
            "nombre": "Segundo",
            "email": "dup@test.com",
            "password": "Test1234!",
            "rol": "cliente",
        })
        assert r.status_code == 409

    def test_registro_password_debil(self, client):
        r = client.post("/auth/register", json={
            "nombre": "Pepe",
            "email": "pepe@test.com",
            "password": "simple",
            "rol": "cliente",
        })
        assert r.status_code == 422

    def test_registro_rol_invalido_no_permite_admin(self, client):
        r = client.post("/auth/register", json={
            "nombre": "Hacker",
            "email": "hack@test.com",
            "password": "Test1234!",
            "rol": "admin",
        })
        assert r.status_code == 422

    def test_registro_taller_ok(self, client):
        r = client.post("/auth/register", json={
            "nombre": "Taller X",
            "email": "tallerx@test.com",
            "password": "Test1234!",
            "rol": "taller",
        })
        assert r.status_code == 201
        assert r.json()["rol"] == "taller"


class TestCU1_Login:
    def test_login_exitoso(self, client):
        _register(client, "login@test.com", "Login User")
        r = client.post("/auth/login", json={
            "email": "login@test.com",
            "password": "Test1234!",
        })
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_password_incorrecto(self, client):
        _register(client, "fail@test.com", "Fail User")
        r = client.post("/auth/login", json={
            "email": "fail@test.com",
            "password": "WrongPass9!",
        })
        assert r.status_code == 401

    def test_login_usuario_inexistente(self, client):
        r = client.post("/auth/login", json={
            "email": "noexiste@test.com",
            "password": "Test1234!",
        })
        assert r.status_code == 401


class TestCU2_Logout:
    def test_logout_exitoso(self, client):
        _register(client, "logout@test.com", "Logout User")
        token = _login(client, "logout@test.com")
        r = client.post("/auth/logout", headers=_auth_headers(token))
        assert r.status_code == 204

    def test_token_revocado_tras_logout(self, client):
        _register(client, "revoke@test.com", "Revoke User")
        token = _login(client, "revoke@test.com")
        client.post("/auth/logout", headers=_auth_headers(token))
        # Intentar usar el token revocado
        r = client.get("/me", headers=_auth_headers(token))
        assert r.status_code == 401


class TestCU4_RecuperarPassword:
    def test_forgot_password_usuario_existente(self, client):
        _register(client, "forgot@test.com", "Forgot User")
        r = client.post("/auth/forgot-password", json={"email": "forgot@test.com"})
        assert r.status_code == 200
        data = r.json()
        assert "message" in data
        # Con DEBUG_RESET_TOKEN=true el token se retorna en la respuesta
        assert "debug_token" in data

    def test_forgot_password_usuario_inexistente(self, client):
        r = client.post("/auth/forgot-password", json={"email": "ghost@test.com"})
        # Debe retornar 200 por seguridad (no revela si el email existe)
        assert r.status_code == 200

    def test_reset_password_con_token_valido(self, client):
        _register(client, "reset@test.com", "Reset User")
        forgot_r = client.post("/auth/forgot-password", json={"email": "reset@test.com"})
        debug_token = forgot_r.json().get("debug_token")
        if not debug_token:
            pytest.skip("DEBUG_RESET_TOKEN no está activo")

        r = client.post("/auth/reset-password", json={
            "token": debug_token,
            "new_password": "NewPass9!",
        })
        assert r.status_code == 204

        # Verificar que el nuevo password funciona
        login_r = client.post("/auth/login", json={
            "email": "reset@test.com",
            "password": "NewPass9!",
        })
        assert login_r.status_code == 200


class TestCU6_Perfil:
    def test_get_perfil(self, client, cliente_token):
        r = client.get("/me", headers=_auth_headers(cliente_token))
        assert r.status_code == 200
        data = r.json()
        assert "email" in data
        assert "vehiculos" in data

    def test_agregar_vehiculo(self, client, cliente_token):
        r = client.post("/me/vehicles", headers=_auth_headers(cliente_token), json={
            "marca": "Toyota",
            "modelo": "Corolla",
            "placa": "ABC-123",
            "anio": 2020,
            "color": "Blanco",
        })
        assert r.status_code == 201
        assert r.json()["placa"] == "ABC-123"

    def test_listar_vehiculos(self, client, cliente_token):
        client.post("/me/vehicles", headers=_auth_headers(cliente_token), json={
            "marca": "Kia", "modelo": "Rio", "placa": "DEF-456"
        })
        r = client.get("/me/vehicles", headers=_auth_headers(cliente_token))
        assert r.status_code == 200
        assert len(r.json()) >= 1

    def test_eliminar_vehiculo(self, client, cliente_token):
        v = client.post("/me/vehicles", headers=_auth_headers(cliente_token), json={
            "marca": "Honda", "modelo": "Civic", "placa": "GHI-789"
        }).json()
        r = client.delete(f"/me/vehicles/{v['id']}", headers=_auth_headers(cliente_token))
        assert r.status_code == 204
