

resource "google_storage_bucket" "staging" {
    name     = "${var.service_name}-staging-${var.environment}"
    location = var.region
}