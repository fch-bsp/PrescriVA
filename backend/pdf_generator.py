from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os
import tempfile
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.units import inch
from reportlab.platypus.flowables import HRFlowable

def generate_pdf(prescription_data):
    """
    Gera um PDF com as informações da receita médica.
    
    Args:
        prescription_data (dict): Dicionário com as informações da receita
        
    Returns:
        str: Caminho para o arquivo PDF gerado
    """
    # Criar um arquivo temporário para o PDF
    temp_dir = tempfile.gettempdir()
    pdf_path = os.path.join(temp_dir, "receita_medica.pdf")
    
    # Configurar o documento
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Criar estilos personalizados
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1,  # Centralizado
        spaceAfter=12
    )
    
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10
    )
    
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=8
    )
    
    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.gray,
        alignment=TA_RIGHT
    )
    
    # Estilo para texto em células da tabela
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_LEFT,
        wordWrap='CJK',  # Permite quebra de linha para textos longos
        leading=12       # Espaçamento entre linhas
    )
    
    # Elementos do documento
    elements = []
    
    # Título
    elements.append(Paragraph("ORIENTAÇÕES SOBRE SUA RECEITA MÉDICA", title_style))
    elements.append(Spacer(1, 12))
    
    # Informações gerais
    elements.append(Paragraph(f"Paciente: {prescription_data.get('paciente', 'Não identificado')}", normal_style))
    elements.append(Paragraph(f"Médico: {prescription_data.get('medico', 'Não identificado')}", normal_style))
    elements.append(Paragraph(f"Data: {prescription_data.get('data', 'Não identificada')}", normal_style))
    elements.append(Spacer(1, 12))
    
    # Medicamentos
    elements.append(Paragraph("MEDICAMENTOS PRESCRITOS", subtitle_style))
    
    for i, med in enumerate(prescription_data.get('medicamentos', [])):
        elements.append(Paragraph(f"Medicamento {i+1}: {med.get('nome', 'Não identificado')}", normal_style))
        
        # Converter texto simples para parágrafos para permitir quebra de linha
        dosagem = Paragraph(med.get('dosagem', 'Não identificada'), cell_style)
        posologia = Paragraph(med.get('posologia', 'Não identificada'), cell_style)
        duracao = Paragraph(med.get('duracao', 'Não identificada'), cell_style)
        
        # Tabela com informações do medicamento
        data = [
            ["Dosagem", dosagem],
            ["Como tomar", posologia],
            ["Duração", duracao]
        ]
        
        # Ajustar largura da tabela e permitir quebra de linha
        table = Table(data, colWidths=[120, 350], rowHeights=None)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Alinhar ao topo
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LEFTPADDING', (1, 0), (1, -1), 6),  # Padding à esquerda para o texto
            ('RIGHTPADDING', (1, 0), (1, -1), 6)  # Padding à direita para o texto
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 12))
    
    # Observações
    if prescription_data.get('observacoes'):
        elements.append(Paragraph("OBSERVAÇÕES IMPORTANTES", subtitle_style))
        elements.append(Paragraph(prescription_data.get('observacoes', ''), normal_style))
        elements.append(Spacer(1, 12))
    
    # Alertas e recomendações
    elements.append(Paragraph("ALERTAS E RECOMENDAÇÕES", subtitle_style))
    elements.append(Paragraph("• Não se automedique. Siga sempre as orientações médicas.", normal_style))
    elements.append(Paragraph("• Mantenha os medicamentos fora do alcance de crianças.", normal_style))
    elements.append(Paragraph("• Verifique a data de validade dos medicamentos antes de usá-los.", normal_style))
    elements.append(Paragraph("• Em caso de reações adversas, procure orientação médica imediatamente.", normal_style))
    
    # Adicionar linha horizontal para separar o conteúdo do rodapé
    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
    elements.append(Spacer(1, 10))
    
    # Criar tabela para o rodapé com logo e texto
    logo_path = "assets/bspcloud_logo.png"
    if os.path.exists(logo_path):
        # Criar uma tabela com duas colunas: texto à esquerda, logo à direita
        footer_text = Paragraph("Desenvolvido por | Fernando Horas", footer_style)
        logo = Image(logo_path, width=1*inch, height=0.4*inch)
        
        footer_data = [[footer_text, logo]]
        footer_table = Table(footer_data, colWidths=[350, 120])
        footer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (1, 0), 'MIDDLE'),
        ]))
        
        elements.append(footer_table)
    else:
        # Se o logo não existir, apenas adicionar o texto
        elements.append(Paragraph("Desenvolvido por | Fernando Horas", footer_style))
    
    # Gerar o PDF
    doc.build(elements)
    
    return pdf_path