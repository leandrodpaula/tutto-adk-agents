# Main Terraform configuration for ADK Agents deployment on AgentSpace
# This file orchestrates the creation of all necessary Google Cloud resources

# Data sources
data "google_project" "project" {
  project_id = var.project_id
}

# Create a random suffix for unique resource names
resource "random_id" "suffix" {
  byte_length = 4
}

# Local values for resource naming
locals {
  project_name = "adk-agents"
  environment  = var.environment
  suffix       = random_id.suffix.hex
  
  # Common labels
  common_labels = {
    project     = local.project_name
    environment = local.environment
    managed_by  = "terraform"
    team        = "adk-team"
  }
  
  # Service account names
  sa_name = "${local.project_name}-${local.environment}-sa"
  sa_display_name = "ADK Agents Service Account"
  sa_description = "Service Account for ADK Agents - Calendar and Gemini access"
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "calendar-json.googleapis.com",
    "generativeai.googleapis.com",
    "iam.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "secretmanager.googleapis.com"
  ])
  
  project = var.project_id
  service = each.value
  
  disable_on_destroy = false
}
