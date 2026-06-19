#!/usr/bin/env bash
#
# bootstrap-backend.sh
#
# Run ONCE before the first Azure DevOps pipeline run. Creates the Azure
# Storage Account that holds Terraform remote state.
#
# Usage:
#   az login
#   ./bootstrap-backend.sh
#
set -euo pipefail

LOCATION="centralindia"
STATE_RESOURCE_GROUP="rg-tfstate"
STATE_STORAGE_ACCOUNT="sttfstateprime$RANDOM"
STATE_CONTAINER="tfstate"

echo "Creating resource group: $STATE_RESOURCE_GROUP"
az group create --name "$STATE_RESOURCE_GROUP" --location "$LOCATION"

echo "Creating storage account: $STATE_STORAGE_ACCOUNT"
az storage account create \
  --name "$STATE_STORAGE_ACCOUNT" \
  --resource-group "$STATE_RESOURCE_GROUP" \
  --location "$LOCATION" \
  --sku Standard_LRS \
  --min-tls-version TLS1_2 \
  --allow-blob-public-access false

echo "Creating blob container: $STATE_CONTAINER"
az storage container create \
  --name "$STATE_CONTAINER" \
  --account-name "$STATE_STORAGE_ACCOUNT" \
  --auth-mode login

cat <<EOF

Backend bootstrap complete. Add these values to the Azure DevOps variable
group "tfstate-backend" (see README.md):

  backend_resource_group   = $STATE_RESOURCE_GROUP
  backend_storage_account  = $STATE_STORAGE_ACCOUNT
  backend_container        = $STATE_CONTAINER
  backend_key              = prime-counter.tfstate

EOF
