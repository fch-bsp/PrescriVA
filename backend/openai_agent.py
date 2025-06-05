import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import time

# Carregar variáveis de ambiente
load_dotenv()

class OpenAIAgent:
    def __init__(self):
        """
        Inicializa o agente OpenAI com a chave da API.
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY não encontrada no arquivo .env")
        
        # Inicializar cliente OpenAI apenas com a chave da API
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-3.5-turbo"  # Usando um modelo mais confiável e amplamente disponível
        print(f"Modelo OpenAI inicializado: {self.model}")
        
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
    
    def interpret_prescription(self, ocr_text, system_prompt=None):
        """
        Interpreta o texto da receita médica extraído pelo OCR.
        
        Args:
            ocr_text (str): Texto extraído da receita médica
            system_prompt (str, optional): Prompt de sistema personalizado
            
        Returns:
            dict: Dicionário com as informações estruturadas da receita
        """
        # Verificar se o texto OCR está vazio
        if not ocr_text or ocr_text.strip() == "":
            return {
                "medico": "Não identificado",
                "paciente": "Não identificado",
                "data": "Não identificada",
                "medicamentos": [],
                "observacoes": "Texto da receita vazio ou não reconhecido pelo OCR."
            }
        
        # Usar o prompt personalizado se fornecido, caso contrário usar o padrão
        if system_prompt is None:
            system_prompt = """
            Você é um assistente especializado em interpretar receitas médicas com alta precisão.
            """
            
        prompt = f"""
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
        """
        
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                # Fazer a chamada para a API da OpenAI
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,  # Temperatura baixa para respostas mais determinísticas
                    response_format={"type": "json_object"}  # Garantir resposta em formato JSON
                )
                
                # Verificar se a resposta contém conteúdo
                if not response or not response.choices or not response.choices[0].message or not response.choices[0].message.content:
                    if attempt < max_retries - 1:
                        print(f"Tentativa {attempt+1} falhou. Tentando novamente em {retry_delay} segundos...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        raise ValueError("Resposta vazia da API OpenAI após várias tentativas")
                
                # Extrair o JSON da resposta
                json_str = response.choices[0].message.content
                if not json_str:
                    if attempt < max_retries - 1:
                        print(f"Conteúdo vazio na tentativa {attempt+1}. Tentando novamente em {retry_delay} segundos...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        raise ValueError("Conteúdo da resposta vazio após várias tentativas")
                
                # Tentar analisar o JSON
                try:
                    prescription_data = json.loads(json_str)
                    return prescription_data
                except json.JSONDecodeError as e:
                    if attempt < max_retries - 1:
                        print(f"Erro ao decodificar JSON na tentativa {attempt+1}: {e}. Tentando novamente...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        raise ValueError(f"Falha ao decodificar JSON após várias tentativas: {e}")
            
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Erro na tentativa {attempt+1}: {e}. Tentando novamente em {retry_delay} segundos...")
                    time.sleep(retry_delay)
                    continue
                else:
                    print(f"Erro após {max_retries} tentativas: {e}")
                    raise
        
        # Se chegamos aqui, todas as tentativas falharam
        return {
            "medico": "Não identificado",
            "paciente": "Não identificado",
            "data": "Não identificada",
            "medicamentos": [],
            "observacoes": "Não foi possível interpretar a receita após várias tentativas."
        }
    
    def get_response(self, query, prescription_context=None, system_prompt=None):
        """
        Obtém uma resposta do agente OpenAI para uma pergunta do usuário.
        
        Args:
            query (str): Pergunta do usuário
            prescription_context (dict): Contexto da prescrição atual
            system_prompt (str, optional): Prompt de sistema personalizado
            
        Returns:
            str: Resposta do agente
        """
        # Construir o contexto com os dados disponíveis
        context = ""
        
        if prescription_context:
            try:
                context += f"""
                Contexto da receita atual:
                {json.dumps(prescription_context, indent=2, ensure_ascii=False)}
                """
            except Exception as e:
                context += "Contexto da receita não disponível devido a um erro."
                print(f"Erro ao serializar contexto da prescrição: {e}")
        
        # Adicionar dados de medicamentos e farmácias ao contexto
        context += f"""
        Dados de medicamentos disponíveis:
        {self.medicamentos_data}
        
        Dados de farmácias disponíveis:
        {self.farmacias_data}
        """
        
        # Usar o prompt personalizado se fornecido, caso contrário usar o padrão
        if system_prompt is None:
            system_prompt = """
            Você é um assistente farmacêutico virtual chamado PrescriVA.
            Sua função é ajudar pacientes a entender suas receitas médicas e fornecer informações precisas sobre medicamentos.
            Forneça respostas claras, precisas e úteis. Se não tiver informações suficientes, 
            indique isso e sugira que o paciente consulte um farmacêutico ou médico.
            Sempre alerte sobre os riscos da automedicação quando apropriado.
            """
        
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                # Fazer a chamada para a API da OpenAI
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"{context}\n\nPergunta do paciente: {query}"}
                    ],
                    temperature=0.3
                )
                
                if not response or not response.choices or not response.choices[0].message:
                    if attempt < max_retries - 1:
                        print(f"Tentativa {attempt+1} falhou. Tentando novamente em {retry_delay} segundos...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        return "Desculpe, não foi possível obter uma resposta após várias tentativas. Por favor, tente novamente mais tarde."
                
                content = response.choices[0].message.content
                if not content:
                    if attempt < max_retries - 1:
                        print(f"Conteúdo vazio na tentativa {attempt+1}. Tentando novamente em {retry_delay} segundos...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        return "Resposta vazia após várias tentativas. Por favor, tente reformular sua pergunta."
                
                return content
            
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Erro na tentativa {attempt+1}: {e}. Tentando novamente em {retry_delay} segundos...")
                    time.sleep(retry_delay)
                    continue
                else:
                    return f"Desculpe, ocorreu um erro após várias tentativas: {str(e)}"
        
        # Se chegamos aqui, todas as tentativas falharam
        return "Não foi possível obter uma resposta. Por favor, tente novamente mais tarde."