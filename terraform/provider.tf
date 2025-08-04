# Provider configuration for Google Cloud
# Configures authentication and default settings

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
  
  # Authentication will be handled by:
  # 1. GOOGLE_APPLICATION_CREDENTIALS environment variable
  # 2. gcloud auth application-default login
  # 3. Service account key file specified in terraform
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

provider "random" {
  # No configuration needed
}
