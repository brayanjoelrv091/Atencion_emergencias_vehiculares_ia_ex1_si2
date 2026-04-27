"""
test_p5_payments.py — Tests de Pagos y Notificaciones (CU16-CU18).
"""

from tests.conftest import _register, _login, _auth_headers


def _setup_incident(client, cliente_token: str) -> int:
    """Crea un incidente y retorna su ID."""
    r = client.post(
        "/incidents",
        headers={**_auth_headers(cliente_token), "Content-Type": "application/json"},
        json={"titulo": "Falla test pago", "latitud": -33.0, "longitud": -70.0},
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


class TestCU18_Pagos:
    def test_pago_exitoso(self, client, cliente_token):
        inc_id = _setup_incident(client, cliente_token)
        r = client.post(
            "/payments/process",
            headers=_auth_headers(cliente_token),
            json={
                "incidente_id": inc_id,
                "monto": 50000.0,
                "moneda": "CLP",
                "metodo_pago": "tarjeta",
            },
        )
        assert r.status_code == 201, r.text
        data = r.json()
        assert data["estado"] == "completado"
        assert data["transaccion_id"] is not None
        assert data["transaccion_id"].startswith("TXN-")

    def test_pago_duplicado_rechazado(self, client, cliente_token):
        inc_id = _setup_incident(client, cliente_token)
        payload = {
            "incidente_id": inc_id,
            "monto": 30000.0,
            "moneda": "CLP",
            "metodo_pago": "efectivo",
        }
        # Primer pago
        r1 = client.post("/payments/process", headers=_auth_headers(cliente_token), json=payload)
        assert r1.status_code == 201

        # Segundo pago — mismo incidente ya pagado
        r2 = client.post("/payments/process", headers=_auth_headers(cliente_token), json=payload)
        assert r2.status_code == 400
        assert "duplicad" in r2.json()["detail"].lower() or "ya tiene" in r2.json()["detail"].lower()

    def test_pago_incidente_de_otro_usuario(self, client, cliente_token):
        """Un cliente NO puede pagar incidentes de otro usuario."""
        # Crear otro cliente con su incidente
        _register(client, "otro@test.com", "Otro Cliente")
        otro_token = _login(client, "otro@test.com")
        inc_ajeno = _setup_incident(client, otro_token)

        r = client.post(
            "/payments/process",
            headers=_auth_headers(cliente_token),
            json={
                "incidente_id": inc_ajeno,
                "monto": 10000.0,
                "moneda": "CLP",
                "metodo_pago": "tarjeta",
            },
        )
        assert r.status_code == 403

    def test_pago_incidente_inexistente(self, client, cliente_token):
        r = client.post(
            "/payments/process",
            headers=_auth_headers(cliente_token),
            json={
                "incidente_id": 99999,
                "monto": 10000.0,
                "moneda": "USD",
                "metodo_pago": "tarjeta",
            },
        )
        assert r.status_code == 404

    def test_pago_sin_autenticacion(self, client):
        r = client.post(
            "/payments/process",
            json={"incidente_id": 1, "monto": 100.0, "moneda": "USD", "metodo_pago": "tarjeta"},
        )
        assert r.status_code == 401

    def test_historial_pagos_cliente(self, client, cliente_token):
        inc_id = _setup_incident(client, cliente_token)
        client.post(
            "/payments/process",
            headers=_auth_headers(cliente_token),
            json={"incidente_id": inc_id, "monto": 20000.0, "moneda": "CLP", "metodo_pago": "transferencia"},
        )
        r = client.get("/payments/history", headers=_auth_headers(cliente_token))
        assert r.status_code == 200
        assert len(r.json()) >= 1
