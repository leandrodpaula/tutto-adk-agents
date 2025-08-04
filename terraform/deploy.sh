#!/bin/bash

# Script de deploy para infraestrutura ADK Agents no Google Cloud
# Uso: ./deploy.sh [ambiente] [ação]
#   ambiente: dev, staging, prod (padrão: dev)
#   ação: plan, apply, destroy (padrão: plan)

set -e

ENVIRONMENT=${1:-dev}
ACTION=${2:-plan}
PROJECT_ID=""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 ADK Agents Infrastructure Deploy${NC}"
echo "======================================"

# Verificar se estamos no diretório correto
if [ ! -f "main.tf" ]; then
    echo -e "${RED}❌ Erro: Execute este script do diretório terraform/${NC}"
    exit 1
fi

# Verificar se terraform está instalado
if ! command -v terraform &> /dev/null; then
    echo -e "${RED}❌ Terraform não encontrado. Instale o Terraform primeiro.${NC}"
    exit 1
fi

# Verificar se gcloud está instalado e autenticado
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Google Cloud SDK não encontrado. Instale o gcloud primeiro.${NC}"
    exit 1
fi

# Verificar autenticação
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n1 > /dev/null; then
    echo -e "${YELLOW}⚠️ Não autenticado no Google Cloud${NC}"
    echo "Execute: gcloud auth login && gcloud auth application-default login"
    exit 1
fi

echo -e "${GREEN}✅ Pré-requisitos verificados${NC}"
echo ""

# Verificar arquivo terraform.tfvars
if [ ! -f "terraform.tfvars" ]; then
    echo -e "${YELLOW}⚠️ Arquivo terraform.tfvars não encontrado${NC}"
    echo "Criando a partir do exemplo..."
    cp terraform.tfvars.example terraform.tfvars
    echo ""
    echo -e "${YELLOW}📝 Por favor, edite terraform.tfvars com suas configurações:${NC}"
    echo "   - project_id: Seu Project ID do Google Cloud"
    echo "   - Outras configurações conforme necessário"
    echo ""
    read -p "Pressione Enter após editar terraform.tfvars..."
fi

# Extrair PROJECT_ID do terraform.tfvars
PROJECT_ID=$(grep -E '^project_id\s*=' terraform.tfvars | sed 's/.*=\s*"\([^"]*\)".*/\1/' | tr -d ' ')

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ PROJECT_ID não encontrado em terraform.tfvars${NC}"
    exit 1
fi

echo -e "${BLUE}📋 Configuração:${NC}"
echo "   Environment: $ENVIRONMENT"
echo "   Action: $ACTION"
echo "   Project ID: $PROJECT_ID"
echo ""

# Definir projeto ativo
echo -e "${BLUE}⚙️ Configurando projeto ativo...${NC}"
gcloud config set project $PROJECT_ID

# Verificar se o projeto existe
if ! gcloud projects describe $PROJECT_ID > /dev/null 2>&1; then
    echo -e "${RED}❌ Projeto $PROJECT_ID não encontrado ou sem acesso${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Projeto $PROJECT_ID ativo${NC}"
echo ""

# Inicializar Terraform se necessário
if [ ! -d ".terraform" ]; then
    echo -e "${BLUE}🔧 Inicializando Terraform...${NC}"
    terraform init
    echo ""
fi

# Executar ação solicitada
case $ACTION in
    "plan")
        echo -e "${BLUE}📋 Executando terraform plan...${NC}"
        terraform plan -var="environment=$ENVIRONMENT"
        ;;
    "apply")
        echo -e "${BLUE}🚀 Executando terraform apply...${NC}"
        terraform plan -var="environment=$ENVIRONMENT"
        echo ""
        echo -e "${YELLOW}⚠️ Isso criará recursos no Google Cloud que podem gerar custos.${NC}"
        read -p "Continuar? (y/N): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            terraform apply -var="environment=$ENVIRONMENT"
            
            if [ $? -eq 0 ]; then
                echo ""
                echo -e "${GREEN}🎉 Deploy concluído com sucesso!${NC}"
                echo ""
                echo -e "${BLUE}📋 Próximos passos:${NC}"
                terraform output next_steps
            fi
        else
            echo "Deploy cancelado."
        fi
        ;;
    "destroy")
        echo -e "${RED}🗑️ Executando terraform destroy...${NC}"
        echo ""
        echo -e "${RED}⚠️ ATENÇÃO: Isso removerá PERMANENTEMENTE todos os recursos!${NC}"
        read -p "Tem CERTEZA que deseja destruir tudo? (y/N): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            terraform destroy -var="environment=$ENVIRONMENT"
            
            if [ $? -eq 0 ]; then
                echo ""
                echo -e "${GREEN}✅ Recursos removidos com sucesso${NC}"
            fi
        else
            echo "Destroy cancelado."
        fi
        ;;
    *)
        echo -e "${RED}❌ Ação inválida: $ACTION${NC}"
        echo "Ações válidas: plan, apply, destroy"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}✨ Script concluído!${NC}"
