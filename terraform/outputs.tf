# Output values for ADK Agents Terraform configuration
# These outputs can be used by other Terraform configurations or for reference

# Service Account outputs
output "service_account_email" {
  description = "Email of the created service account"
  value       = google_service_account.adk_agents_sa.email
}

output "service_account_unique_id" {
  description = "Unique ID of the created service account"
  value       = google_service_account.adk_agents_sa.unique_id
}

output "service_account_key" {
  description = "The service account key (base64 encoded JSON)"
  value       = google_service_account_key.adk_agents_key.private_key
  sensitive   = true
}

# Project information
output "project_id" {
  description = "The Google Cloud Project ID"
  value       = var.project_id
}

output "project_number" {
  description = "The Google Cloud Project Number"
  value       = data.google_project.project.number
}

# Secret Manager outputs
output "service_account_secret_name" {
  description = "Name of the secret containing the service account key"
  value       = google_secret_manager_secret.service_account_key.name
}

output "service_account_secret_id" {
  description = "Full resource ID of the service account secret"
  value       = google_secret_manager_secret.service_account_key.id
}

output "app_config_secret_name" {
  description = "Name of the secret containing application configuration"
  value       = google_secret_manager_secret.app_config.name
}

output "app_config_secret_id" {
  description = "Full resource ID of the application configuration secret"
  value       = google_secret_manager_secret.app_config.id
}

# API Key secrets (conditional outputs)
output "gemini_secret_name" {
  description = "Name of the secret for Gemini API key"
  value       = var.create_gemini_api_key_secret ? google_secret_manager_secret.gemini_api_key[0].name : null
}

output "openai_secret_name" {
  description = "Name of the secret for OpenAI API key"
  value       = var.create_openai_api_key_secret ? google_secret_manager_secret.openai_api_key[0].name : null
}

output "groq_secret_name" {
  description = "Name of the secret for Groq API key"
  value       = var.create_groq_api_key_secret ? google_secret_manager_secret.groq_api_key[0].name : null
}

# Configuration outputs for easy reference
output "configuration_summary" {
  description = "Summary of the deployed configuration"
  value = {
    project_id    = var.project_id
    region        = var.region
    environment   = var.environment
    sa_email      = google_service_account.adk_agents_sa.email
    barbershop    = {
      name     = var.barbershop_name
      phone    = var.barbershop_phone
      timezone = var.barbershop_timezone
      address  = var.barbershop_address
    }
    calendar_id   = var.calendar_id
    secrets_created = {
      service_account = google_secret_manager_secret.service_account_key.name
      app_config     = google_secret_manager_secret.app_config.name
      gemini_key     = var.create_gemini_api_key_secret ? google_secret_manager_secret.gemini_api_key[0].name : "not_created"
      openai_key     = var.create_openai_api_key_secret ? google_secret_manager_secret.openai_api_key[0].name : "not_created"
      groq_key       = var.create_groq_api_key_secret ? google_secret_manager_secret.groq_api_key[0].name : "not_created"
    }
  }
}

# Instructions for next steps
output "next_steps" {
  description = "Instructions for completing the setup"
  value = <<-EOT
    
    🎉 ADK Agents infrastructure has been deployed successfully!
    
    📋 Next Steps:
    
    1. 📧 Share your Google Calendar with the service account:
       Email: ${google_service_account.adk_agents_sa.email}
       Permission: "Make changes to events"
    
    2. 🔑 Add API keys to Secret Manager (if not done via Terraform):
       - Gemini: ${var.create_gemini_api_key_secret ? google_secret_manager_secret.gemini_api_key[0].name : "not_created"}
       - OpenAI: ${var.create_openai_api_key_secret ? google_secret_manager_secret.openai_api_key[0].name : "not_created"}  
       - Groq: ${var.create_groq_api_key_secret ? google_secret_manager_secret.groq_api_key[0].name : "not_created"}
    
    3. 🚀 Deploy your ADK Agents application using:
       - Service Account: ${google_service_account.adk_agents_sa.email}
       - Configuration Secret: ${google_secret_manager_secret.app_config.name}
    
    4. 🧪 Test the setup:
       gcloud secrets versions access latest --secret=${google_secret_manager_secret.service_account_key.secret_id}
    
    📖 For detailed setup instructions, see: /terraform/README.md
    
  EOT
}
