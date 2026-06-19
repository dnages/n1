output "resource_group_name" {
  description = "Name of the deployed resource group."
  value       = azurerm_resource_group.main.name
}

output "benchmark_storage_account_name" {
  description = "Storage account that holds benchmark JSON artifacts."
  value       = azurerm_storage_account.benchmarks.name
}

output "benchmark_container_name" {
  description = "Blob container name for benchmark results."
  value       = azurerm_storage_container.benchmark_results.name
}

output "log_analytics_workspace_id" {
  description = "Log Analytics workspace GUID."
  value       = azurerm_log_analytics_workspace.main.workspace_id
}

output "log_analytics_workspace_resource_id" {
  description = "Full ARM resource ID of the Log Analytics workspace."
  value       = azurerm_log_analytics_workspace.main.id
}
