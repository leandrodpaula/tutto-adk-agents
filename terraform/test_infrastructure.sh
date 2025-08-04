#!/bin/bash

# Script para testar a infraestrutura ADK Agents após deploy
# Uso: ./test_infrastructure.sh [project_id]

set -e

PROJECT_ID=${1:-""}
if [ -z "$PROJECT_ID" ]; then
    # Tentar extrair do terraform.tfvars
    if [ -f "terraform.tfvars" ]; then
        PROJECT_ID=$(grep -E '^project_id\s*=' terraform.tfvars | sed 's/.*=\s*"\([^"]*\)".*/\1/' | tr -d ' ')
    fi
fi

if [ -z "$PROJECT_ID" ]; then
    echo "❌ PROJECT_ID necessário"
    echo "Uso: $0 [project_id]"
    exit 1
fi

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🧪 Testando Infraestrutura ADK Agents${NC}"
echo "======================================"
echo "Project ID: $PROJECT_ID"
echo ""

# Configurar projeto
gcloud config set project $PROJECT_ID

# Obter informações do terraform
SA_EMAIL=""
if [ -f ".terraform/terraform.tfstate" ] || [ -f "terraform.tfstate" ]; then
    SA_EMAIL=$(terraform output -raw service_account_email 2>/dev/null || echo "")
fi

echo -e "${BLUE}1. 📋 Verificando APIs habilitadas...${NC}"
REQUIRED_APIS=(
    "calendar-json.googleapis.com"
    "generativeai.googleapis.com"
    "secretmanager.googleapis.com"
    "iam.googleapis.com"
)

for api in "${REQUIRED_APIS[@]}"; do
    if gcloud services list --enabled --filter="name:$api" --format="value(name)" | grep -q $api; then
        echo -e "   ${GREEN}✅ $api${NC}"
    else
        echo -e "   ${RED}❌ $api${NC}"
    fi
done

echo ""

echo -e "${BLUE}2. 🔐 Verificando Service Account...${NC}"
if [ -n "$SA_EMAIL" ]; then
    if gcloud iam service-accounts describe $SA_EMAIL > /dev/null 2>&1; then
        echo -e "   ${GREEN}✅ Service Account existe: $SA_EMAIL${NC}"
        
        # Verificar permissões
        echo -e "${BLUE}   📝 Verificando permissões IAM...${NC}"
        ROLES=(
            "roles/calendar.editor"
            "roles/aiplatform.user"
            "roles/secretmanager.secretAccessor"
        )
        
        for role in "${ROLES[@]}"; do
            if gcloud projects get-iam-policy $PROJECT_ID --flatten="bindings[].members" --filter="bindings.role:$role AND bindings.members:serviceAccount:$SA_EMAIL" --format="value(bindings.role)" | grep -q $role; then
                echo -e "      ${GREEN}✅ $role${NC}"
            else
                echo -e "      ${RED}❌ $role${NC}"
            fi
        done
    else
        echo -e "   ${RED}❌ Service Account não encontrado: $SA_EMAIL${NC}"
    fi
else
    echo -e "   ${YELLOW}⚠️ Service Account email não encontrado no terraform output${NC}"
fi

echo ""

echo -e "${BLUE}3. 🔒 Verificando Secret Manager...${NC}"
SECRETS=$(gcloud secrets list --filter="name~adk-agents" --format="value(name)")
if [ -n "$SECRETS" ]; then
    echo "$SECRETS" | while read secret; do
        if [ -n "$secret" ]; then
            echo -e "   ${GREEN}✅ $secret${NC}"
            
            # Tentar acessar o secret
            if gcloud secrets versions access latest --secret="$secret" > /dev/null 2>&1; then
                echo -e "      ${GREEN}✓ Acessível${NC}"
            else
                echo -e "      ${YELLOW}⚠ Não acessível (permissões)${NC}"
            fi
        fi
    done
else
    echo -e "   ${RED}❌ Nenhum secret encontrado${NC}"
fi

echo ""

echo -e "${BLUE}4. 📅 Verificando acesso ao Google Calendar...${NC}"
if [ -n "$SA_EMAIL" ]; then
    echo -e "   ${YELLOW}⚠️ AÇÃO MANUAL REQUERIDA:${NC}"
    echo "   📧 Compartilhe seu Google Calendar com: $SA_EMAIL"
    echo "   🔐 Permissão necessária: 'Make changes to events'"
    echo "   📋 Como fazer:"
    echo "      1. Abra https://calendar.google.com/"
    echo "      2. Configurações do calendário"
    echo "      3. Compartilhar com pessoas específicas"
    echo "      4. Adicionar: $SA_EMAIL"
    echo "      5. Permissão: 'Make changes to events'"
else
    echo -e "   ${RED}❌ Service Account não identificado${NC}"
fi

echo ""

echo -e "${BLUE}5. 🔑 Verificando chaves de API...${NC}"
# Tentar acessar secrets de API keys
API_SECRETS=("gemini-key" "openai-key" "groq-key")
for secret_suffix in "${API_SECRETS[@]}"; do
    secret_name="adk-agents-dev-$secret_suffix"
    if gcloud secrets describe $secret_name > /dev/null 2>&1; then
        if gcloud secrets versions access latest --secret="$secret_name" > /dev/null 2>&1; then
            key_length=$(gcloud secrets versions access latest --secret="$secret_name" | wc -c)
            if [ $key_length -gt 10 ]; then
                echo -e "   ${GREEN}✅ $secret_suffix configurada${NC}"
            else
                echo -e "   ${YELLOW}⚠️ $secret_suffix vazia${NC}"
            fi
        else
            echo -e "   ${RED}❌ $secret_suffix não acessível${NC}"
        fi
    else
        echo -e "   ${YELLOW}⚪ $secret_suffix não criada${NC}"
    fi
done

echo ""

echo -e "${BLUE}6. 🚀 Teste de conectividade...${NC}"
if [ -n "$SA_EMAIL" ]; then
    # Criar um teste simples com a service account
    echo -e "   ${BLUE}📡 Testando autenticação...${NC}"
    
    # Baixar chave da service account temporariamente para teste
    temp_key="/tmp/sa_key_test.json"
    if terraform output -raw service_account_key 2>/dev/null | base64 -d > $temp_key 2>/dev/null; then
        export GOOGLE_APPLICATION_CREDENTIALS=$temp_key
        
        # Testar acesso às APIs
        if gcloud auth activate-service-account --key-file=$temp_key > /dev/null 2>&1; then
            echo -e "      ${GREEN}✅ Autenticação com Service Account OK${NC}"
            
            # Test Calendar API (lista de calendários)
            if gcloud calendar calendars list > /dev/null 2>&1; then
                echo -e "      ${GREEN}✅ Google Calendar API OK${NC}"
            else
                echo -e "      ${YELLOW}⚠️ Google Calendar API - verificar permissões${NC}"
            fi
        else
            echo -e "      ${RED}❌ Falha na autenticação${NC}"
        fi
        
        # Limpar arquivo temporário
        rm -f $temp_key
        unset GOOGLE_APPLICATION_CREDENTIALS
    else
        echo -e "      ${YELLOW}⚠️ Não foi possível obter chave para teste${NC}"
    fi
else
    echo -e "   ${RED}❌ Service Account não identificado${NC}"
fi

echo ""

echo -e "${BLUE}📊 Resumo do Teste${NC}"
echo "==================="

# Determinar status geral
if gcloud services list --enabled --filter="name:calendar-json.googleapis.com" --format="value(name)" | grep -q calendar && [ -n "$SA_EMAIL" ]; then
    echo -e "${GREEN}✅ Infraestrutura básica: OK${NC}"
else
    echo -e "${RED}❌ Infraestrutura básica: Problemas encontrados${NC}"
fi

if [ -n "$SA_EMAIL" ]; then
    echo -e "${YELLOW}⚠️ Ação manual pendente: Compartilhar calendário${NC}"
    echo -e "   📧 Email: $SA_EMAIL"
fi

echo ""
echo -e "${BLUE}💡 Próximos passos:${NC}"
echo "1. 📧 Compartilhar Google Calendar com Service Account"
echo "2. 🔑 Adicionar chaves de API nos secrets (se necessário)"
echo "3. 🚀 Deploy da aplicação ADK Agents"
echo "4. 🧪 Testar funcionalidades completas"

echo ""
echo -e "${GREEN}✨ Teste de infraestrutura concluído!${NC}"
