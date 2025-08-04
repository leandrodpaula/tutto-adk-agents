# APIs and Permissions for ADK Agents

# Enable required Google Cloud APIs
resource "google_project_service" "calendar_api" {
  count = var.enable_calendar_integration ? 1 : 0
  
  project = var.project_id
  service = "calendar.googleapis.com"
  
  disable_dependent_services = false
  disable_on_destroy        = false
}

resource "google_project_service" "ai_platform_api" {
  count = var.enable_gemini_integration ? 1 : 0
  
  project = var.project_id
  service = "aiplatform.googleapis.com"
  
  disable_dependent_services = false
  disable_on_destroy        = false
}

resource "google_project_service" "generative_ai_api" {
  count = var.enable_gemini_integration ? 1 : 0
  
  project = var.project_id
  service = "generativelanguage.googleapis.com"
  
  disable_dependent_services = false
  disable_on_destroy        = false
}

resource "google_project_service" "cloud_resource_manager_api" {
  project = var.project_id
  service = "cloudresourcemanager.googleapis.com"
  
  disable_dependent_services = false
  disable_on_destroy        = false
}

resource "google_project_service" "iam_api" {
  project = var.project_id
  service = "iam.googleapis.com"
  
  disable_dependent_services = false
  disable_on_destroy        = false
}

resource "google_project_service" "storage_api" {
  count = var.create_storage_bucket ? 1 : 0
  
  project = var.project_id
  service = "storage.googleapis.com"
  
  disable_dependent_services = false
  disable_on_destroy        = false
}

# IAM roles for Calendar Service Account
resource "google_project_iam_member" "calendar_sa_roles" {
  count = var.enable_calendar_integration ? 1 : 0
  
  project = var.project_id
  role    = "roles/calendar.editor"
  member  = "serviceAccount:${google_service_account.calendar_sa[0].email}"
  
  depends_on = [google_project_service.calendar_api]
}

# IAM roles for Gemini Service Account
resource "google_project_iam_member" "gemini_sa_aiplatform" {
  count = var.enable_gemini_integration ? 1 : 0
  
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.gemini_sa[0].email}"
  
  depends_on = [google_project_service.ai_platform_api]
}

resource "google_project_iam_member" "gemini_sa_ml" {
  count = var.enable_gemini_integration ? 1 : 0
  
  project = var.project_id
  role    = "roles/ml.developer"
  member  = "serviceAccount:${google_service_account.gemini_sa[0].email}"
  
  depends_on = [google_project_service.ai_platform_api]
}

# Basic roles for Application Service Account
resource "google_project_iam_member" "app_sa_basic" {
  project = var.project_id
  role    = "roles/serviceusage.serviceUsageConsumer"
  member  = "serviceAccount:${google_service_account.app_sa.email}"
}

# Storage permissions if bucket is created
resource "google_project_iam_member" "app_sa_storage" {
  count = var.create_storage_bucket ? 1 : 0
  
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.app_sa.email}"
  
  depends_on = [google_project_service.storage_api]
}
