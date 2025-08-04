# 📅 Guia Completo: Configurar Google Calendar

## 🎯 Resumo Rápido

### Service Account (Recomendado)
1. **Google Cloud Console** → Criar projeto → Ativar Calendar API
2. **Service Account** → Baixar JSON → Salvar em `credentials/`
3. **Compartilhar calendário** com email do Service Account
4. **Configurar .env** → Testar

### OAuth2 (Desenvolvimento)
1. **Google Cloud Console** → OAuth 2.0 Client → Desktop App
2. **Baixar client_secrets.json** → Salvar em `credentials/`
3. **Configurar .env** → Testar

---

## 📋 Passo a Passo Detalhado

### 🔧 Service Account (Produção)

#### 1. Google Cloud Console Setup
```
https://console.cloud.google.com/
│
├── Criar/Selecionar Projeto
├── APIs & Services → Library
├── Buscar "Google Calendar API"
└── Clicar "Enable"
```

#### 2. Criar Service Account
```
APIs & Services → Credentials
│
├── Create Credentials → Service Account
├── Nome: barbershop-calendar-bot  
├── Descrição: Service account para agendamentos
├── Create and Continue
├── Pular permissões → Done
└── Service Account criado ✅
```

#### 3. Gerar Chave JSON
```
Lista de Service Accounts
│
├── Clicar no Service Account criado
├── Aba "Keys"
├── Add Key → Create new key
├── Formato: JSON
├── Create
└── Arquivo baixado! 📁
```

#### 4. Configurar Credenciais
```bash
# Mover arquivo baixado para projeto:
mv ~/Downloads/projeto-123abc-456def.json ./credentials/service-account.json

# Configurar no .env:
GOOGLE_SERVICE_ACCOUNT_FILE=./credentials/service-account.json
GOOGLE_CALENDAR_ID=primary
```

#### 5. Compartilhar Calendário
```
Google Calendar (calendar.google.com)
│
├── Seu calendário → ⋮ → Settings and sharing
├── Share with specific people → Add people
├── Email: service-account@projeto.iam.gserviceaccount.com
├── Permissão: Make changes to events
└── Send ✅
```

### 🔧 OAuth2 (Desenvolvimento)

#### 1. Configurar OAuth2
```
Google Cloud Console → Credentials
│
├── Create Credentials → OAuth 2.0 Client IDs
├── Application type: Desktop application
├── Name: Barbershop Calendar Client
├── Create
└── Download JSON
```

#### 2. Salvar Credenciais
```bash
mv ~/Downloads/client_secret_123.json ./credentials/client_secrets.json
```

#### 3. Configurar .env
```bash
GOOGLE_CLIENT_SECRETS_FILE=./credentials/client_secrets.json
```

---

## 🧪 Testando a Configuração

### Verificar Configuração
```bash
python validate_config.py
```

### Testar Integração
```bash
./run_example.sh
```

### Debug Manual
```python
from tools.integrations.google_calendar_client import create_calendar_client
import asyncio

async def test():
    client = create_calendar_client()
    calendars = await client.list_calendars()
    print(f"Calendários encontrados: {len(calendars)}")
    for cal in calendars:
        print(f"  - {cal['summary']}")

asyncio.run(test())
```

---

## ⚠️ Troubleshooting

### Erro: "404 Calendar not found"
- ✅ Verificar se compartilhou o calendário com Service Account
- ✅ Confirmar que GOOGLE_CALENDAR_ID está correto

### Erro: "403 Forbidden"  
- ✅ Verificar permissões do Service Account no calendário
- ✅ Confirmar que Calendar API está habilitada

### Erro: "File not found"
- ✅ Verificar caminho do arquivo JSON
- ✅ Confirmar que arquivo existe em `credentials/`

### Service Account Email
```bash
# Encontrar email do Service Account:
cat credentials/service-account.json | grep client_email
```

---

## 🔒 Segurança

### .gitignore
```
credentials/*.json
credentials/*.key
service-account.json
client_secrets.json
```

### Permissões Mínimas
- **Service Account**: Apenas "Calendar → Make changes to events"
- **Não dar** permissões de administrador desnecessárias

### Rotação de Chaves
- Gerar novas chaves a cada 90 dias
- Revogar chaves antigas no Google Cloud Console

---

## 📊 Status de Integração

| Método | Segurança | Complexidade | Produção |
|--------|-----------|--------------|----------|
| Service Account | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ Sim |
| OAuth2 | ⭐⭐⭐ | ⭐⭐ | ❌ Não |
| Mock | ⭐ | ⭐ | ❌ Desenvolvimento |

**Recomendação**: Use Service Account para produção! 🚀
