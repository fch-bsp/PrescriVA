import streamlit as st
from backend.ocr import process_image
from backend.pdf_generator import generate_pdf
from backend.s3_uploader import upload_to_s3
from backend.model_router import ModelRouter, TaskType
import os
import tempfile
import base64

# Configuração da página
st.set_page_config(
    page_title="PrescriVA - Assistente Virtual de Prescrições",
    page_icon="💊",
    layout="wide"
)

# Inicialização do roteador de modelos
model_router = ModelRouter()

# Função para carregar CSS personalizado
def local_css():
    st.markdown("""
    <style>
        .main {
            background-color: #f8f9fa;
        }
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1, h2, h3 {
            color: #2c3e50;
        }
        .prescription-box {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .chat-message {
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        .user-message {
            background-color: #e3f2fd;
            text-align: right;
        }
        .bot-message {
            background-color: #f1f1f1;
        }
        .footer-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 20px;
        }
        .logo-container {
            text-align: right;
        }
        .logo-container img {
            max-height: 50px;
        }
        .model-info {
            font-size: 0.8em;
            color: #666;
            margin-top: 5px;
        }
        footer {
            visibility: hidden;
        }
        footer:after {
            content: "Desenvolvido por | Fernando Horas";
            visibility: visible;
            display: block;
            position: relative;
            padding: 5px;
            top: 2px;
        }
    </style>
    """, unsafe_allow_html=True)

local_css()

# Título e descrição
st.title("PrescriVA")
st.subheader("Assistente Virtual para Interpretação de Receitas Médicas")

# Inicialização de variáveis de sessão
if 'prescription_data' not in st.session_state:
    st.session_state.prescription_data = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'pdf_path' not in st.session_state:
    st.session_state.pdf_path = None
if 's3_url' not in st.session_state:
    st.session_state.s3_url = None

# Detectar novo upload de arquivo
if 'previous_file' not in st.session_state:
    st.session_state.previous_file = None

# Layout principal com duas colunas
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("### Upload da Receita Médica")
    uploaded_file = st.file_uploader("Faça upload da imagem da sua receita médica", type=["jpg", "jpeg", "png"])
    
    # Verificar se um novo arquivo foi carregado
    if uploaded_file is not None and uploaded_file != st.session_state.previous_file:
        st.session_state.previous_file = uploaded_file
        # Limpar histórico de chat quando um novo arquivo é carregado
        st.session_state.chat_history = []
        st.session_state.prescription_data = None
        st.session_state.pdf_path = None
        st.session_state.s3_url = None
    
    if uploaded_file is not None:
        # Exibir imagem carregada
        st.image(uploaded_file, caption="Receita carregada", use_column_width=True)
        
        # Botão para processar a imagem
        if st.button("Interpretar Receita"):
            with st.spinner("Processando a receita com GPT-4o (Farmacêutico Analisador de Atestados)..."):
                # Salvar o arquivo temporariamente
                temp_file = tempfile.NamedTemporaryFile(delete=False)
                temp_file.write(uploaded_file.getvalue())
                temp_file.close()
                
                # Processar a imagem com OCR e o modelo GPT-4o através do roteador
                prescription_data = process_image(temp_file.name, model_router, TaskType.PRESCRIPTION_ANALYSIS)
                st.session_state.prescription_data = prescription_data
                
                # Remover o arquivo temporário
                os.unlink(temp_file.name)
    
    # Exibir os dados da prescrição se disponíveis
    if st.session_state.prescription_data:
        st.markdown("### Informações da Receita")
        with st.container():
            st.markdown('<div class="prescription-box">', unsafe_allow_html=True)
            
            data = st.session_state.prescription_data
            st.markdown(f"**Médico:** {data.get('medico', 'Não identificado')}")
            st.markdown(f"**Paciente:** {data.get('paciente', 'Não identificado')}")
            st.markdown(f"**Data:** {data.get('data', 'Não identificada')}")
            
            st.markdown("#### Medicamentos:")
            for med in data.get('medicamentos', []):
                st.markdown(f"""
                - **Nome:** {med.get('nome', 'Não identificado')}
                - **Dosagem:** {med.get('dosagem', 'Não identificada')}
                - **Posologia:** {med.get('posologia', 'Não identificada')}
                - **Duração:** {med.get('duracao', 'Não identificada')}
                """)
            
            st.markdown(f"**Observações:** {data.get('observacoes', 'Nenhuma')}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Botões para gerar PDF e salvar no S3
            col_pdf, col_s3 = st.columns(2)
            with col_pdf:
                if st.button("Gerar PDF"):
                    with st.spinner("Gerando PDF..."):
                        pdf_path = generate_pdf(st.session_state.prescription_data)
                        st.session_state.pdf_path = pdf_path
                        st.success("PDF gerado com sucesso!")
                        with open(pdf_path, "rb") as file:
                            st.download_button(
                                label="Baixar PDF",
                                data=file,
                                file_name="receita_medica.pdf",
                                mime="application/pdf"
                            )
            
            with col_s3:
                if st.session_state.pdf_path and st.button("Salvar na Nuvem"):
                    with st.spinner("Enviando para o S3 usando perfil bardhock..."):
                        s3_url = upload_to_s3(st.session_state.pdf_path)
                        st.session_state.s3_url = s3_url
                        st.success(f"Arquivo salvo na nuvem!")
                        st.markdown(f"[Acessar arquivo]({s3_url})")

with col2:
    st.markdown("### Assistente Farmacêutico")
    st.markdown("Converse com nosso assistente virtual para tirar dúvidas sobre sua medicação.")
    
    # Exibir histórico de chat
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f'<div class="chat-message user-message">👤 {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message bot-message">👨‍⚕️ {message["content"]}</div>', unsafe_allow_html=True)
    
    # Função para processar o envio da pergunta
    def process_query():
        query = st.session_state.query
        if query:
            # Adicionar mensagem do usuário ao histórico
            st.session_state.chat_history.append({"role": "user", "content": query})
            
            # Obter resposta do agente através do roteador
            with st.spinner("Consultando o assistente com GPT-3.5 Turbo (Farmacêutico para Atendimento ao Cliente)..."):
                prescription_context = st.session_state.prescription_data if st.session_state.prescription_data else {}
                response = model_router.route_request(TaskType.CHAT, query, prescription_context)
                
                # Adicionar resposta do agente ao histórico
                st.session_state.chat_history.append({"role": "assistant", "content": response})
            
            # Limpar o campo de entrada
            st.session_state.query = ""
    
    # Campo de entrada para o chat com callback
    st.text_input("Digite sua pergunta:", key="query", on_change=process_query)
    
    # Exibir informações sobre o modelo com descrição das funções
    st.markdown(f"""<div class='model-info'>
        <b>Chat:</b> GPT-3.5 Turbo (Farmacêutico para Atendimento ao Cliente) | 
        <b>Análise de Receitas:</b> GPT-4o (Farmacêutico Analisador de Atestados) | 
        Powered by OpenAI
    </div>""", unsafe_allow_html=True)

# Rodapé
st.markdown("---")

# Container para o rodapé com logo e texto
footer_col1, footer_col2 = st.columns([3, 1])
with footer_col1:
    st.markdown("PrescriVA - Democratizando o entendimento de prescrições médicas com apoio de IA")
with footer_col2:
    # Logo BSP Cloud
    logo_path = "assets/bspcloud_logo.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width=150)