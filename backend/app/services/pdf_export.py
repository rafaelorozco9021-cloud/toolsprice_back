from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable, Image
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
from datetime import datetime

TYPE_LABELS = {
    "construccion": "Construcción",
    "soldadura": "Soldadura",
    "pintura": "Pintura",
    "plomeria": "Plomería",
    "herramientas": "Herramientas",
    "mano_obra": "Mano de Obra",
}

def _fmt_cop(v: float) -> str:
    return f"${v:,.0f}".replace(",", ".") + " COP"

def generate_budget_pdf(budget, items: list[dict]) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.6*inch,
        rightMargin=0.6*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch,
        title=f"ToolsPrice - Presupuesto {getattr(budget, 'budget_type', 'construccion')}",
        author="ToolsPrice"
    )

    elements = []
    styles = getSampleStyleSheet()

    # --- HEADER ToolsPrice grande centrado ---
    brand_style = ParagraphStyle(
        'Brand',
        parent=styles['Heading1'],
        fontSize=34,
        leading=36,
        textColor=colors.HexColor('#4F46E5'),
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceAfter=2,
    )
    # Tracking effect: add letter spacing via HTML? Use simple
    elements.append(Paragraph("ToolsPrice", brand_style))

    # Subtitulo Presupuesto de [Tipo]
    btype = getattr(budget, 'budget_type', 'construccion') or 'construccion'
    label = TYPE_LABELS.get(btype.lower(), btype.capitalize())
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        leading=16,
        textColor=colors.HexColor('#6B7280'),
        alignment=TA_CENTER,
        fontName='Helvetica',
        spaceAfter=6,
        textTransform='uppercase',
    )
    elements.append(Paragraph(f"Presupuesto de {label}", subtitle_style))

    # linea decorativa
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#4F46E5'), spaceBefore=4, spaceAfter=12))

    # --- INFO BLOQUE organizado en 2 columnas ---
    info_left_style = ParagraphStyle('InfoLeft', parent=styles['Normal'], fontSize=9, leading=12, textColor=colors.HexColor('#374151'), spaceAfter=3)
    info_right_style = ParagraphStyle('InfoRight', parent=styles['Normal'], fontSize=9, leading=12, textColor=colors.HexColor('#374151'), alignment=TA_RIGHT, spaceAfter=3)
    label_style = ParagraphStyle('Label', parent=styles['Normal'], fontSize=8, leading=10, textColor=colors.HexColor('#9CA3AF'), alignment=TA_LEFT, fontName='Helvetica-Bold')
    label_r = ParagraphStyle('LabelR', parent=label_style, alignment=TA_RIGHT)

    bid_short = str(budget.id)[:8].upper()
    fecha = budget.created_at.strftime('%d/%m/%Y %H:%M') if hasattr(budget.created_at, 'strftime') else str(budget.created_at)[:10]
    tipo_txt = label

    # Usar tabla 2 columnas para info
    info_data = [
        [Paragraph('<font color="#9CA3AF"><b>N° PRESUPUESTO</b></font>', label_style), Paragraph(f'<b>#{bid_short}</b>', info_right_style)],
        [Paragraph('<font color="#9CA3AF"><b>FECHA</b></font>', label_style), Paragraph(fecha, info_right_style)],
        [Paragraph('<font color="#9CA3AF"><b>TIPO</b></font>', label_style), Paragraph(f'<font color="#EA580C"><b>{tipo_txt}</b></font>', info_right_style)],
        [Paragraph(f'<font color="#6B7280">{budget.name}</font>', info_left_style), Paragraph(f'<b>{len(items)} ítems</b> · Homecenter', info_right_style)],
    ]
    info_table = Table(info_data, colWidths=[3.2*inch, 3.5*inch])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.HexColor('#E5E7EB')),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 12))

    # Descripción si existe
    if getattr(budget, 'description', None) and budget.description != f"Presupuesto de {btype}":
        desc_style = ParagraphStyle('Desc', parent=styles['Normal'], fontSize=9, leading=11, textColor=colors.HexColor('#6B7280'), fontName='Helvetica-Oblique', alignment=TA_CENTER, spaceAfter=8, borderPadding=(6,6,6), backColor=colors.HexColor('#F9FAFB'))
        elements.append(Paragraph(budget.description, desc_style))
        elements.append(Spacer(1, 6))

    # --- TABLA PRODUCTOS ---
    data = [[
        Paragraph('<b><font color="white">Producto</font></b>', styles['Normal']),
        Paragraph('<b><font color="white">Cant.</font></b>', styles['Normal']),
        Paragraph('<b><font color="white">P. Unit.</font></b>', styles['Normal']),
        Paragraph('<b><font color="white">Subtotal</font></b>', styles['Normal']),
    ]]
    for item in items:
        if isinstance(item, dict):
            pn = item.get("product_name", "")
            qty = item.get("quantity", 1)
            up = item.get("unit_price", 0)
            tp = item.get("total_price", float(up) * int(qty))
        else:
            pn = getattr(item, "product_name", "")
            qty = getattr(item, "quantity", 1)
            up = getattr(item, "unit_price", 0)
            tp = getattr(item, "total_price", float(up) * int(qty))
        # escapar html
        pn_esc = pn.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")[:55]
        data.append([
            Paragraph(f'<font size=8>{pn_esc}</font>', ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, leading=10)),
            Paragraph(f'<font size=8>{qty}</font>', ParagraphStyle('cellC', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER)),
            Paragraph(f'<font size=8>{_fmt_cop(float(up))}</font>', ParagraphStyle('cellR', parent=styles['Normal'], fontSize=8, alignment=TA_RIGHT)),
            Paragraph(f'<font size=8><b>{_fmt_cop(float(tp))}</b></font>', ParagraphStyle('cellR', parent=styles['Normal'], fontSize=8, alignment=TA_RIGHT)),
        ])

    col_widths = [3.4*inch, 0.7*inch, 1.4*inch, 1.4*inch]
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,1), (-1,-1), 6),
        ('BOTTOMPADDING', (0,1), (-1,-1), 6),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 14))

    # --- TOTALES alineados a la derecha ---
    totals_data = [
        [Paragraph('<font color="#6B7280">Subtotal</font>', ParagraphStyle('tlab', parent=styles['Normal'], fontSize=9, alignment=TA_RIGHT)), Paragraph(_fmt_cop(float(budget.subtotal)), ParagraphStyle('tval', parent=styles['Normal'], fontSize=9, alignment=TA_RIGHT))],
        [Paragraph('<font color="#6B7280">IVA (16%)</font>', ParagraphStyle('tlab', parent=styles['Normal'], fontSize=9, alignment=TA_RIGHT)), Paragraph(_fmt_cop(float(budget.tax_amount)), ParagraphStyle('tval', parent=styles['Normal'], fontSize=9, alignment=TA_RIGHT))],
        [Paragraph('<b><font color="#4F46E5" size=11>TOTAL</font></b>', ParagraphStyle('tlab2', parent=styles['Normal'], fontSize=11, alignment=TA_RIGHT, textColor=colors.HexColor('#4F46E5'))), Paragraph(f'<b><font color="#4F46E5" size=11>{_fmt_cop(float(budget.total))}</font></b>', ParagraphStyle('tval2', parent=styles['Normal'], fontSize=11, alignment=TA_RIGHT, textColor=colors.HexColor('#4F46E5')))],
    ]
    totals_table = Table(totals_data, colWidths=[5.0*inch, 1.9*inch])
    totals_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 2), (-1, 2), 2, colors.HexColor('#4F46E5')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 18))

    # --- NOTA ---
    note_style = ParagraphStyle('Note', parent=styles['Normal'], fontSize=7, leading=9, textColor=colors.HexColor('#9CA3AF'), alignment=TA_CENTER, spaceAfter=20)
    elements.append(Paragraph("Precios obtenidos en tiempo real de <b>Homecenter (homecenter.com.co)</b> · Categoría Materiales de Construcción · Vigencia sujeta a disponibilidad", note_style))

    # --- FIRMA DIGITAL ---
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="55%", thickness=0.7, color=colors.HexColor('#9CA3AF'), spaceBefore=30, spaceAfter=6, hAlign='CENTER'))
    # Firma estilo script
    sig_style = ParagraphStyle('Sig', parent=styles['Normal'], fontSize=18, leading=20, textColor=colors.HexColor('#1F2937'), alignment=TA_CENTER, fontName='Helvetica-Oblique')
    # Usamos texto cursivo como firma digital
    elements.append(Paragraph("<font color=\"#4F46E5\">ToolsPrice</font> · Firma Digital", sig_style))
    sig_sub = ParagraphStyle('SigSub', parent=styles['Normal'], fontSize=8, leading=10, textColor=colors.HexColor('#6B7280'), alignment=TA_CENTER, spaceAfter=2)
    elements.append(Paragraph(f"Documento generado electrónicamente por <b>ToolsPrice</b>", sig_sub))
    elements.append(Paragraph(f"ID: {bid_short} · {datetime.utcnow().strftime('%d/%m/%Y %H:%M UTC')} · Verificación: toolsprice.homecenter/{bid_short.lower()}", sig_sub))
    elements.append(Paragraph("Este presupuesto tiene validez de 7 días y no constituye reserva de inventario.", ParagraphStyle('SigNote', parent=sig_sub, fontSize=7, textColor=colors.HexColor('#9CA3AF'), spaceBefore=6)))

    # Footer pequeño
    elements.append(Spacer(1, 14))
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=7, leading=8, textColor=colors.HexColor('#9CA3AF'), alignment=TA_CENTER)
    elements.append(Paragraph("ToolsPrice · www.toolsprice.co · contacto@toolsprice.co · Scraping exclusivo Homecenter", footer_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
