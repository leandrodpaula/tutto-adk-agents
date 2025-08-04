#!/bin/bash

# Script para executar o exemplo do Barbershop Scheduler Agent
# Uso: ./run_example.sh [provedor_llm]
#   provedor_llm: openai, gemini, groq ou mock (padrão: auto-detect do .env)

LLM_PROVIDER=${1:-""}

echo "🚀 Iniciando Barbershop Scheduler Agent..."

# Verificar se existe arquivo .env
if [ -f ".env" ]; then
    echo "📋 Carregando configurações do .env"
    # Não carregar aqui pois o Python fará isso
else
    echo "⚠️ Arquivo .env não encontrado"
    echo "💡 Dica: Copie .env.example para .env e configure suas chaves de API"
    echo "   cp .env.example .env"
    echo ""
fi

# Se provedor foi especificado, sobrescrever
if [ -n "$LLM_PROVIDER" ]; then
    export ADK_LLM_PROVIDER=$LLM_PROVIDER
    echo "🧠 Provedor LLM: $LLM_PROVIDER (via parâmetro)"
else
    # Tentar ler do .env ou usar auto-detect
    if [ -f ".env" ]; then
        PROVIDER_FROM_ENV=$(grep "^ADK_LLM_PROVIDER=" .env | cut -d'=' -f2 | tr -d '"' | tr -d "'")
        if [ -n "$PROVIDER_FROM_ENV" ]; then
            echo "🧠 Provedor LLM: $PROVIDER_FROM_ENV (do .env)"
        else
            echo "🧠 Provedor LLM: auto-detect (baseado nas chaves disponíveis)"
        fi
    else
        echo "🧠 Provedor LLM: mock (sem .env)"
    fi
fi

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual Python..."
    python3 -m venv venv
fi

# Ativar ambiente virtual e instalar dependências
echo "📦 Instalando dependências base..."
./venv/bin/pip install -q google-auth google-auth-oauthlib google-api-python-client

# Instalar dependências específicas do LLM se especificado
if [ -n "$LLM_PROVIDER" ] && [ "$LLM_PROVIDER" != "mock" ]; then
    echo "📦 Instalando dependências do LLM ($LLM_PROVIDER)..."
    case $LLM_PROVIDER in
        "openai")
            ./venv/bin/pip install -q openai
            echo "💡 Configure OPENAI_API_KEY no .env para usar OpenAI"
            ;;
        "gemini")
            ./venv/bin/pip install -q google-generativeai
            echo "💡 Configure GOOGLE_API_KEY no .env para usar Gemini"
            ;;
        "groq")
            ./venv/bin/pip install -q groq
            echo "💡 Configure GROQ_API_KEY no .env para usar Groq"
            ;;
        *)
            echo "⚠️ Provedor LLM não reconhecido: $LLM_PROVIDER. Usando mock."
            ;;
    esac
else
    echo "📦 Instalando todas as dependências LLM (para auto-detect)..."
    ./venv/bin/pip install -q openai google-generativeai groq 2>/dev/null || echo "   (algumas dependências podem ter falhado, mas o sistema funcionará)"
fi

echo ""

# Executar exemplo
echo "🏃 Executando exemplo..."
./venv/bin/python examples/barbershop_example.py

echo ""
echo "✨ Exemplo concluído!"
echo ""
echo "💡 Para configurar chaves de API reais:"
echo "   1. cp .env.example .env"
echo "   2. Edite .env com suas chaves"
echo "   3. Consulte API_KEYS_GUIDE.md para obter chaves"
