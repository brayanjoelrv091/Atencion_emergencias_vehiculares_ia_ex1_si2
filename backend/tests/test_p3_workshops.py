"""
test_p3_workshops.py — Tests de Talleres (CU10-CU13).
"""

from tests.conftest import _auth_headers


def _create_workshop(client, token: str, nombre: str = "Taller Test") -> dict:
    r = client.post(
        "/workshops",
        headers=_auth_headers(token),
        json={
            "nombre": nombre,
            "direccion": "Calle Falsa 123",
            "latitud": -33.45,
            "longitud": -70.65,
            "especialidades": ["motor", "frenos"],
        },
    )
    assert r.status_code == 201, r.text
    return r.json()


class TestCU10_RegistrarTaller:
    def test_taller_puede_registrarse(self, client, taller_token):
        data = _create_workshop(client, taller_token)
        assert data["nombre"] == "Taller Test"
        assert data["esta_activo"] is True

    def test_cliente_no_puede_registrar_taller(self, client, cliente_token):
        r = client.post(
            "/workshops",
            headers=_auth_headers(cliente_token),
            json={"nombre": "X", "direccion": "Y", "latitud": -33.0, "longitud": -70.0},
        )
        assert r.status_code == 403

    def test_listar_talleres_activos_publico(self, client, taller_token):
        _create_workshop(client, taller_token, "Taller Público")
        r = client.get("/workshops/all")
        assert r.status_code == 200
        assert len(r.json()) >= 1

    def test_agregar_tecnico(self, client, taller_token):
        taller = _create_workshop(client, taller_token)
        r = client.post(
            f"/workshops/{taller['id']}/technicians",
            headers=_auth_headers(taller_token),
            json={"nombre": "Técnico Juan", "especialidad": "motor"},
        )
        assert r.status_code == 201
        assert r.json()["nombre"] == "Técnico Juan"


class TestCU11_CU12_Solicitudes:
    def test_listar_solicitudes_vacias(self, client, taller_token):
        taller = _create_workshop(client, taller_token)
        r = client.get(
            f"/workshops/{taller['id']}/requests",
            headers=_auth_headers(taller_token),
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)


class TestCU13_Historial:
    def test_historial_vacio(self, client, taller_token):
        taller = _create_workshop(client, taller_token)
        r = client.get(
            f"/workshops/{taller['id']}/history",
            headers=_auth_headers(taller_token),
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)
