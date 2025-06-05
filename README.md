# PrescriVA - Assistente Virtual para Interpretação de Receitas Médicas

PrescriVA é uma aplicação que utiliza inteligência artificial para interpretar receitas médicas e fornecer informações úteis aos pacientes sobre seus medicamentos.

## Arquitetura do Sistema

A aplicação utiliza um sistema de roteamento inteligente entre modelos de IA para otimizar o desempenho e a precisão:

```
[Usuário]
   |
   v
[App Frontend (Streamlit)]
   |
   v
[Backend com lógica de roteamento + Instruções específicas]
   ├──> GPT-3.5 Turbo (Chat com cliente) + Instruções de Farmacêutico para Atendimento
   └──> GPT-4o (Análise de atestado/receita) + Instruções de Farmacêutico Analisador
```

## Componentes Principais

- **Frontend**: Interface de usuário construída com Streamlit
- **Backend**:
  - **ModelRouter**: Direciona solicitações para o modelo mais adequado com base no tipo de tarefa
  - **OCR**: Extração de texto de imagens de receitas médicas
  - **Agentes de IA**: Interpretação de receitas e resposta a perguntas dos usuários
  - **Instruções Específicas**: Cada agente recebe instruções personalizadas para sua função

## Modelos de IA Utilizados

- **GPT-3.5 Turbo (Farmacêutico para Atendimento ao Cliente)**: Utilizado para chat com o cliente, oferecendo bom equilíbrio entre desempenho e custo. Especializado em responder dúvidas sobre medicamentos com linguagem acessível e educativa.
- **GPT-4o (Farmacêutico Analisador de Atestados)**: Utilizado para análise de atestados e receitas médicas, onde maior precisão é necessária. Especializado em extrair informações detalhadas de receitas com atenção técnica e criteriosa.

## Funcionalidades

- Upload de imagens de receitas médicas
- Extração e interpretação automática das informações da receita
- Chat com assistente virtual para tirar dúvidas sobre medicamentos
- Geração de PDF com informações estruturadas da receita
- Armazenamento de documentos na nuvem (AWS S3)

## Requisitos

- Python 3.8+
- Tesseract OCR
- Chave de API da OpenAI
- Credenciais AWS (opcional, para armazenamento em S3)

## Instalação

1. Clone o repositório
2. Instale as dependências: `pip install -r requirements.txt`
3. Instale o Tesseract OCR:
   - Ubuntu/Debian: `sudo apt-get install tesseract-ocr tesseract-ocr-por`
   - macOS: `brew install tesseract tesseract-lang`
   - Windows: Baixe o instalador em https://github.com/UB-Mannheim/tesseract/wiki
4. Configure as variáveis de ambiente:
   - Crie um arquivo `.env` na raiz do projeto
   - Adicione sua chave da API OpenAI: `OPENAI_API_KEY=sua_chave_aqui`

## Execução

```bash
python app.py
```

Ou use o script de execução:

```bash
./run_prescriva.sh
```

## Estrutura do Projeto

```
App_PrescriVA/
├── assets/                # Recursos estáticos (imagens, logos)
├── backend/               # Lógica de backend
│   ├── __init__.py
│   ├── database.py        # Operações de banco de dados
│   ├── gemini_agent.py    # Agente Google Gemini (alternativo)
│   ├── model_router.py    # Roteador de modelos de IA
│   ├── model_instructions.py # Instruções específicas para cada modelo
│   ├── ocr.py             # Processamento de imagens e OCR
│   ├── openai_agent.py    # Agente OpenAI
│   ├── pdf_generator.py   # Geração de PDFs
│   └── s3_uploader.py     # Upload para AWS S3
├── data/                  # Dados e banco de dados
├── app.py                 # Aplicação principal
└── requirements.txt       # Dependências do projeto
```

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença

Este projeto está licenciado sob a licença MIT.