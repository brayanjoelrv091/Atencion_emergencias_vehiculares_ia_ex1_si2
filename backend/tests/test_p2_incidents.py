"""
test_p2_incidents.py — Tests de Incidentes (CU7-CU9).
"""

from tests.conftest import _auth_headers


def _create_incident(client, token: str, **overrides) -> dict:
    payload = {
        "titulo": "Falla de motor",
        "descripcion": "El motor no arranca",
        "latitud": -33.4500,
        "longitud": -70.6500,
    } | overrides
    r = client.post(
        "/incidents",
        headers={**_auth_headers(token), "Content-Type": "application/json"},
        json=payload,
    )
    assert r.status_code == 201, r.text
    return r.json()


class TestCU7_ReportarIncidente:
    def test_crear_incidente_exitoso(self, client, cliente_token):
        data = _create_incident(client, cliente_token)
        assert data["titulo"] == "Falla de motor"
        assert data["estado"] == "nuevo"
        assert data["latitud"] == -33.4500

    def test_crear_incidente_sin_token(self, client):
        r = client.post("/incidents", json={
            "titulo": "Test", "latitud": -33.0, "longitud": -70.0,
        })
        assert r.status_code == 401

    def test_listar_mis_incidentes(self, client, cliente_token):
        _create_incident(client, cliente_token)
        _create_incident(client, cliente_token, titulo="Segundo incidente")
        r = client.get("/incidents/my", headers=_auth_headers(cliente_token))
        assert r.status_code == 200
        assert len(r.json()) >= 2

    def test_incidente_con_campos_opcionales(self, client, cliente_token):
        data = _create_incident(
            client, cliente_token,
            titulo="Choque leve",
            descripcion="Golpe en parachoques trasero",
            latitud=-33.4200,
            longitud=-70.6100,
        )
        assert data["descripcion"] == "Golpe en parachoques trasero"


class TestCU9_FichaIncidente:
    def test_obtener_detalle_incidente(self, client, cliente_token):
        inc = _create_incident(client, cliente_token)
        r = client.get(f"/incidents/{inc['id']}", headers=_auth_headers(cliente_token))
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == inc["id"]
        assert "medios" in data

    def test_incidente_inexistente_retorna_404(self, client, cliente_token):
        r = client.get("/incidents/99999", headers=_auth_headers(cliente_token))
        assert r.status_code == 404


class TestCU8_ClasificacionIA:
    def test_clasificar_incidente(self, client, cliente_token):
        inc = _create_incident(client, cliente_token)
        r = client.post(
            f"/incidents/{inc['id']}/classify",
            headers=_auth_headers(cliente_token),
        )
        # Puede retornar 200 (clasificado) o 422 si falta info
        assert r.status_code in {200, 201, 422}

    def test_clasificar_incidente_inexistente(self, client, cliente_token):
        r = client.post(
            "/incidents/99999/classify",
            headers=_auth_headers(cliente_token),
        )
        assert r.status_code == 404
