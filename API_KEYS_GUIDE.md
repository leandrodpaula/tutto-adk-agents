# 🔑 Guia para Obter Chaves de API dos Provedores LLM

## 📋 Resumo Rápido

| Provedor | Site para Chave | Formato da Chave | Custo Aproximado |
|----------|-----------------|------------------|------------------|
| **OpenAI** | [platform.openai.com](https://platform.openai.com/api-keys) | `sk-...` | $0.002/1K tokens |
| **Google Gemini** | [makersuite.google.com](https://makersuite.google.com/app/apikey) | `AIza...` | Grátis até limite |
| **Groq** | [console.groq.com](https://console.groq.com/keys) | `gsk_...` | Grátis até limite |

---

## 🟢 OpenAI (Recomendado para Qualidade)

### 1. Criar Conta
- Acesse: https://platform.openai.com/
- Clique em "Sign Up" se não tiver conta
- Faça login na sua conta existente

### 2. Obter Chave da API
- Vá para: https://platform.openai.com/api-keys
- Clique em "Create new secret key"
- Dê um nome para a chave (ex: "Barbearia-ADK")
- **IMPORTANTE**: Copie e salve a chave imediatamente (não será mostrada novamente)

### 3. Configurar Cobrança
- Vá para: https://platform.openai.com/account/billing
- Adicione método de pagamento
- Configure limite de gastos para controle

### 4. Configurar no Sistema
```bash
# No arquivo .env
OPENAI_API_KEY=sk-proj-sua-chave-aqui-muito-longa
ADK_LLM_PROVIDER=openai
ADK_LLM_MODEL=gpt-3.5-turbo  # ou gpt-4
```

### 💰 Custos OpenAI
- **GPT-3.5-turbo**: $0.0015/1K tokens input, $0.002/1K tokens output
- **GPT-4**: $0.03/1K tokens input, $0.06/1K tokens output
- **GPT-4-turbo**: $0.01/1K tokens input, $0.03/1K tokens output

---

## 🔵 Google Gemini (Melhor Custo-Benefício)

### 1. Criar Conta Google
- Você precisa de uma conta Google ativa
- Acesse: https://makersuite.google.com/

### 2. Obter Chave da API
- Vá para: https://makersuite.google.com/app/apikey
- Clique em "Create API Key"
- Selecione um projeto do Google Cloud ou crie um novo
- Copie a chave gerada

### 3. Configurar no Sistema
```bash
# No arquivo .env
GOOGLE_API_KEY=AIzaSua-chave-google-aqui
ADK_LLM_PROVIDER=gemini
ADK_LLM_MODEL=gemini-pro  # ou gemini-1.5-pro
```

### 💰 Custos Gemini
- **Gemini Pro**: Grátis até 60 consultas/minuto
- **Gemini Pro Vision**: Grátis até 60 consultas/minuto
- Ótimo para desenvolvimento e testes

---

## ⚡ Groq (Melhor Velocidade)

### 1. Criar Conta
- Acesse: https://console.groq.com/
- Clique em "Sign Up" ou use conta Google/GitHub

### 2. Obter Chave da API
- Vá para: https://console.groq.com/keys
- Clique em "Create API Key"
- Dê um nome para a chave
- Copie a chave gerada

### 3. Configurar no Sistema
```bash
# No arquivo .env
GROQ_API_KEY=gsk_sua-chave-groq-aqui
ADK_LLM_PROVIDER=groq
ADK_LLM_MODEL=llama2-70b-4096  # ou mixtral-8x7b-32768
```

### 💰 Custos Groq
- **Llama2-70b**: Grátis até limite diário
- **Mixtral-8x7b**: Grátis até limite diário
- Excelente para prototipagem rápida

---

## 🚀 Configuração Rápida

### Passo 1: Copiar arquivo de exemplo
```bash
cd /home/leo/workspace/tutto-adk-agents
cp .env.example .env
```

### Passo 2: Editar arquivo .env
```bash
nano .env  # ou use seu editor preferido
```

### Passo 3: Escolher e configurar UM provedor

#### Para OpenAI:
```bash
OPENAI_API_KEY=sk-sua-chave-aqui
ADK_LLM_PROVIDER=openai
```

#### Para Gemini:
```bash
GOOGLE_API_KEY=AIza-sua-chave-aqui
ADK_LLM_PROVIDER=gemini
```

#### Para Groq:
```bash
GROQ_API_KEY=gsk_sua-chave-aqui
ADK_LLM_PROVIDER=groq
```

### Passo 4: Testar configuração
```bash
# Testar com provedor configurado
./run_example.sh

# Ou testar provedor específico
./run_example.sh openai   # se configurou OpenAI
./run_example.sh gemini   # se configurou Gemini
./run_example.sh groq     # se configurou Groq
```

---

## 🔒 Segurança das Chaves

### ✅ Boas Práticas
- **NUNCA** commite arquivos `.env` no Git
- Mantenha chaves em arquivo `.env` local
- Use permissões restritivas: `chmod 600 .env`
- Regenere chaves periodicamente
- Configure limites de gasto quando possível

### ❌ O que NÃO fazer
- Não cole chaves em código fonte
- Não compartilhe chaves em mensagens/emails
- Não use chaves em repositórios públicos
- Não deixe chaves em logs ou prints

### 🛡️ Configurar Limites
```bash
# OpenAI: Configure em platform.openai.com/account/billing
# Exemplo de limite mensal: $20

# Groq: Monitore uso em console.groq.com/usage
# Gemini: Configure quotas em Google Cloud Console
```

---

## 🧪 Testando Diferentes Provedores

### Script de Teste Rápido
```bash
# Testar OpenAI
export OPENAI_API_KEY="sk-..."
./run_example.sh openai

# Testar Gemini  
export GOOGLE_API_KEY="AIza..."
./run_example.sh gemini

# Testar Groq
export GROQ_API_KEY="gsk_..."
./run_example.sh groq
```

### Comparação de Performance
```bash
# Teste todos os provedores (se configurados)
for provider in openai gemini groq; do
    echo "=== Testando $provider ==="
    time ./run_example.sh $provider
    echo ""
done
```

---

## 📊 Recomendações por Uso

| Caso de Uso | Provedor Recomendado | Motivo |
|-------------|---------------------|---------|
| **Desenvolvimento** | Groq ou Gemini | Gratuito, rápido |
| **Produção** | OpenAI | Máxima qualidade |
| **Prototipagem** | Groq | Velocidade extrema |
| **Orçamento Limitado** | Gemini | Melhor custo-benefício |
| **Aplicação Crítica** | OpenAI GPT-4 | Confiabilidade máxima |

---

## 🆘 Troubleshooting

### Erro: "Invalid API Key"
```bash
# Verificar se a chave está correta
echo $OPENAI_API_KEY  # ou GOOGLE_API_KEY, GROQ_API_KEY

# Verificar formato da chave
# OpenAI: deve começar com 'sk-'
# Gemini: deve começar com 'AIza'
# Groq: deve começar com 'gsk_'
```

### Erro: "Quota Exceeded"
```bash
# Verificar uso nas respectivas consoles:
# OpenAI: https://platform.openai.com/usage
# Groq: https://console.groq.com/usage
# Gemini: Google Cloud Console
```

### Erro: "Rate Limit"
```bash
# Adicionar delay entre chamadas
# Configurar no .env:
ADK_REQUEST_DELAY=1000  # milliseconds
```

---

## 💡 Dicas Avançadas

### Rotação de Chaves
```bash
# Configurar múltiplas chaves (implementação futura)
OPENAI_API_KEY_1=sk-primary-key
OPENAI_API_KEY_2=sk-backup-key
```

### Monitoramento de Custos
```bash
# Adicionar ao .env para logs de custo
LOG_API_USAGE=true
COST_ALERT_THRESHOLD=10.00  # USD
```

### Cache de Respostas
```bash
# Ativar cache para economizar
ENABLE_LLM_CACHE=true
CACHE_TTL_HOURS=24
```
