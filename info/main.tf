provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "RG" {
  name     = RG.name
  location = RG.location
}

resource "azurerm_virtual_network" "VM_network" {
  name                = azurerm_virtual_network.VM_network.name
  resource_group_name = azurerm_resource_group.RG.name
  location            = azurerm_resource_group.RG.location
  address_space       = ["10.0.0.0/16"]
}

resource "azurerm_subnet" "VM_subnet" {
  name                 = azurerm_subnet.VM_subnet.name
  resource_group_name  = azurerm_resource_group.RG.name
  virtual_network_name = azurerm_virtual_network.VM_network.name
  address_prefixes     = ["10.0.2.0/24"]
}

resource "azurerm_windows_virtual_machine_scale_set" "VMSS" {
  name                 = azurerm_windows_virtual_machine_scale_set.VMSS.name
  resource_group_name  = azurerm_resource_group.RG.name
  location             = azurerm_resource_group.RG.location
  sku                  = "Standard_D4_v5"
  instances            = 1
  admin_password       = "P@55w0rd1234!"
  admin_username       = "adminuser"
  computer_name_prefix = "vm-"

  source_image_reference {
    publisher = "MicrosoftWindowsServer"
    offer     = "WindowsServer"
    sku       = "2016-Datacenter-Server-Core"
    version   = "latest"
  }

  os_disk {
    storage_account_type = "Standard_LRS"
    caching              = "ReadWrite"
  }

  network_interface {
    name    = "example"
    primary = true

    ip_configuration {
      name      = "internal"
      primary   = true
      subnet_id = azurerm_subnet.VM_subnet.id
    }
  }
}