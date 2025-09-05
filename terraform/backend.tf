
terraform {
  backend "gcs" {}
}

data "terraform_remote_state" "remote" {
  backend = "gcs"
  config = {
    bucket = "${var.project_id}-tfstate"
    prefix = "${var.project_id}/${var.environment}"
  }
}
