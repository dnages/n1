terraform {
  required_version = ">= 1.7.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }

  # Remote state is stored in Azure Storage (created once via bootstrap/).
  # Backend connection details are injected at init time by the Azure DevOps
  # pipeline or via -backend-config flags locally.
  backend "azurerm" {}
}

provider "azurerm" {
  features {}
}
