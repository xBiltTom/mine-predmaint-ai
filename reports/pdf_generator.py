"""
Generador de Reportes Ejecutivos en PDF usando ReportLab.
Diseño formal institucional con membrete UNT / Minería y tablas estilizadas.
"""
from io import BytesIO
from datetime import datetime
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

class PDFReportGenerator:
    @staticmethod
    def generate_executive_report(
        kpis: Dict[str, Any],
        equipments: List[Dict[str, Any]],
        predictions: List[Dict[str, Any]],
        work_orders: List[Dict[str, Any]],
        generated_by: str = "Ingeniero de Mantenimiento"
    ) -> bytes:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Estilos personalizados
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#1E293B")
        )
        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#64748B")
        )
        section_heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#0F766E"),
            spaceBefore=10,
            spaceAfter=6
        )
        cell_style = ParagraphStyle(
            "TableCell",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10
        )
        cell_header_style = ParagraphStyle(
            "TableHeaderCell",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=colors.white
        )

        story = []

        # Encabezado Institucional
        story.append(Paragraph("UNIVERSIDAD NACIONAL DE TRUJILLO — INGENIERÍA DE SOFTWARE II", subtitle_style))
        story.append(Paragraph("SISTEMA DE MANTENIMIENTO PREDICTIVO DE CARGUÍO MINERO (IA)", title_style))
        story.append(Paragraph(f"INFORME EJECUTIVO DE CONFIABILIDAD OPERACIONAL | {datetime.now().strftime('%d/%m/%Y %H:%M')}", subtitle_style))
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F766E"), spaceAfter=12))

        # 1. KPIs Principales
        story.append(Paragraph("1. Resumen Ejecutivo de Confiabilidad y Flota", section_heading))
        
        kpi_data = [
            [
                Paragraph("<b>Disponibilidad Flota:</b>", cell_style),
                Paragraph(f"{kpis.get('disponibilidad_pct', 94.2)}%", cell_style),
                Paragraph("<b>MTBF Estimado:</b>", cell_style),
                Paragraph(f"{kpis.get('mtbf_horas', 312.5)} hrs", cell_style)
            ],
            [
                Paragraph("<b>MTTR Promedio:</b>", cell_style),
                Paragraph(f"{kpis.get('mttr_horas', 6.4)} hrs", cell_style),
                Paragraph("<b>Alertas Críticas (7d):</b>", cell_style),
                Paragraph(f"{kpis.get('alertas_criticas', len(predictions))}", cell_style)
            ]
        ]
        kpi_table = Table(kpi_data, colWidths=[130, 130, 130, 130])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 14))

        # 2. Estado de Flota de Carguío
        story.append(Paragraph("2. Censo y Estado de Equipos de Carguío Minero", section_heading))
        eq_rows = [[
            Paragraph("TAG", cell_header_style),
            Paragraph("Equipo / Modelo", cell_header_style),
            Paragraph("Ubicación Tajo", cell_header_style),
            Paragraph("Horas Acum.", cell_header_style),
            Paragraph("Estado Operativo", cell_header_style)
        ]]
        for eq in equipments[:8]:
            eq_rows.append([
                Paragraph(eq["codigo_tag"], cell_style),
                Paragraph(f"{eq['tipo_equipo']}<br/>{eq['marca_modelo']}", cell_style),
                Paragraph(eq["ubicacion_tajo"], cell_style),
                Paragraph(f"{eq['horas_acumuladas']:.1f}", cell_style),
                Paragraph(eq["estado_operativo"], cell_style)
            ])
        eq_table = Table(eq_rows, colWidths=[70, 160, 130, 70, 90])
        eq_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(eq_table)
        story.append(Spacer(1, 14))

        # 3. Diagnósticos y Predicciones Críticas de la IA
        story.append(Paragraph("3. Diagnósticos Predictivos y Alertas Recientes", section_heading))
        pred_rows = [[
            Paragraph("Equipo", cell_header_style),
            Paragraph("Prob. Falla", cell_header_style),
            Paragraph("Criticidad", cell_header_style),
            Paragraph("Falla Estimada", cell_header_style),
            Paragraph("RUL Est.", cell_header_style),
            Paragraph("Recomendación Técnica", cell_header_style)
        ]]
        for p in predictions[:6]:
            pred_rows.append([
                Paragraph(p.get("codigo_tag", "EQ-XX"), cell_style),
                Paragraph(f"{p['prob_falla']*100:.1f}%", cell_style),
                Paragraph(p["nivel_criticidad"], cell_style),
                Paragraph(p["tipo_falla_estimada"], cell_style),
                Paragraph(f"{p.get('rtv_horas_estimadas', 0):.0f} hrs", cell_style),
                Paragraph(p["recomendacion_tecnica"][:75] + "...", cell_style)
            ])
        if len(pred_rows) == 1:
            pred_rows.append([Paragraph("Sin alertas críticas registradas", cell_style)] * 6)
        pred_table = Table(pred_rows, colWidths=[65, 55, 60, 110, 50, 180])
        pred_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0F766E")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(pred_table)
        story.append(Spacer(1, 20))

        # 4. Firma de Responsabilidad
        signature_data = [
            [
                Paragraph("___________________________________<br/><b>Generado Por:</b><br/>" + generated_by, cell_style),
                Paragraph("___________________________________<br/><b>V°B° Superintendencia de Mantenimiento</b><br/>Minera San Cristóbal S.A.", cell_style)
            ]
        ]
        sig_table = Table(signature_data, colWidths=[260, 260])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        story.append(KeepTogether([sig_table]))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
