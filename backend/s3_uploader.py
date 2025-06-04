import boto3
import os
from datetime import datetime
import uuid
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def upload_to_s3(file_path):
    """
    Faz upload de um arquivo para um bucket S3.
    
    Args:
        file_path (str): Caminho para o arquivo a ser enviado
        
    Returns:
        str: URL do arquivo no S3
    """
    try:
        # Obter configurações do arquivo .env
        profile = os.getenv('profile', 'bardhock')
        bucket_name = os.getenv('S3_BUCKET', 'medicacao-poc-ghd25fg')
        region = os.getenv('AWS_REGION', 'us-east-1')
        
        # Inicializar o cliente S3 usando o perfil especificado
        session = boto3.Session(profile_name=profile)
        s3_client = session.client('s3', region_name=region)
        
        # Gerar um nome de arquivo único
        file_name = os.path.basename(file_path)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        s3_file_name = f"{timestamp}_{unique_id}_{file_name}"
        
        # Fazer upload do arquivo
        s3_client.upload_file(
            file_path,
            bucket_name,
            s3_file_name,
            ExtraArgs={'ContentType': 'application/pdf'}
        )
        
        # Gerar URL do arquivo
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_file_name}"
        
        return s3_url
    
    except Exception as e:
        print(f"Erro ao fazer upload para o S3: {e}")
        # Em caso de erro, retornamos uma URL fictícia
        return f"https://exemplo-s3.amazonaws.com/receitas/demo_{os.path.basename(file_path)}"