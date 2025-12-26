"""
PDF generator for patient history with branding and watermark.
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from io import BytesIO
from typing import Dict, Any


def generate_pdf(history_data: Dict[str, Any]) -> BytesIO:
    """Generate branded PDF from history JSON data."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    watermark_style = ParagraphStyle(
        'Watermark',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#93c5fd'),
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique'
    )
    
    # Title
    elements.append(Paragraph("SafeSpace", title_style))
    elements.append(Paragraph("Patient History Report", styles['Heading2']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Patient Info
    elements.append(Paragraph(f"<b>Patient:</b> {history_data.get('display_name', 'Anonymous')}", styles['Normal']))
    elements.append(Paragraph(f"<b>Report Generated:</b> {history_data.get('generated_at', 'N/A')}", styles['Normal']))
    elements.append(Paragraph(f"<b>Period:</b> Last 7 Days", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Watermark
    elements.append(Paragraph("CONFIDENTIAL - SafeSpace", watermark_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Trends Summary
    trends = history_data.get('trends', {})
    elements.append(Paragraph("Summary Trends", heading_style))
    trends_data = [
        ['Metric', 'Value'],
        ['Average Sentiment', f"{trends.get('average_sentiment', 0):.2f}"],
        ['Average Intensity', f"{trends.get('average_intensity', 0):.2f}"],
        ['Total Risk Flags', str(trends.get('total_risk_flags', 0))],
        ['Journal Entries', str(trends.get('total_journal_entries', 0))],
        ['Chat Sessions', str(trends.get('total_chat_sessions', 0))],
    ]
    trends_table = Table(trends_data, colWidths=[3*inch, 2*inch])
    trends_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(trends_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Journal Summaries
    journal_summaries = history_data.get('journal_summaries', [])
    if journal_summaries:
        elements.append(Paragraph("Journal Entries", heading_style))
        for idx, journal in enumerate(journal_summaries[:10], 1):  # Limit to 10 entries
            elements.append(Paragraph(f"<b>Entry {idx} - {journal.get('date', 'N/A')[:10]}</b>", styles['Normal']))
            elements.append(Paragraph(f"Summary: {journal.get('summary', 'N/A')}", styles['Normal']))
            elements.append(Paragraph(f"Sentiment: {journal.get('sentiment_score', 0):.2f} | Intensity: {journal.get('intensity_score', 0):.2f}", styles['Normal']))
            themes = journal.get('key_themes', [])
            if themes:
                elements.append(Paragraph(f"Themes: {', '.join(themes)}", styles['Normal']))
            risk_flags = journal.get('risk_flags', {})
            if any(risk_flags.values()):
                active_risks = [k for k, v in risk_flags.items() if v]
                elements.append(Paragraph(f"<b>Risk Flags: {', '.join(active_risks)}</b>", styles['Normal']))
            elements.append(Spacer(1, 0.15*inch))
    
    # Chat Highlights
    chat_highlights = history_data.get('chat_highlights', [])
    if chat_highlights:
        elements.append(PageBreak())
        elements.append(Paragraph("Chat Session Highlights", heading_style))
        for chat in chat_highlights[:5]:  # Limit to 5 sessions
            elements.append(Paragraph(f"<b>Session {chat.get('session_id')} - {chat.get('created_at', 'N/A')[:10]}</b>", styles['Normal']))
            elements.append(Paragraph(f"Status: {chat.get('status', 'N/A')} | Messages: {chat.get('message_count', 0)}", styles['Normal']))
            elements.append(Spacer(1, 0.15*inch))
    
    # Escalation Summary
    escalation_summary = history_data.get('escalation_summary', [])
    if escalation_summary:
        elements.append(Paragraph("Escalation History", heading_style))
        for esc in escalation_summary:
            elements.append(Paragraph(f"<b>Ticket {esc.get('ticket_id')}</b> - {esc.get('created_at', 'N/A')[:10]}", styles['Normal']))
            elements.append(Paragraph(f"Status: {esc.get('status', 'N/A')} | Verdict: {esc.get('verdict', 'N/A')}", styles['Normal']))
            elements.append(Spacer(1, 0.15*inch))
    
    # Footer watermark on every page
    def add_watermark(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica-Oblique', 40)
        canvas.setFillColor(colors.HexColor('#e0e7ff'), alpha=0.3)
        canvas.rotate(45)
        canvas.drawString(2*inch, 2*inch, "SafeSpace")
        canvas.restoreState()
    
    # Build PDF
    doc.build(elements, onFirstPage=add_watermark, onLaterPages=add_watermark)
    
    buffer.seek(0)
    return buffer

