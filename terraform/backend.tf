# Backend configuration for Terraform state
# Configure remote state storage in Google Cloud Storage

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }

  # Remote state configuration - uncomment and configure for production
  # backend "gcs" {
  #   bucket = "your-terraform-state-bucket-name"
  #   prefix = "adk-agents/terraform/state"
  # }
  
  # For development, you can use local state by commenting out the backend block
}
