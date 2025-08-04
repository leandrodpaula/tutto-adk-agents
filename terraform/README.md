# ADK Agents - Terraform Infrastructure

Este diretório contém a configuração Terraform para provisionar a infraestrutura necessária do ADK Agents no Google Cloud Platform.

## 🏗️ Arquitetura

A infraestrutura criada inclui:

- **Service Account** com permissões para Google Calendar e Gemini AI
- **Secret Manager** para armazenar chaves de API e configurações
- **IAM Roles** para acesso aos serviços necessários
- **APIs** habilitadas (Calendar, Generative AI, Secret Manager)

## 📁 Estrutura de Arquivos

```
terraform/
├── backend.tf          # Configuração do backend Terraform
├── provider.tf         # Configuração dos providers
├── main.tf            # Recursos principais e data sources
├── sa.tf              # Service Account e permissões IAM
├── secret.tf          # Secret Manager e armazenamento seguro
├── variables.tf       # Variáveis de entrada
├── outputs.tf         # Outputs do Terraform
├── terraform.tfvars.example  # Exemplo de configuração
└── README.md          # Este arquivo
```

## 🚀 Deployment

### Pré-requisitos

1. **Google Cloud SDK** instalado e configurado:
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

2. **Terraform** instalado (versão >= 1.0)

3. **Projeto Google Cloud** criado

### Passo a Passo

#### 1. Configurar variáveis
```bash
# Copiar arquivo de exemplo
cp terraform.tfvars.example terraform.tfvars

# Editar com suas configurações
nano terraform.tfvars
```

#### 2. Inicializar Terraform
```bash
cd terraform
terraform init
```

#### 3. Planejar deployment
```bash
terraform plan
```

#### 4. Aplicar configuração
```bash
terraform apply
```

#### 5. Anotar outputs importantes
```bash
terraform output service_account_email
terraform output configuration_summary
```

## 🔧 Configuração

### Variáveis Obrigatórias

```hcl
# terraform.tfvars
project_id = "seu-projeto-gcp"
```

### Variáveis Opcionais

```hcl
# Localização
region = "us-central1"
zone   = "us-central1-a"

# Ambiente
environment = "dev"  # dev, staging, prod

# Permissões
enable_calendar_admin = false

# Secrets a serem criados
create_gemini_api_key_secret = true
create_openai_api_key_secret = false
create_groq_api_key_secret   = false

# Configuração da barbearia
barbershop_name     = "Sua Barbearia"
barbershop_timezone = "America/Sao_Paulo"
barbershop_phone    = "+5511999999999"
barbershop_address  = "Seu endereço"
```

## 🔐 Segurança

### Service Account Criado

O Terraform cria um Service Account com as seguintes permissões:

- **roles/calendar.editor**: Gerenciar eventos do calendário
- **roles/aiplatform.user**: Usar Gemini AI
- **roles/secretmanager.secretAccessor**: Acessar secrets
- **roles/logging.logWriter**: Escrever logs
- **roles/monitoring.editor**: Métricas de monitoramento
- **roles/errorreporting.writer**: Relatórios de erro

### Secrets Criados

1. **Service Account Key**: Credenciais para autenticação
2. **App Configuration**: Configurações da aplicação
3. **API Keys**: Chaves para OpenAI, Gemini, Groq (opcionais)

## 📊 Recursos Criados

### Google Cloud APIs Habilitadas
- Google Calendar API
- Generative AI API  
- Secret Manager API
- IAM API
- Cloud Resource Manager API

### IAM Resources
- 1 Service Account
- 6+ IAM Role Bindings
- 1 Service Account Key

### Secret Manager
- 2-5 Secrets (dependendo da configuração)
- Versões iniciais dos secrets

## 🧪 Testando a Infraestrutura

### 1. Verificar Service Account
```bash
# Listar service accounts
gcloud iam service-accounts list

# Verificar permissões
gcloud projects get-iam-policy PROJECT_ID
```

### 2. Testar Secret Manager
```bash
# Listar secrets
gcloud secrets list

# Acessar service account key
gcloud secrets versions access latest --secret="adk-agents-dev-sa-key"
```

### 3. Verificar APIs habilitadas
```bash
gcloud services list --enabled
```

## 🔄 Pós-Deploy

### 1. Compartilhar Calendário

**IMPORTANTE**: Você deve compartilhar seu Google Calendar com o Service Account criado:

```bash
# Obter email do Service Account
terraform output service_account_email

# No Google Calendar (calendar.google.com):
# 1. Configurações do calendário
# 2. Compartilhar com pessoas específicas  
# 3. Adicionar o email do Service Account
# 4. Permissão: "Make changes to events"
```

### 2. Adicionar API Keys (se não foram definidas no Terraform)

```bash
# Adicionar chave do Gemini
echo "SUA_CHAVE_GEMINI" | gcloud secrets versions add adk-agents-dev-gemini-key --data-file=-

# Adicionar chave do OpenAI (se criado o secret)
echo "SUA_CHAVE_OPENAI" | gcloud secrets versions add adk-agents-dev-openai-key --data-file=-
```

### 3. Configurar Aplicação

Use as informações dos outputs para configurar sua aplicação:

```bash
# Ver todos os outputs
terraform output

# Configuração específica
terraform output configuration_summary
```

## 🗑️ Limpeza

Para remover todos os recursos:

```bash
terraform destroy
```

**⚠️ Atenção**: Isso removerá permanentemente todos os recursos criados!

## 📝 Troubleshooting

### Erro: "API not enabled"
```bash
# Habilitar APIs manualmente se necessário
gcloud services enable calendar-json.googleapis.com
gcloud services enable generativeai.googleapis.com
```

### Erro: "Insufficient permissions"
```bash
# Verificar permissões do usuário
gcloud auth list
gcloud projects get-iam-policy PROJECT_ID
```

### Erro: "Secret already exists"
```bash
# Importar secret existente
terraform import google_secret_manager_secret.service_account_key projects/PROJECT_ID/secrets/SECRET_NAME
```

## 🤝 Manutenção

### Rotação de Chaves
```bash
# Criar nova versão da chave
terraform apply -replace="google_service_account_key.adk_agents_key"
```

### Backup do State
```bash
# Para produção, configure backend remoto no backend.tf
terraform {
  backend "gcs" {
    bucket = "seu-bucket-terraform-state"
    prefix = "adk-agents"
  }
}
```

---

📖 **Para mais informações**: Consulte a documentação principal do projeto em `/README.md`
