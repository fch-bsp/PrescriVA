import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

# Carregar variáveis de ambiente
load_dotenv()

class GeminiAgent:
    def __init__(self):
        """
        Inicializa o agente Gemini com a chave da API do Google.
        """
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY não encontrada no arquivo .env")
        
        genai.configure(api_key=api_key)
        
        # Usar o modelo gemini-1.5-pro para maior precisão em tarefas complexas
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        print("Modelo Gemini inicializado: gemini-1.5-pro (modelo de alta precisão)")
        
        # Carregar dados de medicamentos e farmácias
        self.load_data()
    
    def load_data(self):
        """
        Carrega os dados de medicamentos e farmácias dos arquivos de texto.
        """
        try:
            # Carregar dados do banco de medicamentos
            with open('data/medicamentos.txt', 'r', encoding='utf-8') as f:
                self.medicamentos_data = f.read()
        except FileNotFoundError:
            self.medicamentos_data = "Arquivo de medicamentos não encontrado."
        
        try:
            # Carregar dados de farmácias
            with open('data/farmacias.txt', 'r', encoding='utf-8') as f:
                self.farmacias_data = f.read()
        except FileNotFoundError:
            self.farmacias_data = "Arquivo de farmácias não encontrado."
    
    def interpret_prescription(self, ocr_text):
        """
        Interpreta o texto da receita médica extraído pelo OCR.
        
        Args:
            ocr_text (str): Texto extraído da receita médica
            
        Returns:
            dict: Dicionário com as informações estruturadas da receita
        """
        prompt = f"""
        Você é um assistente especializado em interpretar receitas médicas.
        Analise o texto a seguir, que foi extraído de uma receita médica usando OCR, e estruture as informações com alta precisão.
        
        Texto da receita:
        {ocr_text}
        
        Extraia e organize as seguintes informações em formato JSON:
        - medico: nome do médico
        - paciente: nome do paciente
        - data: data da receita
        - medicamentos: lista de medicamentos, cada um contendo:
          - nome: nome do medicamento
          - dosagem: dosagem do medicamento
          - posologia: instruções de uso
          - duracao: duração do tratamento
        - observacoes: quaisquer observações adicionais
        
        Se alguma informação não estiver clara ou não for encontrada, indique como "Não identificado" em vez de tentar adivinhar.
        Retorne apenas o JSON, sem explicações adicionais.
        """
        
        try:
            # Configurar parâmetros de geração para maior precisão
            generation_config = {
                "temperature": 0.1,  # Temperatura mais baixa para respostas mais determinísticas
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048  # Garantir espaço suficiente para respostas detalhadas
            }
            
            # Gerar resposta com configurações específicas
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Extrair o JSON da resposta
            json_str = response.text
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
            
            prescription_data = json.loads(json_str)
            return prescription_data
        except Exception as e:
            print(f"Erro ao processar resposta do Gemini: {e}")
            # Retornar estrutura básica em caso de erro
            return {
                "medico": "Não identificado",
                "paciente": "Não identificado",
                "data": "Não identificada",
                "medicamentos": [],
                "observacoes": f"Erro ao processar a receita: {str(e)}"
            }
    
    def get_response(self, query, prescription_context=None):
        """
        Obtém uma resposta do agente Gemini para uma pergunta do usuário.
        
        Args:
            query (str): Pergunta do usuário
            prescription_context (dict): Contexto da prescrição atual
            
        Returns:
            str: Resposta do agente
        """
        # Construir o contexto com os dados disponíveis
        context = ""
        
        if prescription_context:
            context += f"""
            Contexto da receita atual:
            {json.dumps(prescription_context, indent=2, ensure_ascii=False)}
            """
        
        # Adicionar dados de medicamentos e farmácias ao contexto
        context += f"""
        Dados de medicamentos disponíveis:
        {self.medicamentos_data}
        
        Dados de farmácias disponíveis:
        {self.farmacias_data}
        """
        
        prompt = f"""
        Você é um assistente farmacêutico virtual chamado PrescriVA.
        Sua função é ajudar pacientes a entender suas receitas médicas e fornecer informações precisas sobre medicamentos.
        
        {context}
        
        Pergunta do paciente: {query}
        
        Forneça uma resposta clara, precisa e útil. Se não tiver informações suficientes, 
        indique isso e sugira que o paciente consulte um farmacêutico ou médico.
        Sempre alerte sobre os riscos da automedicação quando apropriado.
        """
        
        try:
            # Configurar parâmetros de geração para maior precisão
            generation_config = {
                "temperature": 0.2,
                "top_p": 0.95,
                "max_output_tokens": 1024
            }
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            return response.text
        except Exception as e:
            return f"Desculpe, ocorreu um erro ao processar sua pergunta: {str(e)}"