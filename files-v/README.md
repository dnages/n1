# Azure VM Scale Set Auto Scaling — Terraform + Python + Azure DevOps

Automated deployment of an Azure Virtual Machine Scale Set (VMSS) behind a
load balancer, with CPU-based auto scaling provided both natively by Azure
Monitor and by a custom Python script, deployed through an Azure DevOps
pipeline sourced from GitHub.

> **Terminology note:** the original spec referenced AWS tools (Boto3, EC2,
> CloudWatch). This project uses their Azure equivalents throughout:
>
> | AWS term (original ask) | Azure equivalent (used here) |
> |---|---|
> | EC2 Auto Scaling Group + Launch Template | Virtual Machine Scale Set (VMSS) |
> | IAM role | Azure RBAC role assignment / Managed Identity |
> | Security Group | Network Security Group (NSG) |
> | Application Load Balancer (ALB) | Azure Load Balancer (Standard SKU) |
> | Boto3 | Azure SDK for Python (`azure-mgmt-compute`, `azure-mgmt-monitor`) |
> | CloudWatch Logs/Metrics | Azure Monitor / Log Analytics workspace |

## Architecture

```
                          Internet
                             │
                      Public IP (Standard)
                             │
                    Azure Load Balancer
                       (port 80, TCP probe)
                             │
              ┌──────────────┴──────────────┐
              │     VM Scale Set (Linux)     │
              │  NSG: 80 from LB, 22 from    │
              │  your IP, deny all else      │
              │  Managed Identity attached   │
              └──────────────┬──────────────┘
                             │ diagnostic settings
                             ▼
                 Log Analytics Workspace
                             ▲
                             │ metrics query + log shipping
                  scale_vmss.py  (Azure SDK)
                             │
                  Azure Monitor autoscale_setting
                  (native rules, same thresholds)
```

## Repository structure

```
azure-vmss-autoscale/
├── terraform/
│   ├── providers.tf              # provider + remote state backend config
│   ├── variables.tf              # all input variables
│   ├── main.tf                   # VMSS, NSG, LB, identity, RBAC, monitoring, autoscale
│   ├── outputs.tf                # IDs, public IP, workspace key, etc.
│   └── terraform.tfvars.example  # copy to terraform.tfvars and fill in
├── scripts/
│   ├── scale_vmss.py              # CPU-based scaler using the Azure SDK
│   └── requirements.txt
├── pipelines/
│   └── azure-pipelines.yml       # Azure DevOps pipeline, sourced from GitHub
├── bootstrap/
│   └── bootstrap-backend.sh      # one-time script to create the tfstate storage
└── README.md
```

## Prerequisites

- An Azure subscription, with permission to create resources and role assignments.
- The Azure CLI installed locally (`az`), logged in (`az login`), for the one-time bootstrap step.
- An Azure DevOps organization and project.
- This code pushed to a GitHub repository.
- An SSH key pair for logging in to the VMs (`ssh-keygen -t rsa -b 4096`).

---

## Step 1 — Push this repo to GitHub

Create a GitHub repository and push the `azure-vmss-autoscale` folder contents to it (the Terraform, scripts, and pipeline files at minimum need to be there — Azure DevOps will read `pipelines/azure-pipelines.yml` directly from GitHub).

## Step 2 — One-time Azure setup

**2a. Create the Terraform remote state storage** (run once, locally):

```bash
az login
cd azure-vmss-autoscale/bootstrap
chmod +x bootstrap-backend.sh
./bootstrap-backend.sh
```

Note the `backend_resource_group`, `backend_storage_account`, `backend_container`, and `backend_key` values it prints — you'll enter these into a variable group in Step 2c.

**2b. Create an Azure Resource Manager service connection in Azure DevOps**

In your Azure DevOps project: **Project Settings → Service connections → New service connection → Azure Resource Manager → Service principal (automatic)**. Scope it to the subscription you're deploying into, and name it `azure-vmss-service-connection` (matching the pipeline YAML — change both if you use a different name).

This creates a service principal behind the scenes. Grant it:
- **Contributor** on the subscription or target resource group (to create resources).
- **User Access Administrator** (or equivalent) if you want it to also create the role assignment for the scaler — only needed if you set `scaler_principal_id` in Terraform.

Get its object ID for later:
```bash
az ad sp list --display-name "<service-connection-name>" --query "[0].id" -o tsv
```

**2c. Create variable groups**

In Azure DevOps: **Pipelines → Library → + Variable group**.

Group `tfstate-backend`:
| Variable | Value |
|---|---|
| `backend_resource_group` | from bootstrap output |
| `backend_storage_account` | from bootstrap output |
| `backend_container` | from bootstrap output |
| `backend_key` | `vmss-autoscale.tfstate` |

Group `vmss-config`:
| Variable | Value |
|---|---|
| `admin_source_cidr` | your IP in CIDR form, e.g. `203.0.113.10/32` |
| `admin_ssh_public_key` | contents of your `.pub` key |
| `scaler_principal_id` | object ID from step 2b (or leave blank) |
| `app_resource_group` | `rg-vmss-autoscale` (must match `terraform/variables.tf`) |
| `vmss_name` | `vmss-app` (must match `terraform/variables.tf`) |

Mark `admin_ssh_public_key` as secret if your org policy requires it (it's not sensitive on its own, but keeping it out of logs is good hygiene).

**2d. Create an environment with an approval gate**

**Pipelines → Environments → New environment**, name it `vmss-production` (matches the YAML). Add an **Approvals** check so a human signs off before `terraform apply` runs against real infrastructure.

**2e. Install the Terraform extension**

From the Azure DevOps Marketplace, install **"Terraform" by Microsoft DevLabs** into your organization — it provides the `TerraformInstaller` and `TerraformTaskV4` tasks the pipeline uses.

## Step 3 — Create the pipeline from GitHub

In Azure DevOps: **Pipelines → New pipeline → GitHub → (authorize if prompted) → select your repository → Existing Azure Pipelines YAML file → `/pipelines/azure-pipelines.yml`**. Save (don't run yet if you still need to finish Step 2).

## Step 4 — Run the pipeline

Push to your `main` branch, or trigger the pipeline manually. It runs in stages:

1. **ValidateAndPlan** — `terraform init`, `validate`, `plan`. Review the plan output in the pipeline logs.
2. **Apply** — waits for your approval on the `vmss-production` environment, then runs `terraform apply`.
3. **RunScaler** — installs Python dependencies and runs `scale_vmss.py` once.

## Step 5 — Verify the deployment

```bash
az vmss list --resource-group rg-vmss-autoscale -o table
az network public-ip show --resource-group rg-vmss-autoscale --name pip-vmss-app-lb --query ipAddress -o tsv
```

Open the printed IP in a browser — you should see the default nginx page from each instance's bootstrap script. You can also read these same values from the pipeline's Terraform output, or with `terraform output` locally.

Check that diagnostic data is flowing into Log Analytics:
```bash
az monitor log-analytics workspace show --resource-group rg-vmss-autoscale --workspace-name log-vmss-app
```
Then in the Azure Portal, open the workspace and run a query like `AzureMetrics | take 20` under **Logs**.

## Step 6 — Run scale_vmss.py outside the pipeline (optional)

For local testing:

```bash
cd scripts
pip install -r requirements.txt
az login

python scale_vmss.py \
  --subscription-id <your-subscription-id> \
  --resource-group rg-vmss-autoscale \
  --vmss-name vmss-app \
  --scale-up-threshold 70 \
  --scale-down-threshold 25 \
  --min-instances 2 \
  --max-instances 6
```

`DefaultAzureCredential` will use your `az login` session automatically.

### Scheduling it continuously

The `RunScaler` pipeline stage runs the script once per pipeline run. For continuous scaling decisions, pick one:
- **Cron on a VM**: add a cron entry calling the script every 1–5 minutes.
- **Azure Automation Runbook**: schedule the script as a Python runbook using its managed identity.
- **Azure Function (Timer trigger)**: deploy the script as a timer-triggered function for a serverless, scheduled run.
- **Scheduled Azure DevOps pipeline**: duplicate the `RunScaler` stage into its own pipeline with a `schedules:` trigger (e.g. every 5 minutes), though Azure DevOps' minimum useful schedule granularity makes this better suited to less frequent checks.

In production, the native `azurerm_monitor_autoscale_setting` rules in `main.tf` already provide continuous, low-latency autoscaling without any of this — treat `scale_vmss.py` as the place to add logic those rules can't express (custom metrics, external signals, your own audit log), not as the primary scaler.

## Step 7 — Test autoscaling end to end

SSH into an instance (via the load balancer's NAT, a bastion, or by temporarily assigning a public IP) and generate CPU load:

```bash
sudo apt-get install -y stress-ng
stress-ng --cpu 2 --timeout 600s
```

Watch the scale set respond:
```bash
watch -n 30 "az vmss show --resource-group rg-vmss-autoscale --name vmss-app --query sku.capacity -o tsv"
```

You should see capacity increase within a few minutes (driven by the native autoscale rule, and/or by `scale_vmss.py` if you've scheduled it), and decrease again a few minutes after load stops.

## Step 8 — Tear down

```bash
cd terraform
terraform destroy \
  -var="admin_source_cidr=203.0.113.10/32" \
  -var="admin_ssh_public_key=$(cat ~/.ssh/id_rsa.pub)"
```

Then remove the bootstrap state storage if you no longer need it:
```bash
az group delete --name rg-tfstate --yes --no-wait
```

## Troubleshooting

- **`terraform init` fails with a backend auth error**: confirm the service connection has at least `Storage Blob Data Contributor` on the state storage account, or that `backendServiceArm` in the pipeline matches the connection name exactly.
- **VMSS instances unreachable on port 80**: check the NSG rule priorities (lower number = evaluated first) and confirm the LB health probe is passing (`az network lb probe list`).
- **`scale_vmss.py` raises a 403/Authorization error**: the identity it's running as needs the `Virtual Machine Contributor` role on the resource group — set `scaler_principal_id` in Terraform, or assign the role manually with `az role assignment create`.
- **No data points from `get_average_cpu`**: diagnostic settings can take a few minutes to start flowing after `terraform apply`; also confirm the scale set has been running long enough to emit a "Percentage CPU" metric over the lookback window.
