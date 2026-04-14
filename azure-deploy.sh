#!/bin/bash
# ============================================================
#  Azure Deployment Script — AI-Powered ATS
#  Deploys: Azure Container Registry + App Service + PostgreSQL
# ============================================================
set -euo pipefail

# ── Configuration (edit these) ──────────────────────────────
RESOURCE_GROUP="ats-capstone-rg"
LOCATION="eastus"
ACR_NAME="atscapstoneacr"           # must be globally unique, lowercase
APP_NAME="ai-ats-app"               # must be globally unique
DB_SERVER_NAME="ats-capstone-db"     # must be globally unique
DB_ADMIN_USER="atsadmin"
DB_ADMIN_PASSWORD=""                 # set via: export DB_ADMIN_PASSWORD=<your-password>
DB_NAME="ats_db"
APP_SERVICE_PLAN="ats-plan"
SKU="B2"                            # B2 = 2 vCPU, 3.5 GB (good for demo)

# ── Validate ────────────────────────────────────────────────
if [ -z "${DB_ADMIN_PASSWORD:-}" ]; then
  echo "ERROR: Set DB_ADMIN_PASSWORD first:"
  echo "  export DB_ADMIN_PASSWORD='YourStr0ng!Pass'"
  exit 1
fi

if [ -z "${GROQ_API_KEY:-}" ] && [ -z "${NVIDIA_API_KEY:-}" ]; then
  echo "WARNING: Neither GROQ_API_KEY nor NVIDIA_API_KEY is set."
  echo "  export GROQ_API_KEY=gsk_..."
  echo "  export NVIDIA_API_KEY=nvapi-..."
fi

echo "========================================="
echo "  Deploying AI-Powered ATS to Azure"
echo "========================================="

# ── 1. Resource Group ───────────────────────────────────────
echo "[1/7] Creating resource group..."
az group create --name "$RESOURCE_GROUP" --location "$LOCATION" --output none

# ── 2. Azure Container Registry ─────────────────────────────
echo "[2/7] Creating container registry..."
az acr create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$ACR_NAME" \
  --sku Basic \
  --admin-enabled true \
  --output none

# Build and push image
echo "       Building and pushing Docker image..."
az acr build \
  --registry "$ACR_NAME" \
  --image ats-app:latest \
  --file Dockerfile \
  . \
  --no-logs

# ── 3. PostgreSQL Flexible Server ────────────────────────────
echo "[3/7] Creating PostgreSQL server (with pgvector)..."
az postgres flexible-server create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$DB_SERVER_NAME" \
  --location "$LOCATION" \
  --admin-user "$DB_ADMIN_USER" \
  --admin-password "$DB_ADMIN_PASSWORD" \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --storage-size 32 \
  --version 16 \
  --yes \
  --output none

# Allow Azure services to connect
echo "       Configuring firewall..."
az postgres flexible-server firewall-rule create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$DB_SERVER_NAME" \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0 \
  --output none

# Create database
echo "       Creating database..."
az postgres flexible-server db create \
  --resource-group "$RESOURCE_GROUP" \
  --server-name "$DB_SERVER_NAME" \
  --database-name "$DB_NAME" \
  --output none

# Enable pgvector extension
echo "       Enabling pgvector extension..."
az postgres flexible-server parameter set \
  --resource-group "$RESOURCE_GROUP" \
  --server-name "$DB_SERVER_NAME" \
  --name azure.extensions \
  --value vector \
  --output none

# ── 4. App Service Plan ─────────────────────────────────────
echo "[4/7] Creating App Service plan..."
az appservice plan create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$APP_SERVICE_PLAN" \
  --sku "$SKU" \
  --is-linux \
  --output none

# ── 5. Web App (Container) ──────────────────────────────────
echo "[5/7] Creating web app..."
ACR_LOGIN_SERVER=$(az acr show --name "$ACR_NAME" --query loginServer -o tsv)
ACR_PASSWORD=$(az acr credential show --name "$ACR_NAME" --query "passwords[0].value" -o tsv)

az webapp create \
  --resource-group "$RESOURCE_GROUP" \
  --plan "$APP_SERVICE_PLAN" \
  --name "$APP_NAME" \
  --container-image-name "${ACR_LOGIN_SERVER}/ats-app:latest" \
  --container-registry-url "https://${ACR_LOGIN_SERVER}" \
  --container-registry-user "$ACR_NAME" \
  --container-registry-password "$ACR_PASSWORD" \
  --output none

# ── 6. Configure Environment Variables ──────────────────────
echo "[6/7] Setting environment variables..."
DB_HOST="${DB_SERVER_NAME}.postgres.database.azure.com"
DATABASE_URL="postgresql://${DB_ADMIN_USER}:${DB_ADMIN_PASSWORD}@${DB_HOST}:5432/${DB_NAME}?sslmode=require"

az webapp config appsettings set \
  --resource-group "$RESOURCE_GROUP" \
  --name "$APP_NAME" \
  --settings \
    DATABASE_URL="$DATABASE_URL" \
    GROQ_API_KEY="${GROQ_API_KEY:-}" \
    NVIDIA_API_KEY="${NVIDIA_API_KEY:-}" \
    NVIDIA_BASE_URL="https://integrate.api.nvidia.com/v1" \
    NVIDIA_MODEL="meta/llama-3.3-70b-instruct" \
    LLM_PROVIDER="${LLM_PROVIDER:-nvidia}" \
    LLM_MODEL="llama-3.3-70b-versatile" \
    EMBEDDING_MODEL="all-MiniLM-L6-v2" \
    WEBSITES_PORT=8000 \
    ALLOWED_ORIGINS="https://${APP_NAME}.azurewebsites.net" \
  --output none

# ── 7. Enable logging ───────────────────────────────────────
echo "[7/7] Enabling logs..."
az webapp log config \
  --resource-group "$RESOURCE_GROUP" \
  --name "$APP_NAME" \
  --docker-container-logging filesystem \
  --output none

# ── Done ─────────────────────────────────────────────────────
APP_URL="https://${APP_NAME}.azurewebsites.net"
echo ""
echo "========================================="
echo "  Deployment complete!"
echo "========================================="
echo "  App URL:  $APP_URL"
echo "  DB Host:  $DB_HOST"
echo "  ACR:      $ACR_LOGIN_SERVER"
echo ""
echo "  View logs:  az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"
echo "  Redeploy:   az acr build --registry $ACR_NAME --image ats-app:latest . && az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP"
echo "========================================="
