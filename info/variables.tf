resource "azurerm_resource_group" "RG" {
  name     = "VM_resource_group"
  location = "West Europe"
}
resource "azurerm_virtual_network" "VM_network" {
  name                = "VM_network"
  resource_group_name = azurerm_resource_group.RG.name
  location            = azurerm_resource_group.RG.location
  
}
resource "azurerm_subnet" "VM_subnet" {
  name                 = "VM_subnet"
  resource_group_name  = azurerm_resource_group.RG.name
  virtual_network_name = azurerm_virtual_network.VM_network.name
  
}
