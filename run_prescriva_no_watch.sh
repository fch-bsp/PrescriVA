#!/bin/bash

# Script para executar a aplicação PrescriVA sem o sistema de watch do Streamlit

# Cores para saída
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Iniciando PrescriVA - Assistente Virtual para Interpretação de Receitas Médicas${NC}"

# Verificar se o Tesseract OCR está instalado
if ! command -v tesseract &> /dev/null; then
    echo -e "${RED}Tesseract OCR não encontrado. Instalando...${NC}"
    sudo apt-get update
    sudo apt-get install -y tesseract-ocr tesseract-ocr-por
    
    # Verificar se a instalação foi bem-sucedida
    if ! command -v tesseract &> /dev/null; then
        echo -e "${RED}Falha ao instalar Tesseract OCR. Por favor, instale manualmente:${NC}"
        echo -e "sudo apt-get install tesseract-ocr tesseract-ocr-por"
        exit 1
    fi
else
    echo -e "${GREEN}Tesseract OCR já está instalado.${NC}"
fi

# Verificar se o ambiente virtual existe, se não, criar
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Criando ambiente virtual...${NC}"
    python3 -m venv venv
fi

# Ativar ambiente virtual
echo -e "${YELLOW}Ativando ambiente virtual...${NC}"
source venv/bin/activate

# Instalar dependências
echo -e "${YELLOW}Instalando dependências...${NC}"
pip install -r requirements.txt

# Inicializar banco de dados se não existir
if [ ! -f "data/prescriva.db" ]; then
    echo -e "${YELLOW}Inicializando banco de dados...${NC}"
    python init_database.py
fi

# Executar a aplicação sem o sistema de watch
echo -e "${GREEN}Iniciando aplicação Streamlit sem o sistema de watch...${NC}"
streamlit run app.py --server.fileWatcherType none

# Desativar ambiente virtual ao sair
deactivate