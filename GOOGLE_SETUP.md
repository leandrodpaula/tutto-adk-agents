# Configuração das Credenciais do Google Calendar

## Métodos de Autenticação

### 1. Service Account (Recomendado para aplicações)

1. Acesse o [Google Cloud Console](https://console.cloud.google.com)
2. Crie um novo projeto ou selecione um existente
3. Ative a API do Google Calendar:
   - Vá para "APIs & Services" > "Library"
   - Pesquise por "Google Calendar API"
   - Clique em "Enable"

4. Crie uma Service Account:
   - Vá para "APIs & Services" > "Credentials"
   - Clique em "Create Credentials" > "Service Account"
   - Preencha o nome e descrição
   - Clique em "Create and Continue"

5. Baixe a chave JSON:
   - Na página da Service Account criada
   - Vá para a aba "Keys"
   - Clique em "Add Key" > "Create new key"
   - Selecione "JSON" e baixe o arquivo

6. Configure as variáveis de ambiente:
```bash
export GOOGLE_PROJECT_ID="seu-projeto-id"
export GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
export GOOGLE_CLIENT_EMAIL="service-account@projeto.iam.gserviceaccount.com"
export GOOGLE_CALENDAR_ID="primary"  # ou ID específico do calendário
```

### 2. OAuth2 (Para aplicações que acessam calendários de usuários)

1. No Google Cloud Console, crie credenciais OAuth2:
   - Vá para "APIs & Services" > "Credentials"
   - Clique em "Create Credentials" > "OAuth 2.0 Client IDs"
   - Configure o tipo de aplicação

2. Baixe o arquivo `credentials.json`

3. Configure as variáveis de ambiente:
```bash
export GOOGLE_OAUTH_CLIENT_ID="seu-client-id"
export GOOGLE_OAUTH_CLIENT_SECRET="seu-client-secret"
export GOOGLE_OAUTH_REDIRECT_URI="http://localhost:8080/callback"
```

## Arquivo .env (Exemplo)

Crie um arquivo `.env` na raiz do projeto:

```env
# Google Calendar API - Service Account
GOOGLE_PROJECT_ID=meu-projeto-barbershop
GOOGLE_CLIENT_EMAIL=barbershop-scheduler@meu-projeto.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC...
-----END PRIVATE KEY-----
GOOGLE_CALENDAR_ID=primary

# Configurações da Barbearia
BARBERSHOP_NAME=Barbearia do João
BARBERSHOP_TIMEZONE=America/Sao_Paulo
BARBERSHOP_PHONE=+5511999999999
BARBERSHOP_ADDRESS=Rua das Flores, 123 - São Paulo, SP

# Configurações do Agent
AGENT_NAME=barbershop_scheduler
ENABLE_MOCK_MODE=false
LOG_LEVEL=INFO
```

## Compartilhar Calendário com Service Account

Para que a Service Account possa acessar o calendário:

1. Abra o Google Calendar
2. Vá nas configurações do calendário que deseja usar
3. Em "Compartilhar com pessoas específicas", adicione o email da Service Account
4. Dê permissão de "Fazer alterações em eventos"

## Testar Configuração

Execute este script para testar as credenciais:

```python
import os
from tools.integrations.google_calendar_client import create_calendar_client

async def test_credentials():
    try:
        client = create_calendar_client()
        
        # Testar listagem de calendários
        calendars = await client.list_calendars()
        print(f"✅ Credenciais OK! Encontrados {len(calendars)} calendários")
        
        for calendar in calendars:
            print(f"  📅 {calendar['summary']} ({calendar['id']})")
            
    except Exception as e:
        print(f"❌ Erro nas credenciais: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_credentials())
```

## Segurança

⚠️ **IMPORTANTE**: 

- Nunca commite credenciais no Git
- Use variáveis de ambiente ou arquivos `.env`
- Adicione `.env` no `.gitignore`
- Restrinja as permissões da Service Account
- Use HTTPS em produção
- Monitore o uso da API

## Troubleshooting

### Erro: "Access denied"
- Verifique se a API está habilitada
- Confirme se o calendário foi compartilhado com a Service Account

### Erro: "Invalid credentials" 
- Verifique as variáveis de ambiente
- Confirme se a chave privada está correta (incluindo quebras de linha)

### Erro: "Calendar not found"
- Use "primary" para o calendário principal
- Ou obtenha o ID específico do calendário nas configurações

### Erro: "Quota exceeded"
- Monitore o uso da API no Google Cloud Console
- Implemente rate limiting se necessário
