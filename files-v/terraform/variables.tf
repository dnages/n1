variable "resource_group_name" {
  description = "Resource group for prime-counter project resources."
  type        = string
  default     = "rg-prime-counter"
}

variable "location" {
  description = "Azure region for all resources."
  type        = string
  default     = "centralindia"
}

variable "environment" {
  description = "Environment tag (dev, test, prod)."
  type        = string
  default     = "dev"
}

variable "storage_account_name" {
  description = "Globally unique storage account name for benchmark artifacts."
  type        = string
  default     = "stprimecounter001"
}

variable "tags" {
  description = "Extra tags applied to every resource."
  type        = map(string)
  default     = {}
}
