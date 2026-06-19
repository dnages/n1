locals {
  common_tags = merge(
    {
      environment = var.environment
      managed_by  = "terraform"
      project     = "prime-counter"
    },
    var.tags
  )
}

resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
  tags     = local.common_tags
}

# Stores benchmark JSON output uploaded by the Azure DevOps pipeline.
resource "azurerm_storage_account" "benchmarks" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"
  allow_nested_items_to_be_public = false
  tags                     = local.common_tags
}

resource "azurerm_storage_container" "benchmark_results" {
  name                  = "benchmark-results"
  storage_account_id    = azurerm_storage_account.benchmarks.id
  container_access_type = "private"
}

# Central place to query pipeline and benchmark logs from the Azure Portal.
resource "azurerm_log_analytics_workspace" "main" {
  name                = "log-prime-counter"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = local.common_tags
}

resource "azurerm_monitor_diagnostic_setting" "storage" {
  name                       = "diag-benchmark-storage"
  target_resource_id         = azurerm_storage_account.benchmarks.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  enabled_metric {
    category = "Transaction"
  }
}
