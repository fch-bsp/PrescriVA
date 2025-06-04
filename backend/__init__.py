# Inicialização do pacote backend
from .openai_agent import OpenAIAgent
from .ocr import process_image
from .pdf_generator import generate_pdf
from .s3_uploader import upload_to_s3
from .database import Database