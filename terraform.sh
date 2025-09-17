#!/bin/bash

# Export environment variables
export TF_VAR_project_id="tutto-assistants"
export TF_VAR_environment="hml"
export TF_VAR_region="us-central1"
export TF_VAR_service_name="tutto-adk-agents"
cd terraform

# Initialize Terraform
terraform init -backend-config="bucket=${TF_VAR_project_id}-tfstate" -backend-config="prefix=${TF_VAR_project_id}/${TF_VAR_service_name}/${TF_VAR_environment}" -reconfigure

# Apply the Terraform configuration
if [ "$1" == "apply" ]; then
  terraform apply -auto-approve
fi

# Destroy the Terraform configuration
if [ "$1" == "destroy" ]; then
  terraform destroy -auto-approve "$2"
fi

# Unlock the Terraform state
if [ "$1" == "unlock" ]; then
  terraform force-unlock -force "$2"
fi