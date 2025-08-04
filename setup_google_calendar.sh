#!/bin/bash

# Script helper para configurar Google Calendar
# Uso: ./setup_google_calendar.sh

echo "📅 Setup do Google Calendar para ADK Agents"
echo "==========================================="

# Verificar se pasta credentials existe
if [ ! -d "credentials" ]; then
    echo "📁 Criando pasta credentials..."
    mkdir -p credentials
    echo "credentials/*.json" >> .gitignore
    echo "credentials/*.key" >> .gitignore
fi

echo ""
echo "🔧 Escolha o método de autenticação:"
echo "1) Service Account (Recomendado para produção)"
echo "2) OAuth2 (Para desenvolvimento)"
echo "3) Manter Mock (Desenvolvimento sem API)"
echo ""

read -p "Escolha (1-3): " choice

case $choice in
    1)
        echo ""
        echo "🔐 Configurando Service Account..."
        echo ""
        echo "📋 Passos necessários:"
        echo "1. Acesse: https://console.cloud.google.com/"
        echo "2. Crie/selecione um projeto"
        echo "3. Ative a Google Calendar API"
        echo "4. Crie um Service Account"
        echo "5. Baixe o arquivo JSON"
        echo "6. Salve como: credentials/service-account.json"
        echo ""
        echo "📖 Guia completo: GOOGLE_CALENDAR_SETUP.md"
        echo ""
        
        read -p "Pressione Enter quando tiver o arquivo service-account.json..."
        
        if [ -f "credentials/service-account.json" ]; then
            echo "✅ Arquivo encontrado!"
            
            # Extrair email do service account
            SERVICE_EMAIL=$(cat credentials/service-account.json | grep -o '"client_email": "[^"]*' | cut -d'"' -f4)
            echo ""
            echo "📧 Email do Service Account: $SERVICE_EMAIL"
            echo ""
            echo "⚠️  IMPORTANTE: Compartilhe seu calendário com este email!"
            echo "   📅 Google Calendar → Configurações → Compartilhar com pessoas específicas"
            echo "   ✉️  Adicione: $SERVICE_EMAIL"
            echo "   🔐 Permissão: 'Fazer alterações em eventos'"
            echo ""
            
            # Configurar .env
            if grep -q "GOOGLE_SERVICE_ACCOUNT_FILE" .env; then
                sed -i 's|GOOGLE_SERVICE_ACCOUNT_FILE=.*|GOOGLE_SERVICE_ACCOUNT_FILE=./credentials/service-account.json|' .env
            else
                echo "GOOGLE_SERVICE_ACCOUNT_FILE=./credentials/service-account.json" >> .env
            fi
            
            echo "✅ Configuração Service Account completa!"
        else
            echo "❌ Arquivo credentials/service-account.json não encontrado"
            echo "💡 Siga o guia em GOOGLE_CALENDAR_SETUP.md"
        fi
        ;;
        
    2)
        echo ""
        echo "🔐 Configurando OAuth2..."
        echo ""
        echo "📋 Passos necessários:"
        echo "1. Acesse: https://console.cloud.google.com/"
        echo "2. Vá para Credentials"
        echo "3. Create Credentials → OAuth 2.0 Client IDs"
        echo "4. Application type: Desktop application"
        echo "5. Baixe o arquivo client_secrets.json"
        echo "6. Salve como: credentials/client_secrets.json"
        echo ""
        
        read -p "Pressione Enter quando tiver o arquivo client_secrets.json..."
        
        if [ -f "credentials/client_secrets.json" ]; then
            echo "✅ Arquivo encontrado!"
            
            # Configurar .env
            if grep -q "GOOGLE_CLIENT_SECRETS_FILE" .env; then
                sed -i 's|GOOGLE_CLIENT_SECRETS_FILE=.*|GOOGLE_CLIENT_SECRETS_FILE=./credentials/client_secrets.json|' .env
            else
                echo "GOOGLE_CLIENT_SECRETS_FILE=./credentials/client_secrets.json" >> .env
            fi
            
            echo "✅ Configuração OAuth2 completa!"
        else
            echo "❌ Arquivo credentials/client_secrets.json não encontrado"
        fi
        ;;
        
    3)
        echo ""
        echo "🎭 Mantendo configuração Mock..."
        echo "✅ Perfeito para desenvolvimento!"
        ;;
        
    *)
        echo "❌ Opção inválida"
        exit 1
        ;;
esac

echo ""
echo "🧪 Testando configuração..."
python validate_config.py

echo ""
echo "🎉 Setup concluído!"
echo ""
echo "💡 Próximos passos:"
echo "   1. Execute: ./run_example.sh"
echo "   2. Consulte: GOOGLE_CALENDAR_SETUP.md para troubleshooting"
echo "   3. Configure outras credenciais no .env se necessário"
