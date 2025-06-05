import os
from enum import Enum
from backend.openai_agent import OpenAIAgent
from backend.gemini_agent import GeminiAgent
from backend.model_instructions import CHAT_INSTRUCTIONS, PRESCRIPTION_ANALYSIS_INSTRUCTIONS

class TaskType(Enum):
    """Enum para definir os tipos de tarefas que podem ser roteadas."""
    CHAT = "chat"  # Conversa com cliente
    PRESCRIPTION_ANALYSIS = "prescription_analysis"  # Análise de atestado/receita

class ModelRouter:
    """
    Classe responsável por rotear solicitações para o modelo mais adequado
    com base no tipo de tarefa.
    """
    def __init__(self):
        """
        Inicializa o roteador de modelos carregando os agentes disponíveis.
        """
        # Inicializar os agentes sob demanda para economizar recursos
        self._openai_agent = None
        self._gemini_agent = None
        
        # Definir o mapeamento de tarefas para modelos
        self.task_model_mapping = {
            TaskType.CHAT: "gpt-3.5-turbo",  # Chat com cliente usa GPT-3.5 Turbo
            TaskType.PRESCRIPTION_ANALYSIS: "gpt-4o"  # Análise de atestado usa GPT-4o
        }
        
        # Definir instruções específicas para cada tipo de tarefa
        self.task_instructions = {
            TaskType.CHAT: CHAT_INSTRUCTIONS,
            TaskType.PRESCRIPTION_ANALYSIS: PRESCRIPTION_ANALYSIS_INSTRUCTIONS
        }
        
        print("ModelRouter inicializado com mapeamento de tarefas para modelos:")
        for task, model in self.task_model_mapping.items():
            print(f"- {task.value}: {model}")
    
    @property
    def openai_agent(self):
        """Inicializa o agente OpenAI sob demanda."""
        if self._openai_agent is None:
            self._openai_agent = OpenAIAgent()
        return self._openai_agent
    
    @property
    def gemini_agent(self):
        """Inicializa o agente Gemini sob demanda."""
        if self._gemini_agent is None:
            self._gemini_agent = GeminiAgent()
        return self._gemini_agent
    
    def route_request(self, task_type, *args, **kwargs):
        """
        Roteia a solicitação para o modelo mais adequado com base no tipo de tarefa.
        
        Args:
            task_type (TaskType): Tipo de tarefa a ser executada
            *args, **kwargs: Argumentos a serem passados para o método do agente
            
        Returns:
            Resultado da execução do método no agente selecionado
        """
        if task_type == TaskType.CHAT:
            # Para chat com cliente, usar GPT-3.5 Turbo
            return self._handle_chat_request(*args, **kwargs)
        
        elif task_type == TaskType.PRESCRIPTION_ANALYSIS:
            # Para análise de atestado/receita, usar GPT-4o
            return self._handle_prescription_analysis(*args, **kwargs)
        
        else:
            raise ValueError(f"Tipo de tarefa não suportado: {task_type}")
    
    def _handle_chat_request(self, query, prescription_context=None):
        """
        Processa solicitações de chat usando o modelo GPT-3.5 Turbo.
        
        Args:
            query (str): Pergunta do usuário
            prescription_context (dict): Contexto da prescrição atual
            
        Returns:
            str: Resposta do agente
        """
        print(f"Roteando solicitação de chat para modelo: {self.task_model_mapping[TaskType.CHAT]}")
        
        # Obter as instruções específicas para chat
        chat_instructions = self.task_instructions[TaskType.CHAT]
        
        # Usar o agente OpenAI com modelo GPT-3.5 Turbo para chat
        # Substituir o system prompt padrão pelo personalizado
        return self.openai_agent.get_response(
            query, 
            prescription_context,
            system_prompt=chat_instructions
        )
    
    def _handle_prescription_analysis(self, ocr_text):
        """
        Processa análise de atestado/receita usando o modelo GPT-4o.
        
        Args:
            ocr_text (str): Texto extraído da receita médica
            
        Returns:
            dict: Dicionário com as informações estruturadas da receita
        """
        print(f"Roteando análise de receita para modelo: {self.task_model_mapping[TaskType.PRESCRIPTION_ANALYSIS]}")
        
        # Obter as instruções específicas para análise de prescrição
        prescription_instructions = self.task_instructions[TaskType.PRESCRIPTION_ANALYSIS]
        
        # Verificar se o modelo configurado é GPT-4o
        if self.task_model_mapping[TaskType.PRESCRIPTION_ANALYSIS] == "gpt-4o":
            # Temporariamente alterar o modelo do agente OpenAI para GPT-4o
            original_model = self.openai_agent.model
            self.openai_agent.model = "gpt-4o"
            
            try:
                # Usar o agente OpenAI com modelo GPT-4o para análise de receita
                # Passar as instruções específicas para análise de prescrição
                result = self.openai_agent.interpret_prescription(
                    ocr_text,
                    system_prompt=prescription_instructions
                )
            finally:
                # Restaurar o modelo original
                self.openai_agent.model = original_model
            
            return result
        else:
            # Caso o mapeamento seja alterado para usar Gemini no futuro
            return self.gemini_agent.interpret_prescription(ocr_text)