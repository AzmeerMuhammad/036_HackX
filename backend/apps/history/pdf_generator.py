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
    elements.append(Paragraph("Comprehensive Patient History Report", styles['Heading2']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Patient Info
    elements.append(Paragraph(f"<b>Patient:</b> {history_data.get('display_name', 'Anonymous')}", styles['Normal']))
    elements.append(Paragraph(f"<b>Username:</b> {history_data.get('username', 'N/A')}", styles['Normal']))
    if history_data.get('account_created'):
        elements.append(Paragraph(f"<b>Account Created:</b> {history_data.get('account_created', 'N/A')[:10]}", styles['Normal']))
    elements.append(Paragraph(f"<b>Report Generated:</b> {history_data.get('generated_at', 'N/A')[:19]}", styles['Normal']))
    elements.append(Paragraph(f"<b>Period:</b> Complete History (All Available Data)", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Watermark
    elements.append(Paragraph("CONFIDENTIAL - SafeSpace", watermark_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Statistics Summary
    stats = history_data.get('statistics', {})
    trends = history_data.get('trends', {})
    elements.append(Paragraph("Overview Statistics", heading_style))
    stats_data = [
        ['Metric', 'Value'],
        ['Total Journal Entries', str(stats.get('total_journal_entries', 0))],
        ['Total Chat Sessions', str(stats.get('total_chat_sessions', 0))],
        ['Total Chat Messages', str(stats.get('total_chat_messages', 0))],
        ['Escalated Sessions', str(stats.get('escalated_sessions', 0))],
        ['Total Escalations', str(stats.get('total_escalations', 0))],
        ['First Entry Date', stats.get('first_entry_date', 'N/A')[:10] if stats.get('first_entry_date') else 'N/A'],
        ['Last Entry Date', stats.get('last_entry_date', 'N/A')[:10] if stats.get('last_entry_date') else 'N/A'],
    ]
    stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(stats_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Trends Summary
    elements.append(Paragraph("Emotional Trends", heading_style))
    trends_data = [
        ['Metric', 'Value'],
        ['Average Sentiment', f"{trends.get('average_sentiment', 0):.2f}"],
        ['Average Emotional Intensity', f"{trends.get('average_intensity', 0):.2f}"],
        ['Average Mood Intensity', f"{trends.get('average_mood_intensity', 0):.2f}"],
        ['Total Risk Flags', str(trends.get('total_risk_flags', 0))],
        ['Average Chat Risk Score', f"{trends.get('average_chat_risk_score', 0):.2f}"],
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
    
    # Sentiment Distribution
    sentiment_dist = trends.get('sentiment_distribution', {})
    if sentiment_dist:
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("Sentiment Distribution", styles['Heading3']))
        sentiment_text = ', '.join([f"{k}: {v}" for k, v in sentiment_dist.items()])
        elements.append(Paragraph(sentiment_text, styles['Normal']))
    
    # Most Common Themes
    common_themes = trends.get('most_common_themes', [])
    if common_themes:
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("Most Common Themes", styles['Heading3']))
        themes_text = ', '.join([f"{t.get('theme', '')} ({t.get('count', 0)})" for t in common_themes[:10]])
        elements.append(Paragraph(themes_text, styles['Normal']))
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Journal Summaries - ALL entries
    journal_summaries = history_data.get('journal_summaries', [])
    if journal_summaries:
        elements.append(PageBreak())
        elements.append(Paragraph("Complete Journal History", heading_style))
        elements.append(Paragraph(f"Total Entries: {len(journal_summaries)}", styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        for idx, journal in enumerate(journal_summaries, 1):
            date_str = journal.get('date', 'N/A')[:10] if journal.get('date') else 'N/A'
            elements.append(Paragraph(f"<b>Entry #{idx} - {date_str}</b>", styles['Normal']))
            
            mood = journal.get('mood', 'Not specified')
            mood_intensity = journal.get('mood_intensity', 0.0)
            if mood != 'Not specified':
                elements.append(Paragraph(f"Mood: {mood} (Intensity: {mood_intensity:.2f})", styles['Normal']))
            
            summary = journal.get('summary', '')
            if summary:
                elements.append(Paragraph(f"Summary: {summary}", styles['Normal']))
            
            sentiment_score = journal.get('sentiment_score', 0.0)
            sentiment_label = journal.get('sentiment_label', 'neutral')
            intensity_score = journal.get('intensity_score', 0.0)
            elements.append(Paragraph(f"Sentiment: {sentiment_label} ({sentiment_score:.2f}) | Emotional Intensity: {intensity_score:.2f}", styles['Normal']))
            
            themes = journal.get('key_themes', [])
            if themes:
                elements.append(Paragraph(f"Themes: {', '.join(themes)}", styles['Normal']))
            
            emotions = journal.get('detected_emotions', [])
            if emotions:
                emotion_str = ', '.join([str(e) for e in emotions[:5]])  # Limit display
                elements.append(Paragraph(f"Detected Emotions: {emotion_str}", styles['Normal']))
            
            risk_flags = journal.get('risk_flags', {})
            if risk_flags and any(risk_flags.values()):
                active_risks = [k for k, v in risk_flags.items() if v]
                elements.append(Paragraph(f"<b>⚠️ Risk Flags: {', '.join(active_risks)}</b>", styles['Normal']))
            
            if journal.get('suggest_start_chat'):
                elements.append(Paragraph("<b>💬 Chat Session Recommended</b>", styles['Normal']))
            
            elements.append(Spacer(1, 0.2*inch))
            
            # Add page break every 5 entries to avoid overly long pages
            if idx % 5 == 0 and idx < len(journal_summaries):
                elements.append(PageBreak())
    else:
        elements.append(PageBreak())
        elements.append(Paragraph("Journal Entries", heading_style))
        elements.append(Paragraph("No journal entries found.", styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
    
    # Chat Sessions - ALL sessions
    chat_highlights = history_data.get('chat_highlights', [])
    if chat_highlights:
        elements.append(PageBreak())
        elements.append(Paragraph("Complete Chat Session History", heading_style))
        elements.append(Paragraph(f"Total Sessions: {len(chat_highlights)}", styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        for idx, chat in enumerate(chat_highlights, 1):
            session_id = chat.get('session_id', 'N/A')
            date_str = chat.get('created_at', 'N/A')[:10] if chat.get('created_at') else 'N/A'
            elements.append(Paragraph(f"<b>Session #{idx} (ID: {session_id}) - {date_str}</b>", styles['Normal']))
            
            status = chat.get('status', 'N/A')
            message_count = chat.get('message_count', 0)
            elements.append(Paragraph(f"Status: {status.upper()} | Messages: {message_count}", styles['Normal']))
            
            if chat.get('is_anonymous'):
                elements.append(Paragraph("Mode: Anonymous", styles['Normal']))
            
            session_summary = chat.get('session_summary', '')
            if session_summary:
                elements.append(Paragraph(f"Summary: {session_summary}", styles['Normal']))
            
            max_risk = chat.get('max_risk_score', 0.0)
            if max_risk > 0:
                elements.append(Paragraph(f"Max Risk Score: {max_risk:.2f}", styles['Normal']))
            
            sentiment_trend = chat.get('sentiment_trend', [])
            if sentiment_trend:
                avg_sentiment = sum(sentiment_trend) / len(sentiment_trend) if sentiment_trend else 0.0
                elements.append(Paragraph(f"Average Sentiment in Session: {avg_sentiment:.2f}", styles['Normal']))
            
            sop_categories = chat.get('active_sop_categories', [])
            if sop_categories:
                elements.append(Paragraph(f"SOP Categories Used: {', '.join(sop_categories)}", styles['Normal']))
            
            elements.append(Spacer(1, 0.2*inch))
            
            # Add page break every 3 sessions
            if idx % 3 == 0 and idx < len(chat_highlights):
                elements.append(PageBreak())
    else:
        elements.append(PageBreak())
        elements.append(Paragraph("Chat Sessions", heading_style))
        elements.append(Paragraph("No chat sessions found.", styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
    
    # Escalation Summary - ALL escalations
    escalation_summary = history_data.get('escalation_summary', [])
    if escalation_summary:
        elements.append(PageBreak())
        elements.append(Paragraph("Escalation History", heading_style))
        elements.append(Paragraph(f"Total Escalations: {len(escalation_summary)}", styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        for esc in escalation_summary:
            ticket_id = esc.get('ticket_id', 'N/A')
            date_str = esc.get('created_at', 'N/A')[:10] if esc.get('created_at') else 'N/A'
            elements.append(Paragraph(f"<b>Ticket #{ticket_id} - {date_str}</b>", styles['Normal']))
            
            status = esc.get('status', 'N/A')
            verdict = esc.get('verdict', 'N/A')
            elements.append(Paragraph(f"Status: {status.upper()} | Verdict: {verdict.replace('_', ' ').title() if verdict != 'pending' else 'Pending'}", styles['Normal']))
            
            reason = esc.get('reason', '')
            if reason:
                elements.append(Paragraph(f"Reason: {reason}", styles['Normal']))
            
            professional_notes = esc.get('professional_notes', '')
            if professional_notes:
                elements.append(Paragraph(f"Professional Notes: {professional_notes}", styles['Normal']))
            
            assigned = esc.get('assigned_professional', 'Unassigned')
            elements.append(Paragraph(f"Assigned Professional: {assigned}", styles['Normal']))
            
            reviewed_at = esc.get('reviewed_at', '')
            if reviewed_at:
                elements.append(Paragraph(f"Reviewed At: {reviewed_at[:10]}", styles['Normal']))
            
            elements.append(Spacer(1, 0.2*inch))
    else:
        elements.append(PageBreak())
        elements.append(Paragraph("Escalation History", heading_style))
        elements.append(Paragraph("No escalations found.", styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
    
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

