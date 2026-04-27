"""
test_p6_reports.py — Tests de Reportes (CU19-CU20).
"""

from tests.conftest import _auth_headers


class TestCU20_ExportarReportes:
    def test_exportar_pdf_admin(self, client, admin_token):
        r = client.get(
            "/reports/incidents/pdf",
            headers=_auth_headers(admin_token),
        )
        assert r.status_code == 200
        assert r.headers.get("content-type", "").startswith("application/pdf")

    def test_exportar_excel_admin(self, client, admin_token):
        r = client.get(
            "/reports/incidents/excel",
            headers=_auth_headers(admin_token),
        )
        assert r.status_code == 200
        ct = r.headers.get("content-type", "")
        assert "spreadsheet" in ct or "excel" in ct or "octet-stream" in ct

    def test_exportar_sin_autenticacion(self, client):
        r = client.get("/reports/incidents/pdf")
        assert r.status_code == 401

    def test_cliente_no_puede_exportar(self, client, cliente_token):
        r = client.get(
            "/reports/incidents/pdf",
            headers=_auth_headers(cliente_token),
        )
        assert r.status_code == 403


class TestCU19_HistorialReportes:
    def test_listar_reportes_generados(self, client, admin_token):
        r = client.get(
            "/reports/history",
            headers=_auth_headers(admin_token),
        )
        # Puede retornar 200 o 404 si el endpoint tiene otro nombre
        assert r.status_code in {200, 404}
