# Configuração de Provedores LLM

O sistema ADK suporta múltiplos provedores de LLM: **OpenAI**, **Google Gemini** e **Groq**.

## 🧠 Provedores Suportados

### OpenAI

**Modelos suportados:**
- `gpt-3.5-turbo` (padrão)
- `gpt-4`
- `gpt-4-turbo`
- `gpt-4o`

**Configuração:**
```bash
export OPENAI_API_KEY="sk-..."
```

**Usar no código:**
```python
agent = BarbershopSchedulerAgent(
    name="meu_agent",
    llm_provider="openai",
    llm_model="gpt-3.5-turbo"  # opcional
)
```

### Google Gemini

**Modelos suportados:**
- `gemini-pro` (padrão)
- `gemini-1.5-pro`
- `gemini-1.0-pro`

**Configuração:**
```bash
export GOOGLE_API_KEY="AIza..."
```

**Usar no código:**
```python
agent = BarbershopSchedulerAgent(
    name="meu_agent",
    llm_provider="gemini",
    llm_model="gemini-pro"  # opcional
)
```

### Groq

**Modelos suportados:**
- `llama2-70b-4096` (padrão)
- `mixtral-8x7b-32768`
- `gemma-7b-it`

**Configuração:**
```bash
export GROQ_API_KEY="gsk_..."
```

**Usar no código:**
```python
agent = BarbershopSchedulerAgent(
    name="meu_agent",
    llm_provider="groq",
    llm_model="llama2-70b-4096"  # opcional
)
```

## 🎭 Cliente Mock (Desenvolvimento)

Para desenvolvimento e testes sem custo:

```python
agent = BarbershopSchedulerAgent(
    name="meu_agent",
    use_mock_llm=True
)
```

## 🚀 Exemplos de Uso

### Script de Linha de Comando

```bash
# Usar OpenAI
export OPENAI_API_KEY="sk-..."
./run_example.sh openai

# Usar Gemini
export GOOGLE_API_KEY="AIza..."
./run_example.sh gemini

# Usar Groq
export GROQ_API_KEY="gsk_..."
./run_example.sh groq

# Usar Mock (sem chaves API)
./run_example.sh mock
```

### Código Python

```python
import asyncio
from agents.specialized.barbershop_scheduler_agent import BarbershopSchedulerAgent

async def exemplo_multi_llm():
    # Auto-detectar provedor baseado em variáveis de ambiente
    agent1 = BarbershopSchedulerAgent("agent_auto")
    
    # Forçar provedor específico
    agent2 = BarbershopSchedulerAgent(
        "agent_openai",
        llm_provider="openai",
        llm_model="gpt-4"
    )
    
    # Cliente mock para testes
    agent3 = BarbershopSchedulerAgent(
        "agent_mock",
        use_mock_llm=True
    )
    
    # Testar capacidades
    for agent in [agent1, agent2, agent3]:
        if agent.has_llm():
            info = agent.get_llm_info()
            print(f"{agent.name}: {info['provider']}/{info['model']}")
        else:
            print(f"{agent.name}: LLM não disponível")

asyncio.run(exemplo_multi_llm())
```

## ⚙️ Configuração Avançada

### Arquivo .env

Crie um arquivo `.env`:

```env
# Escolha um provedor
OPENAI_API_KEY=sk-your-openai-key
# GOOGLE_API_KEY=AIza-your-gemini-key  
# GROQ_API_KEY=gsk-your-groq-key

# Configurações opcionais
ADK_LLM_PROVIDER=openai
ADK_DEFAULT_MODEL=gpt-3.5-turbo
ADK_TEMPERATURE=0.7
ADK_MAX_TOKENS=1000
```

### Múltiplos Provedores

```python
# Factory para diferentes provedores
def create_agent_with_llm(provider: str):
    return BarbershopSchedulerAgent(
        name=f"agent_{provider}",
        llm_provider=provider,
        temperature=0.3,  # Mais determinístico para agendamentos
        max_tokens=500
    )

# Criar agents com diferentes provedores
agents = {
    "openai": create_agent_with_llm("openai"),
    "gemini": create_agent_with_llm("gemini"),
    "groq": create_agent_with_llm("groq")
}
```

## 🔧 Troubleshooting

### Erro: "LLM client not available"
- Verifique se a chave da API está configurada
- Confirme se as dependências estão instaladas:
  ```bash
  pip install openai google-generativeai groq
  ```

### Erro: "Import could not be resolved"
- Instale as dependências específicas do provedor:
  ```bash
  # OpenAI
  pip install openai
  
  # Gemini
  pip install google-generativeai
  
  # Groq
  pip install groq
  ```

### Fallback para Mock
O sistema automaticamente usa cliente mock se:
- Nenhuma chave de API está configurada
- Dependências não estão instaladas
- Ocorre erro na inicialização do provedor

## 📊 Comparação de Provedores

| Provedor | Velocidade | Custo | Qualidade | Português |
|----------|------------|-------|-----------|-----------|
| OpenAI   | Média      | Alto  | Excelente | Excelente |
| Gemini   | Rápida     | Baixo | Muito Boa | Muito Boa |
| Groq     | Muito Rápida | Baixo | Boa     | Boa       |
| Mock     | Instantâneo | Grátis | Básica  | Básica    |

## 💡 Recomendações

- **Desenvolvimento**: Use Mock para economia
- **Produção**: OpenAI para máxima qualidade
- **Custo-Benefício**: Gemini para equilíbrio
- **Velocidade**: Groq para respostas rápidas

## 🔄 Mudança de Provedor

```python
# Trocar provedor em runtime (não recomendado)
# Melhor recriar o agent

# EVITE:
# agent._llm_client = create_llm_client("novo_provedor")

# PREFIRA:
novo_agent = BarbershopSchedulerAgent(
    name="agent_atualizado",
    llm_provider="novo_provedor"
)
```
