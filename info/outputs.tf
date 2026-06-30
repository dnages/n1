
output "VMSS_public_ip" {
  description = "The public IP address of the VMSS."
  value       = azurerm_windows_virtual_machine_scale_set.VMSS.public_ip
}