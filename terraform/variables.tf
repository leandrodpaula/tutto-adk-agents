# Input variables for ADK Agents Terraform configuration

# Project configuration
variable "project_id" {
  description = "The Google Cloud Project ID where resources will be created"
  type        = string
  validation {
    condition     = length(var.project_id) > 0
    error_message = "Project ID cannot be empty."
  }
}

variable "region" {
  description = "The Google Cloud region for resources"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "The Google Cloud zone for resources"
  type        = string
  default     = "us-central1-a"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

# Service Account configuration
variable "enable_calendar_admin" {
  description = "Enable Calendar Admin role for the service account (use with caution)"
  type        = bool
  default     = false
}

# Secret Manager configuration
variable "create_gemini_api_key_secret" {
  description = "Create a secret for storing Gemini API key"
  type        = bool
  default     = true
}

variable "create_openai_api_key_secret" {
  description = "Create a secret for storing OpenAI API key"
  type        = bool
  default     = false
}

variable "create_groq_api_key_secret" {
  description = "Create a secret for storing Groq API key"
  type        = bool
  default     = false
}

# API Keys (optional - can be set later via Secret Manager UI)
variable "gemini_api_key" {
  description = "Gemini API key (optional - can be set later)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "openai_api_key" {
  description = "OpenAI API key (optional - can be set later)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "groq_api_key" {
  description = "Groq API key (optional - can be set later)"
  type        = string
  default     = ""
  sensitive   = true
}

# Barbershop configuration
variable "barbershop_name" {
  description = "Name of the barbershop"
  type        = string
  default     = "Barbearia ADK"
}

variable "barbershop_timezone" {
  description = "Timezone for the barbershop"
  type        = string
  default     = "America/Sao_Paulo"
}

variable "barbershop_phone" {
  description = "Phone number of the barbershop"
  type        = string
  default     = "+5511999999999"
}

variable "barbershop_address" {
  description = "Address of the barbershop"
  type        = string
  default     = "Rua das Flores, 123 - São Paulo, SP"
}

# Calendar configuration
variable "calendar_id" {
  description = "Google Calendar ID to use (default: primary)"
  type        = string
  default     = "primary"
}
