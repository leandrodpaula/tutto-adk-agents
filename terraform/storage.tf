# Storage and other resources for ADK Agents

# Storage bucket for application data
resource "google_storage_bucket" "app_bucket" {
  count = var.create_storage_bucket ? 1 : 0
  
  name     = "${var.project_id}-${var.application_name}-${var.environment}"
  location = var.region
  project  = var.project_id
  
  # Prevent accidental deletion
  lifecycle {
    prevent_destroy = true
  }
  
  # Versioning for important files
  versioning {
    enabled = true
  }
  
  # Encryption
  encryption {
    default_kms_key_name = null
  }
  
  # Lifecycle management
  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }
  
  # Public access prevention
  public_access_prevention = "enforced"
  
  # Uniform bucket-level access
  uniform_bucket_level_access = true
  
  labels = merge(var.tags, {
    environment = var.environment
    purpose     = "adk-agents-storage"
  })
}

# Secret for storing API keys (if using Google Secret Manager)
resource "google_secret_manager_secret" "api_keys" {
  secret_id = "${var.application_name}-api-keys-${var.environment}"
  project   = var.project_id
  
  labels = merge(var.tags, {
    environment = var.environment
    purpose     = "api-keys"
  })
  
  replication {
    auto {}
  }
}

# Secret version for API keys
resource "google_secret_manager_secret_version" "api_keys_version" {
  secret      = google_secret_manager_secret.api_keys.id
  secret_data = jsonencode({
    openai_api_key = "your-openai-api-key-here"
    groq_api_key   = "your-groq-api-key-here"
    google_api_key = "your-google-api-key-here"
  })
  
  lifecycle {
    ignore_changes = [secret_data]
  }
}

# IAM for Secret Manager access
resource "google_secret_manager_secret_iam_member" "api_keys_accessor" {
  secret_id = google_secret_manager_secret.api_keys.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.app_sa.email}"
  project   = var.project_id
}

# Enable Secret Manager API
resource "google_project_service" "secret_manager_api" {
  project = var.project_id
  service = "secretmanager.googleapis.com"
  
  disable_dependent_services = false
  disable_on_destroy        = false
}
