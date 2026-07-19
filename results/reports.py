import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_patient_report(test_request):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#1A365D'),
        spaceAfter=5,
        alignment=1 # Center
    )
    
    header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor('#2B6CB0'),
        spaceBefore=15,
        spaceAfter=10
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=colors.HexColor('#2D3748')
    )
    
    body_bold_style = ParagraphStyle(
        'BodyTextBold',
        parent=styles['BodyText'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.HexColor('#2D3748')
    )
    
    # Title / Header
    story.append(Paragraph("EXCELSIOR LAB DIAGNOSTICS", title_style))
    story.append(Paragraph("123 MedTech Avenue, Silicon City | Tel: +1 555-0199 | email: lab@excelsior.com", ParagraphStyle('Sub', parent=styles['Normal'], alignment=1, spaceAfter=20)))
    story.append(Spacer(1, 0.1 * inch))
    
    # Demographics Box
    patient = test_request.encounter.patient
    dob_str = patient.date_of_birth.strftime("%Y-%m-%d")
    
    demo_data = [
        [Paragraph("<b>Patient Name:</b>", body_style), Paragraph(patient.full_name, body_bold_style),
         Paragraph("<b>Request Number:</b>", body_style), Paragraph(test_request.request_number, body_bold_style)],
        [Paragraph("<b>Age / Gender:</b>", body_style), Paragraph(f"{patient.gender} (DOB: {dob_str})", body_style),
         Paragraph("<b>Request Date:</b>", body_style), Paragraph(test_request.request_date.strftime("%Y-%m-%d %H:%M"), body_style)],
        [Paragraph("<b>Phone:</b>", body_style), Paragraph(patient.phone_number, body_style),
         Paragraph("<b>Physician:</b>", body_style), Paragraph(test_request.encounter.referring_physician or "Self/Walk-in", body_style)]
    ]
    
    demo_table = Table(demo_data, colWidths=[100, 160, 100, 160])
    demo_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F7FAFC')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E0')),
    ]))
    
    story.append(demo_table)
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("LABORATORY TEST RESULTS", header_style))
    
    # Results Table Headers
    results_data = [
        [Paragraph("<b>Test Name</b>", body_bold_style),
         Paragraph("<b>Result Value</b>", body_bold_style),
         Paragraph("<b>Reference Range</b>", body_bold_style),
         Paragraph("<b>Units</b>", body_bold_style),
         Paragraph("<b>Status</b>", body_bold_style)]
    ]
    
    # Loop over requested tests
    for rt in test_request.requested_tests.all():
        status_str = rt.get_status_display()
        
        has_result = hasattr(rt, 'result')
        has_params = has_result and rt.result.parameter_values.exists()
        
        if has_params:
            # 1. Main test header row
            results_data.append([
                Paragraph(f"<b>{rt.test.name}</b>", body_style),
                Paragraph("-", body_style),
                Paragraph("-", body_style),
                Paragraph("-", body_style),
                Paragraph(status_str, body_style)
            ])
            # 2. Sub-parameter values
            for pv in rt.result.parameter_values.all():
                val_display = pv.value
                if pv.flag == 'H':
                    val_display = f"<font color='red'><b>{pv.value} (H)</b></font>"
                elif pv.flag == 'L':
                    val_display = f"<font color='blue'><b>{pv.value} (L)</b></font>"
                
                results_data.append([
                    Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;&bull;&nbsp;{pv.parameter.name}", body_style),
                    Paragraph(val_display, body_style),
                    Paragraph(pv.parameter.normal_range, body_style),
                    Paragraph(pv.parameter.units or "-", body_style),
                    Paragraph("-", body_style)
                ])
        else:
            result_val = "Pending"
            if has_result:
                result_val = rt.result.value
                if rt.result.is_critical:
                    result_val = f"<font color='red'><b>{result_val} (CRITICAL)</b></font>"
                
            results_data.append([
                Paragraph(rt.test.name, body_style),
                Paragraph(result_val, body_style),
                Paragraph(rt.test.normal_range, body_style),
                Paragraph(rt.test.units or "-", body_style),
                Paragraph(status_str, body_style)
            ])
        
    results_table = Table(results_data, colWidths=[180, 110, 110, 60, 60])
    results_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EDF2F7')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('LINEBELOW', (0,0), (-1,0), 1.5, colors.HexColor('#4A5568')),
        ('LINEBELOW', (0,1), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
    ]))
    
    story.append(results_table)
    story.append(Spacer(1, 0.4 * inch))
    
    # Signatures
    pathologist_name = "Pending Verification"
    technician_name = "Pending Entry"
    
    for rt in test_request.requested_tests.all():
        if hasattr(rt, 'result'):
            if rt.result.recorded_by:
                technician_name = rt.result.recorded_by.get_full_name() or rt.result.recorded_by.username
            if rt.result.verified_by:
                pathologist_name = rt.result.verified_by.get_full_name() or rt.result.verified_by.username
                break
            
    sig_data = [
        [Paragraph("<b>Prepared By:</b>", body_style), Paragraph("<b>Verified & Approved By:</b>", body_style)],
        [Paragraph(f"Technician: {technician_name}", body_style), Paragraph(f"Pathologist: {pathologist_name}", body_bold_style)],
        [Paragraph("_____________________________", body_style), Paragraph("_____________________________", body_style)]
    ]
    
    sig_table = Table(sig_data, colWidths=[260, 260])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    
    story.append(sig_table)
    
    doc.build(story)
    buffer.seek(0)
    return buffer
