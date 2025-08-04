# Secret Manager configuration for storing sensitive credentials
# Stores API keys and service account credentials securely

# Secret for storing the service account key
resource "google_secret_manager_secret" "service_account_key" {
  secret_id = "${local.project_name}-${local.environment}-sa-key"
  project   = var.project_id
  
  labels = local.common_labels
  
  replication {
    auto {}
  }
}

# Store the service account key in Secret Manager
resource "google_secret_manager_secret_version" "service_account_key_version" {
  secret      = google_secret_manager_secret.service_account_key.id
  secret_data = base64decode(google_service_account_key.adk_agents_key.private_key)
}

# Secret for storing Gemini API key (if using API key instead of SA)
resource "google_secret_manager_secret" "gemini_api_key" {
  count     = var.create_gemini_api_key_secret ? 1 : 0
  secret_id = "${local.project_name}-${local.environment}-gemini-key"
  project   = var.project_id
  
  labels = local.common_labels
  
  replication {
    auto {}
  }
}

# Store Gemini API key (manual step required)
resource "google_secret_manager_secret_version" "gemini_api_key_version" {
  count       = var.create_gemini_api_key_secret && var.gemini_api_key != "" ? 1 : 0
  secret      = google_secret_manager_secret.gemini_api_key[0].id
  secret_data = var.gemini_api_key
}

# Secret for storing OpenAI API key (optional)
resource "google_secret_manager_secret" "openai_api_key" {
  count     = var.create_openai_api_key_secret ? 1 : 0
  secret_id = "${local.project_name}-${local.environment}-openai-key"
  project   = var.project_id
  
  labels = local.common_labels
  
  replication {
    auto {}
  }
}

# Store OpenAI API key (manual step required)
resource "google_secret_manager_secret_version" "openai_api_key_version" {
  count       = var.create_openai_api_key_secret && var.openai_api_key != "" ? 1 : 0
  secret      = google_secret_manager_secret.openai_api_key[0].id
  secret_data = var.openai_api_key
}

# Secret for storing Groq API key (optional)
resource "google_secret_manager_secret" "groq_api_key" {
  count     = var.create_groq_api_key_secret ? 1 : 0
  secret_id = "${local.project_name}-${local.environment}-groq-key"
  project   = var.project_id
  
  labels = local.common_labels
  
  replication {
    auto {}
  }
}

# Store Groq API key (manual step required)
resource "google_secret_manager_secret_version" "groq_api_key_version" {
  count       = var.create_groq_api_key_secret && var.groq_api_key != "" ? 1 : 0
  secret      = google_secret_manager_secret.groq_api_key[0].id
  secret_data = var.groq_api_key
}

# Secret for application configuration
resource "google_secret_manager_secret" "app_config" {
  secret_id = "${local.project_name}-${local.environment}-config"
  project   = var.project_id
  
  labels = local.common_labels
  
  replication {
    auto {}
  }
}

# Store application configuration
resource "google_secret_manager_secret_version" "app_config_version" {
  secret = google_secret_manager_secret.app_config.id
  secret_data = jsonencode({
    project_id = var.project_id
    region     = var.region
    environment = var.environment
    service_account_email = google_service_account.adk_agents_sa.email
    barbershop_name = var.barbershop_name
    barbershop_timezone = var.barbershop_timezone
    barbershop_phone = var.barbershop_phone
    barbershop_address = var.barbershop_address
  })
}
