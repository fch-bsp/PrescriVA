# PrescriVA

<div align="center">
  <h3>Assistente Virtual Inteligente para Interpretação de Receitas Médicas</h3>
  <p>Democratizando o acesso à informação médica com Inteligência Artificial</p>
</div>

## 🌟 Visão Geral

![Image](https://github.com/user-attachments/assets/6cef3aa4-6f64-453d-adbd-7ca8714b8d00)
O PrescriVA é uma solução inovadora que utiliza inteligência artificial para interpretar receitas médicas, tornando as informações mais acessíveis e compreensíveis para os pacientes. A plataforma combina tecnologias de OCR (Reconhecimento Óptico de Caracteres) e processamento de linguagem natural para extrair, estruturar e explicar prescrições médicas de forma clara e objetiva.

## 🚀 Principais Funcionalidades

### Interpretação de Receitas
- **Reconhecimento Avançado**: Processamento de imagens de receitas médicas escritas à mão ou digitadas
- **Extração Inteligente**: Identificação precisa de médico, paciente, data, medicamentos e instruções
- **Estruturação de Dados**: Organização clara das informações extraídas em formato padronizado

### Assistente Farmacêutico Virtual
- **Chat Interativo**: Interface conversacional para tirar dúvidas sobre medicamentos
- **Base de Conhecimento**: Informações detalhadas sobre mais de 20 medicamentos comuns
- **Orientações Personalizadas**: Respostas contextualizadas com base na receita do paciente

### Documentação e Armazenamento
- **Geração de PDF**: Criação automática de documentos com layout profissional e acessível
- **Armazenamento em Nuvem**: Integração com AWS S3 para salvar documentos com segurança
- **Download Local**: Opção para baixar o PDF gerado diretamente no dispositivo

## 💻 Tecnologias Utilizadas

- **Backend**: Python, OpenAI API, SQLite
- **Frontend**: Streamlit
- **Processamento de Imagem**: OpenCV, Tesseract OCR
- **Geração de PDF**: ReportLab
- **Armazenamento**: AWS S3

## ⚙️ Requisitos

- Python 3.8+
- Tesseract OCR
- Chave de API OpenAI
- Credenciais AWS (opcional, para funcionalidade de armazenamento em nuvem)

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/prescriva.git
cd prescriva
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Instale o Tesseract OCR:
   - Ubuntu/Debian: `sudo apt-get install tesseract-ocr tesseract-ocr-por`
   - macOS: `brew install tesseract tesseract-lang`
   - Windows: Baixe o instalador em https://github.com/UB-Mannheim/tesseract/wiki

4. Configure o arquivo `.env` com suas credenciais:
```
OPENAI_API_KEY="sua-chave-api-aqui"
AWS_ACCESS_KEY_ID="sua-access-key"
AWS_SECRET_ACCESS_KEY="sua-secret-key"
AWS_REGION="sua-regiao"
S3_BUCKET="seu-bucket"
profile="seu-perfil-aws"
```

5. Inicialize o banco de dados:
```bash
python init_database.py
```

## 🚀 Execução

Execute o script de inicialização:
```bash
./run_prescriva.sh
```

Ou inicie manualmente:
```bash
streamlit run app.py
```

Acesse a interface web no navegador: http://localhost:8501

## 🔒 Segurança e Privacidade

- Processamento local de imagens
- Não armazena dados sensíveis de pacientes
- Comunicação segura com APIs externas
- Opção de armazenamento em nuvem com criptografia

## 👥 Impacto Social

O PrescriVA foi desenvolvido com foco em acessibilidade e inclusão, beneficiando especialmente:

- Pessoas idosas com dificuldade para ler receitas manuscritas
- Pacientes com deficiência visual parcial
- Cuidadores e familiares responsáveis pela administração de medicamentos
- Comunidades com acesso limitado a orientação farmacêutica

## 📄 Licença

Este projeto está licenciado sob a licença MIT.

---

<div align="center">
  <p>Desenvolvido por Fernando Horas</p>
</div>
