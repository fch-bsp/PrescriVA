import cv2
import numpy as np
import pytesseract
from PIL import Image
import os
import sys

def check_tesseract():
    """
    Verifica se o Tesseract OCR está instalado e disponível.
    Retorna instruções de instalação se não estiver.
    """
    try:
        pytesseract.get_tesseract_version()
        return True
    except pytesseract.TesseractNotFoundError:
        print("\n\n============== ERRO: TESSERACT NÃO ENCONTRADO ==============")
        print("O Tesseract OCR não está instalado ou não está no PATH.")
        print("\nPara instalar no Ubuntu/Debian:")
        print("    sudo apt-get install tesseract-ocr tesseract-ocr-por")
        print("\nPara instalar no macOS:")
        print("    brew install tesseract tesseract-lang")
        print("\nPara instalar no Windows:")
        print("    Baixe o instalador em: https://github.com/UB-Mannheim/tesseract/wiki")
        print("    E adicione o diretório de instalação ao PATH do sistema")
        print("===========================================================\n\n")
        return False

def process_image(image_path, openai_agent):
    """
    Processa a imagem da receita médica usando OCR e o agente OpenAI para extrair informações estruturadas.
    
    Args:
        image_path (str): Caminho para a imagem da receita
        openai_agent: Instância do agente OpenAI para interpretação
        
    Returns:
        dict: Dicionário com as informações estruturadas da receita
    """
    # Verificar se o Tesseract está instalado
    if not check_tesseract():
        # Retornar dados vazios se o Tesseract não estiver disponível
        return {
            "medico": "Erro: Tesseract OCR não encontrado",
            "paciente": "Por favor, instale o Tesseract OCR",
            "data": "",
            "medicamentos": [],
            "observacoes": "Não foi possível processar a receita porque o Tesseract OCR não está instalado."
        }
    
    try:
        # Carregar a imagem
        image = cv2.imread(image_path)
        
        # Verificar se a imagem foi carregada corretamente
        if image is None:
            raise ValueError(f"Não foi possível carregar a imagem: {image_path}")
        
        # Redimensionar a imagem se for muito grande (mantendo a proporção)
        max_dimension = 2000
        height, width = image.shape[:2]
        if max(height, width) > max_dimension:
            scale = max_dimension / max(height, width)
            image = cv2.resize(image, None, fx=scale, fy=scale)
        
        # Pré-processamento da imagem para melhorar o OCR
        # Converter para escala de cinza
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Aplicar desfoque gaussiano para reduzir ruído
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Aplicar limiarização adaptativa
        thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY_INV, 11, 2)
        
        # Aplicar operações morfológicas para melhorar a qualidade
        kernel = np.ones((1, 1), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        
        # Inverter a imagem para texto preto em fundo branco
        final_image = cv2.bitwise_not(opening)
        
        # Configurar o Tesseract para melhor reconhecimento de texto
        custom_config = r'--oem 3 --psm 6 -l por'
        
        # Realizar OCR na imagem processada
        text = pytesseract.image_to_string(final_image, config=custom_config)
        
        # Verificar se o texto extraído não está vazio
        if not text or text.strip() == "":
            return {
                "medico": "Não identificado",
                "paciente": "Não identificado",
                "data": "Não identificada",
                "medicamentos": [],
                "observacoes": "Não foi possível extrair texto da imagem. A imagem pode estar muito clara, escura ou desfocada."
            }
        
        print(f"Texto extraído pelo OCR: {text[:100]}...")  # Imprimir os primeiros 100 caracteres para debug
        
        # Usar o agente OpenAI para interpretar o texto extraído
        prescription_data = openai_agent.interpret_prescription(text)
        
        return prescription_data
    
    except Exception as e:
        print(f"Erro ao processar imagem: {e}")
        return {
            "medico": "Erro ao processar a imagem",
            "paciente": "Ocorreu um erro",
            "data": "",
            "medicamentos": [],
            "observacoes": f"Erro: {str(e)}"
        }