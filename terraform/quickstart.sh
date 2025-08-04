#!/bin/bash

# Quick Start para ADK Agents Terraform
# Este script guia você através do processo completo de deploy

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 ADK Agents - Quick Start${NC}"
echo "============================="
echo ""

# Verificar se estamos no diretório terraform
if [ ! -f "main.tf" ]; then
    echo -e "${RED}❌ Execute este script do diretório terraform/${NC}"
    exit 1
fi

echo -e "${BLUE}👋 Bem-vindo ao setup do ADK Agents!${NC}"
echo ""
echo "Este script irá:"
echo "1. 🔧 Verificar pré-requisitos"
echo "2. ⚙️ Configurar terraform.tfvars"
echo "3. 🚀 Fazer deploy da infraestrutura"
echo "4. 🧪 Testar a configuração"
echo ""

read -p "Continuar? (y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Setup cancelado."
    exit 0
fi

echo ""
echo -e "${BLUE}🔧 Passo 1: Verificando pré-requisitos...${NC}"

# Verificar terraform
if command -v terraform &> /dev/null; then
    echo -e "${GREEN}✅ Terraform instalado${NC}"
else
    echo -e "${RED}❌ Terraform não encontrado${NC}"
    echo "Instale o Terraform: https://learn.hashicorp.com/terraform/getting-started/install.html"
    exit 1
fi

# Verificar gcloud
if command -v gcloud &> /dev/null; then
    echo -e "${GREEN}✅ Google Cloud SDK instalado${NC}"
else
    echo -e "${RED}❌ Google Cloud SDK não encontrado${NC}"
    echo "Instale o gcloud: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Verificar autenticação
if gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n1 > /dev/null; then
    ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n1)
    echo -e "${GREEN}✅ Autenticado como: $ACTIVE_ACCOUNT${NC}"
else
    echo -e "${YELLOW}⚠️ Não autenticado no Google Cloud${NC}"
    echo "Executando autenticação..."
    gcloud auth login
    gcloud auth application-default login
fi

echo ""
echo -e "${BLUE}⚙️ Passo 2: Configuração${NC}"

# Configurar terraform.tfvars
if [ ! -f "terraform.tfvars" ]; then
    echo "Criando terraform.tfvars..."
    cp terraform.tfvars.example terraform.tfvars
fi

echo ""
echo -e "${YELLOW}📝 Configuração necessária:${NC}"
echo ""

# Solicitar Project ID
echo -n "🏗️ Google Cloud Project ID: "
read PROJECT_ID

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ Project ID é obrigatório${NC}"
    exit 1
fi

# Atualizar terraform.tfvars
sed -i "s/your-gcp-project-id/$PROJECT_ID/" terraform.tfvars

# Perguntar sobre outras configurações
echo ""
echo -n "🌎 Região (padrão: us-central1): "
read REGION
REGION=${REGION:-us-central1}
sed -i "s/us-central1/$REGION/" terraform.tfvars

echo ""
echo -n "🏪 Nome da barbearia (padrão: Barbearia ADK): "
read BARBERSHOP_NAME
if [ -n "$BARBERSHOP_NAME" ]; then
    sed -i "s/Barbearia ADK/$BARBERSHOP_NAME/" terraform.tfvars
fi

echo ""
echo -n "📞 Telefone da barbearia (padrão: +5511999999999): "
read BARBERSHOP_PHONE
if [ -n "$BARBERSHOP_PHONE" ]; then
    sed -i "s/+5511999999999/$BARBERSHOP_PHONE/" terraform.tfvars
fi

echo ""
echo -e "${BLUE}🔑 Configuração de API Keys${NC}"
echo "Você pode configurar agora ou depois via Secret Manager:"
echo ""

echo -n "🧠 Chave do Gemini (opcional): "
read -s GEMINI_KEY
echo ""
if [ -n "$GEMINI_KEY" ]; then
    sed -i "s/gemini_api_key = \"\"/gemini_api_key = \"$GEMINI_KEY\"/" terraform.tfvars
fi

echo ""
echo -e "${GREEN}✅ Configuração salva em terraform.tfvars${NC}"

echo ""
echo -e "${BLUE}🚀 Passo 3: Deploy da infraestrutura${NC}"
echo ""

# Configurar projeto ativo
gcloud config set project $PROJECT_ID

# Verificar se projeto existe
if ! gcloud projects describe $PROJECT_ID > /dev/null 2>&1; then
    echo -e "${RED}❌ Projeto $PROJECT_ID não encontrado ou sem acesso${NC}"
    exit 1
fi

# Inicializar terraform
if [ ! -d ".terraform" ]; then
    echo "Inicializando Terraform..."
    terraform init
fi

# Mostrar plano
echo -e "${BLUE}📋 Revisando o que será criado...${NC}"
terraform plan

echo ""
echo -e "${YELLOW}⚠️ O deploy criará recursos no Google Cloud que podem gerar custos mínimos.${NC}"
read -p "Continuar com o deploy? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}🚀 Executando deploy...${NC}"
    terraform apply -auto-approve
    
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}🎉 Deploy concluído com sucesso!${NC}"
        
        # Obter informações importantes
        SA_EMAIL=$(terraform output -raw service_account_email)
        
        echo ""
        echo -e "${BLUE}🧪 Passo 4: Teste da infraestrutura${NC}"
        ./test_infrastructure.sh $PROJECT_ID
        
        echo ""
        echo -e "${BLUE}📋 Informações importantes:${NC}"
        echo -e "${YELLOW}📧 Service Account Email:${NC} $SA_EMAIL"
        echo ""
        echo -e "${RED}⚠️ AÇÃO MANUAL REQUERIDA:${NC}"
        echo "1. Abra https://calendar.google.com/"
        echo "2. Vá em Configurações do seu calendário"
        echo "3. Compartilhar com pessoas específicas"
        echo "4. Adicione: $SA_EMAIL"
        echo "5. Permissão: 'Make changes to events'"
        echo ""
        
        terraform output next_steps
        
        echo ""
        echo -e "${GREEN}✅ Setup completo!${NC}"
        echo ""
        echo -e "${BLUE}📖 Próximos passos:${NC}"
        echo "1. 📧 Compartilhar Google Calendar (OBRIGATÓRIO)"
        echo "2. 🔑 Adicionar chaves de API se necessário"
        echo "3. 🚀 Deploy da aplicação ADK Agents"
        echo "4. 📋 Consultar /terraform/README.md para detalhes"
        
    else
        echo -e "${RED}❌ Erro no deploy${NC}"
        exit 1
    fi
else
    echo "Deploy cancelado."
fi

echo ""
echo -e "${BLUE}✨ Quick Start concluído!${NC}"
