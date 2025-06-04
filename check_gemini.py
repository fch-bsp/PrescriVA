import os
import google.generativeai as genai
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def main():
    """
    Script para verificar os modelos Gemini disponíveis.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("ERRO: GOOGLE_API_KEY não encontrada no arquivo .env")
        return
    
    print(f"Usando API key: {api_key[:5]}...{api_key[-5:]}")
    
    try:
        # Configurar a API
        genai.configure(api_key=api_key)
        
        # Listar modelos disponíveis
        print("Listando modelos disponíveis:")
        models = genai.list_models()
        
        for model in models:
            print(f"- {model.name}")
            print(f"  Métodos suportados: {model.supported_generation_methods}")
            print()
        
        # Tentar usar o modelo gemini-pro
        print("Testando modelo gemini-pro:")
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Olá, como você está?")
        print(f"Resposta: {response.text}")
        
    except Exception as e:
        print(f"ERRO: {e}")

if __name__ == "__main__":
    main()