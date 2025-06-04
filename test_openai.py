import os
from dotenv import load_dotenv
from openai import OpenAI

# Carregar variáveis de ambiente
load_dotenv()

def test_openai_connection():
    """
    Testa a conexão com a API da OpenAI.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERRO: OPENAI_API_KEY não encontrada no arquivo .env")
        return
    
    print(f"Usando API key: {api_key[:5]}...{api_key[-5:]}")
    
    try:
        # Inicializar cliente OpenAI
        client = OpenAI(api_key=api_key)
        
        # Testar uma chamada simples
        print("Testando conexão com a API da OpenAI...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Modelo mais básico para teste
            messages=[
                {"role": "system", "content": "Você é um assistente útil."},
                {"role": "user", "content": "Olá, como você está?"}
            ]
        )
        
        print(f"Resposta recebida: {response.choices[0].message.content}")
        print("Conexão com a API da OpenAI estabelecida com sucesso!")
        
    except Exception as e:
        print(f"ERRO ao conectar com a API da OpenAI: {e}")

if __name__ == "__main__":
    test_openai_connection()