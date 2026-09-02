"""
Pruebas automatizadas de Generación de Reportes Multiformato (PDF, Word, Excel).
"""
import pytest
from reports.pdf_generator import PDFReportGenerator
from reports.docx_generator import DocxReportGenerator
from reports.excel_generator import ExcelReportGenerator

@pytest.fixture
def mock_report_data():
    kpis = {"disponibilidad_pct": 95.0, "mtbf_horas": 320.0, "mttr_horas": 5.5, "alertas_criticas": 2}
    equipments = [{
        "id": 1, "codigo_tag": "PALA-01", "tipo_equipo": "Pala Eléctrica",
        "marca_modelo": "Komatsu P&H", "anio_fabricacion": 2021, "capacidad_carga_tn": 100.0,
        "ubicacion_tajo": "Tajo Norte", "estado_operativo": "OPERATIVO", "horas_acumuladas": 8500.0
    }]
    predictions = [{
        "id": 1, "codigo_tag": "PALA-01", "prob_falla": 0.85, "estado_predicho": "FALLA INMINENTE",
        "tipo_falla_estimada": "Falla Térmica", "nivel_criticidad": "CRITICO",
        "rtv_horas_estimadas": 24.0, "recomendacion_tecnica": "Revisar termostato"
    }]
    work_orders = [{
        "id": 1, "codigo_ot": "OT-001", "codigo_tag": "PALA-01", "prioridad": "ALTA",
        "titulo": "Inspección térmica", "estado": "PENDIENTE", "asignado_nombre": "Carlos"
    }]
    telemetry = [{
        "id": 1, "codigo_tag": "PALA-01", "fecha_hora": "2026-09-02 12:00:00",
        "temp_motor_c": 82.0, "presion_hidraulica_psi": 3200.0, "vibracion_rodamientos_mm_s": 2.1,
        "presion_aceite_psi": 50.0, "temp_refrigerante_c": 80.0, "rpm_motor": 1700.0,
        "voltaje_sistema_v": 26.0, "corriente_a": 150.0, "falla_registrada": False
    }]
    audit_logs = [{
        "id": 1, "created_at": "2026-09-02 12:00:00", "username": "admin", "rol": "Administrador",
        "accion": "LOGIN", "tabla_afectada": "usuarios", "ip_origen": "127.0.0.1"
    }]
    return kpis, equipments, predictions, work_orders, telemetry, audit_logs

def test_pdf_report_generation(mock_report_data):
    kpis, equipments, predictions, work_orders, _, _ = mock_report_data
    pdf_bytes = PDFReportGenerator.generate_executive_report(
        kpis=kpis, equipments=equipments, predictions=predictions,
        work_orders=work_orders, generated_by="Tester"
    )
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")

def test_docx_report_generation(mock_report_data):
    kpis, equipments, _, work_orders, _, _ = mock_report_data
    docx_bytes = DocxReportGenerator.generate_technical_report(
        kpis=kpis, equipments=equipments, models_benchmark={},
        statistical_results={}, work_orders=work_orders, author="Tester"
    )
    assert isinstance(docx_bytes, bytes)
    assert len(docx_bytes) > 1000
    # Archivos zip/docx empiezan con 'PK'
    assert docx_bytes.startswith(b"PK")

def test_excel_report_generation(mock_report_data):
    kpis, equipments, predictions, work_orders, telemetry, audit_logs = mock_report_data
    xlsx_bytes = ExcelReportGenerator.generate_full_workbook(
        kpis=kpis, equipments=equipments, telemetry=telemetry,
        predictions=predictions, work_orders=work_orders, audit_logs=audit_logs
    )
    assert isinstance(xlsx_bytes, bytes)
    assert len(xlsx_bytes) > 1000
    assert xlsx_bytes.startswith(b"PK")
