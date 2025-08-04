# Service Accounts for ADK Agents

# Service Account for Google Calendar operations
resource "google_service_account" "calendar_sa" {
  count = var.enable_calendar_integration ? 1 : 0
  
  account_id   = "${var.application_name}-calendar-${var.environment}"
  display_name = "ADK Agents Calendar Service Account"
  description  = "Service Account for Google Calendar integration in ADK Agents"
  project      = var.project_id
}

# Service Account for Gemini AI operations
resource "google_service_account" "gemini_sa" {
  count = var.enable_gemini_integration ? 1 : 0
  
  account_id   = "${var.application_name}-gemini-${var.environment}"
  display_name = "ADK Agents Gemini Service Account"
  description  = "Service Account for Google Gemini AI integration in ADK Agents"
  project      = var.project_id
}

# Service Account for general application operations
resource "google_service_account" "app_sa" {
  account_id   = "${var.application_name}-app-${var.environment}"
  display_name = "ADK Agents Application Service Account"
  description  = "Main Service Account for ADK Agents application"
  project      = var.project_id
}

# Generate JSON keys for Service Accounts
resource "google_service_account_key" "calendar_key" {
  count = var.enable_calendar_integration ? 1 : 0
  
  service_account_id = google_service_account.calendar_sa[0].name
  public_key_type    = "TYPE_X509_PEM_FILE"
}

resource "google_service_account_key" "gemini_key" {
  count = var.enable_gemini_integration ? 1 : 0
  
  service_account_id = google_service_account.gemini_sa[0].name
  public_key_type    = "TYPE_X509_PEM_FILE"
}

resource "google_service_account_key" "app_key" {
  service_account_id = google_service_account.app_sa.name
  public_key_type    = "TYPE_X509_PEM_FILE"
}

# Save Service Account keys to local files
resource "local_sensitive_file" "calendar_credentials" {
  count = var.enable_calendar_integration ? 1 : 0
  
  content  = base64decode(google_service_account_key.calendar_key[0].private_key)
  filename = "${path.module}/../credentials/calendar-service-account.json"
  
  depends_on = [google_service_account_key.calendar_key]
}

resource "local_sensitive_file" "gemini_credentials" {
  count = var.enable_gemini_integration ? 1 : 0
  
  content  = base64decode(google_service_account_key.gemini_key[0].private_key)
  filename = "${path.module}/../credentials/gemini-service-account.json"
  
  depends_on = [google_service_account_key.gemini_key]
}

resource "local_sensitive_file" "app_credentials" {
  content  = base64decode(google_service_account_key.app_key.private_key)
  filename = "${path.module}/../credentials/app-service-account.json"
  
  depends_on = [google_service_account_key.app_key]
}
