import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_quotation_pdf(quotation, brand):
    """
    Generates a professional PDF quotation for Virat Tent House.
    """
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
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#8A1424') # Royal Maroon
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#4A5568')
    )

    header_right = ParagraphStyle(
        'HeaderRight',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        alignment=2, # Right align
        textColor=colors.HexColor('#1A202C')
    )

    meta_label = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#2D3748')
    )

    meta_val = ParagraphStyle(
        'MetaVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1A202C')
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=colors.white,
        alignment=1 # Center
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12
    )

    elements = []

    # Header Row
    header_data = [
        [
            Paragraph(f"<b>{brand.business_name}</b>", title_style),
            Paragraph(f"<b>QUOTATION</b><br/><font color='#718096' size='9'>#{quotation.quotation_number}</font>", header_right)
        ],
        [
            Paragraph(f"{brand.tagline}<br/>{brand.address}<br/>Phone: {brand.phone_number} | Email: {brand.email}", subtitle_style),
            Paragraph(f"<b>Date:</b> {quotation.created_at.strftime('%d-%b-%Y')}<br/><b>Valid Until:</b> {quotation.valid_until.strftime('%d-%b-%Y') if quotation.valid_until else 'N/A'}", subtitle_style)
        ]
    ]

    header_table = Table(header_data, colWidths=[3.8 * inch, 3.7 * inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 12))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#CFA83B'), spaceBefore=1, spaceAfter=12))

    # Customer & Event Information Block
    info_data = [
        [
            Paragraph("<b>CUSTOMER DETAILS</b>", meta_label),
            Paragraph("<b>EVENT DETAILS</b>", meta_label)
        ],
        [
            Paragraph(f"<b>Name:</b> {quotation.customer.name}<br/><b>Phone:</b> {quotation.customer.phone}<br/><b>Email:</b> {quotation.customer.email or 'N/A'}", meta_val),
            Paragraph(f"<b>Event:</b> {quotation.event_type}<br/><b>Date:</b> {quotation.event_date.strftime('%d-%b-%Y')}<br/><b>Venue:</b> {quotation.venue}", meta_val)
        ]
    ]
    info_table = Table(info_data, colWidths=[3.75 * inch, 3.75 * inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8F9FA')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 14))

    # Itemized Breakdown Table
    items_header = [
        Paragraph("<b>#</b>", table_header_style),
        Paragraph("<b>Service / Item Description</b>", table_header_style),
        Paragraph("<b>Qty</b>", table_header_style),
        Paragraph("<b>Rate (₹)</b>", table_header_style),
        Paragraph("<b>Total (₹)</b>", table_header_style)
    ]
    items_rows = [items_header]

    idx = 1
    for item in quotation.items.all():
        items_rows.append([
            Paragraph(str(idx), table_cell_style),
            Paragraph(item.description, table_cell_style),
            Paragraph(str(item.quantity), table_cell_style),
            Paragraph(f"{item.unit_price:,.2f}", table_cell_style),
            Paragraph(f"{item.total_price:,.2f}", table_cell_style),
        ])
        idx += 1

    if idx == 1:
        items_rows.append([
            Paragraph("1", table_cell_style),
            Paragraph(quotation.title, table_cell_style),
            Paragraph("1", table_cell_style),
            Paragraph(f"{quotation.subtotal:,.2f}", table_cell_style),
            Paragraph(f"{quotation.subtotal:,.2f}", table_cell_style),
        ])

    items_table = Table(items_rows, colWidths=[0.4 * inch, 3.9 * inch, 0.8 * inch, 1.2 * inch, 1.2 * inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8A1424')),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E0')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FCFDFD')]),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 10))

    # Summary Totals Table
    totals_data = [
        [Paragraph("<b>Subtotal:</b>", meta_val), Paragraph(f"₹{quotation.subtotal:,.2f}", meta_val)],
        [Paragraph("<b>Discount:</b>", meta_val), Paragraph(f"- ₹{quotation.discount:,.2f}", meta_val)],
        [Paragraph(f"<b>GST / Tax ({quotation.tax_rate}%):</b>", meta_val), Paragraph(f"₹{quotation.tax_amount:,.2f}", meta_val)],
        [Paragraph("<b>Grand Total:</b>", meta_label), Paragraph(f"<b>₹{quotation.grand_total:,.2f}</b>", meta_label)],
        [Paragraph("<b>Advance Required (30%):</b>", meta_val), Paragraph(f"₹{quotation.advance_required:,.2f}", meta_val)],
        [Paragraph("<b>Balance on Setup:</b>", meta_val), Paragraph(f"₹{max(0, quotation.grand_total - quotation.advance_required):,.2f}", meta_val)],
    ]
    totals_table = Table(totals_data, colWidths=[2.2 * inch, 1.4 * inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#FFF9E6')),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('LINEABOVE', (0, 3), (-1, 3), 1, colors.HexColor('#CFA83B')),
        ('LINEBELOW', (0, 3), (-1, 3), 1, colors.HexColor('#CFA83B')),
    ]))

    # Wrap Totals Table in a container right aligned
    layout_data = [
        [
            Paragraph("<b>Terms & Conditions:</b><br/>" + quotation.terms_and_conditions.replace('\n', '<br/>'), subtitle_style),
            totals_table
        ]
    ]
    summary_layout = Table(layout_data, colWidths=[3.9 * inch, 3.6 * inch])
    summary_layout.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(summary_layout)
    elements.append(Spacer(1, 20))

    # Signatures
    sign_data = [
        [Paragraph("Customer Signature & Acceptance", subtitle_style), Paragraph(f"Authorized Signatory<br/><b>{brand.business_name}</b>", header_right)]
    ]
    sign_table = Table(sign_data, colWidths=[3.75 * inch, 3.75 * inch])
    sign_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
        ('LINEABOVE', (0, 0), (0, 0), 1, colors.HexColor('#718096')),
        ('LINEABOVE', (1, 0), (1, 0), 1, colors.HexColor('#718096')),
    ]))
    elements.append(sign_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer
