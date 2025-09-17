
terraform {
  backend "gcs" {}
}

data "terraform_remote_state" "remote" {
  backend = "gcs"
  config = {
    bucket = "${var.project_id}-tfstate"
    prefix = "${var.service_name}/${var.environment}"
  }
}
