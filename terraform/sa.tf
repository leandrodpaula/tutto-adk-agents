# Service Account configuration for ADK Agents
# Creates SA with permissions for Google Calendar and Gemini AI

# Create the main service account for ADK Agents
resource "google_service_account" "adk_agents_sa" {
  account_id   = local.sa_name
  display_name = local.sa_display_name
  description  = local.sa_description
  project      = var.project_id
}

# Create service account key for authentication
resource "google_service_account_key" "adk_agents_key" {
  service_account_id = google_service_account.adk_agents_sa.name
  public_key_type    = "TYPE_X509_PEM_FILE"
  private_key_type   = "TYPE_GOOGLE_CREDENTIALS_FILE"
}

# IAM bindings for the service account
# Calendar API permissions
resource "google_project_iam_member" "calendar_editor" {
  project = var.project_id
  role    = "roles/calendar.editor"
  member  = "serviceAccount:${google_service_account.adk_agents_sa.email}"
}

# Additional Calendar permissions for full access
resource "google_project_iam_member" "calendar_admin" {
  count   = var.enable_calendar_admin ? 1 : 0
  project = var.project_id
  role    = "roles/calendar.admin"
  member  = "serviceAccount:${google_service_account.adk_agents_sa.email}"
}

# Generative AI permissions for Gemini
resource "google_project_iam_member" "generative_ai_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.adk_agents_sa.email}"
}

# Vertex AI permissions for enhanced Gemini access
resource "google_project_iam_member" "vertex_ai_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.adk_agents_sa.email}"
}

# Secret Manager permissions to access stored credentials
resource "google_project_iam_member" "secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.adk_agents_sa.email}"
}

# Logging permissions for monitoring
resource "google_project_iam_member" "logging_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.adk_agents_sa.email}"
}

# Monitoring permissions
resource "google_project_iam_member" "monitoring_writer" {
  project = var.project_id
  role    = "roles/monitoring.editor"
  member  = "serviceAccount:${google_service_account.adk_agents_sa.email}"
}

# Error Reporting permissions
resource "google_project_iam_member" "error_writer" {
  project = var.project_id
  role    = "roles/errorreporting.writer"
  member  = "serviceAccount:${google_service_account.adk_agents_sa.email}"
}
