import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def create_invoice_pdf(data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=22, leading=26, textColor=colors.HexColor('#1E293B')
    )
    subtitle_style = ParagraphStyle(
        'DocSub', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=colors.HexColor('#64748B')
    )
    invoice_title_style = ParagraphStyle(
        'InvTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=22, leading=26, textColor=colors.HexColor('#2563EB'), alignment=2
    )
    meta_style = ParagraphStyle(
        'Meta', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9, leading=13, textColor=colors.HexColor('#475569'), alignment=2
    )
    section_head = ParagraphStyle(
        'SecHead', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=9, leading=11, textColor=colors.HexColor('#2563EB')
    )
    body_bold = ParagraphStyle(
        'BodyBold', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=colors.HexColor('#0F172A')
    )
    body_text = ParagraphStyle(
        'BodyText', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9, leading=13, textColor=colors.HexColor('#475569')
    )

    elements = []

    # Header section
    header_data = [
        [
            Paragraph("MIKE ROSS", title_style),
            Paragraph("INVOICE", invoice_title_style)
        ],
        [
            Paragraph("DISPATCH SERVICES", subtitle_style),
            Paragraph(f"<b>Invoice #:</b> {data['invoice_number']}<br/><b>Date:</b> {data['invoice_date']}<br/><b>Terms:</b> Due Upon Receipt", meta_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[270, 270])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 15))

    # Dispatcher & Billed To box
    address_data = [
        [
            Paragraph("DISPATCHER", section_head),
            Paragraph("BILLED TO", section_head)
        ],
        [
            Paragraph("<b>Mike Ross</b><br/>Independent Freight Dispatcher", body_text),
            Paragraph(f"<b>{data['carrier_name']}</b><br/>Carrier Partner", body_text)
        ]
    ]
    address_table = Table(address_data, colWidths=[270, 270])
    address_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LINEBEFORE', (0,0), (0,1), 2, colors.HexColor('#2563EB')),
        ('LINEBEFORE', (1,0), (1,1), 2, colors.HexColor('#0F172A')),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(address_table)
    elements.append(Spacer(1, 20))

    # Load Table Headers & Data
    th_style = ParagraphStyle('TH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.white)
    th_r_style = ParagraphStyle('THR', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.white, alignment=2)
    td_style = ParagraphStyle('TD', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=12)
    td_r_style = ParagraphStyle('TDR', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=12, alignment=2)

    table_content = [
        [
            Paragraph("LOAD DETAILS", th_style),
            Paragraph("ROUTE (PICKUP → DELIVERY)", th_style),
            Paragraph("LOAD AMOUNT", th_r_style),
            Paragraph(f"DISPATCH FEE ({data['percentage']}%)", th_r_style)
        ],
        [
            Paragraph(f"<b>Broker:</b> {data['broker_name']}<br/><font color='#64748B'>Contact: {data['broker_contact']}</font>", td_style),
            Paragraph(f"<b>Pick:</b> {data['pickup_location']} ({data['pickup_date']})<br/><b>Drop:</b> {data['drop_location']} ({data['drop_date']})", td_style),
            Paragraph(f"${data['load_amount']:,.2f}", td_r_style),
            Paragraph(f"${data['dispatch_fee']:,.2f}", td_r_style)
        ]
    ]

    load_table = Table(table_content, colWidths=[130, 210, 100, 100])
    load_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#F8FAFC')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
    ]))
    elements.append(load_table)
    elements.append(Spacer(1, 20))

    # Bottom Payment & Totals Table
    pay_title = ParagraphStyle('PayTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=11, textColor=colors.HexColor('#1E40AF'))
    pay_body = ParagraphStyle('PayBody', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=12, textColor=colors.HexColor('#334155'))
    tot_label = ParagraphStyle('TotLabel', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=12, textColor=colors.HexColor('#475569'))
    tot_val = ParagraphStyle('TotVal', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=12, alignment=2, textColor=colors.HexColor('#0F172A'))
    due_label = ParagraphStyle('DueLabel', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=14, textColor=colors.HexColor('#0F172A'))
    due_val = ParagraphStyle('DueVal', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=14, alignment=2, textColor=colors.HexColor('#2563EB'))

    summary_data = [
        [
            Paragraph("<b>PAYMENT METHOD: ZELLE</b>", pay_title),
            Paragraph("Total Gross Freight:", tot_label),
            Paragraph(f"${data['load_amount']:,.2f}", tot_val)
        ],
        [
            Paragraph("Account Name: <b>Babar Hussain</b><br/>Zelle Phone: <b>916-750-7274</b>", pay_body),
            Paragraph("Dispatch Fee Rate:", tot_label),
            Paragraph(f"{data['percentage']:.2f}%", tot_val)
        ],
        [
            Paragraph(f"<font color='#2563EB'>* Please include Invoice #{data['invoice_number']} in memo.</font>", pay_body),
            Paragraph("Total Due:", due_label),
            Paragraph(f"${data['dispatch_fee']:,.2f}", due_val)
        ]
    ]

    summary_table = Table(summary_data, colWidths=[280, 130, 130])
    summary_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (0,-1), 1, colors.HexColor('#BFDBFE')),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#EFF6FF')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('LINEABOVE', (1,2), (2,2), 1, colors.HexColor('#0F172A')),
    ]))
    elements.append(summary_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
