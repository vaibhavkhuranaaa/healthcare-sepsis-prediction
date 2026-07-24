#!/usr/bin/env bash
set -euo pipefail

# Synthetic-only Azure deployment. Never place MIMIC data or artifacts in this workspace command.
: "${APP_NAME:?Set a globally unique lowercase APP_NAME, e.g. sepsisewsdemo123}"
RESOURCE_GROUP="${RESOURCE_GROUP:-rg-${APP_NAME}}"
LOCATION="${LOCATION:-eastus2}"
IMAGE_TAG="${IMAGE_TAG:-demo-v1}"

az group create --name "$RESOURCE_GROUP" --location "$LOCATION"
az deployment group create --resource-group "$RESOURCE_GROUP" --name foundation \
  --template-file infra/foundation.bicep --parameters appName="$APP_NAME" location="$LOCATION"

REGISTRY_NAME="${APP_NAME}acr"
LOGIN_SERVER="$(az acr show --resource-group "$RESOURCE_GROUP" --name "$REGISTRY_NAME" --query loginServer -o tsv)"
az acr build --registry "$REGISTRY_NAME" --image "sepsis:${IMAGE_TAG}" --file docker/Dockerfile .

DEPLOYMENT="$(az deployment group create --resource-group "$RESOURCE_GROUP" --name app \
  --template-file infra/app.bicep \
  --parameters appName="$APP_NAME" location="$LOCATION" image="${LOGIN_SERVER}/sepsis:${IMAGE_TAG}" \
  environmentId="$(az containerapp env show --resource-group "$RESOURCE_GROUP" --name "${APP_NAME}-env" --query id -o tsv)" \
  registryServer="$LOGIN_SERVER" \
  appInsightsConnectionString="$(az monitor app-insights component show --resource-group "$RESOURCE_GROUP" --app "${APP_NAME}-insights" --query connectionString -o tsv)" \
  --query properties.outputs.appUrl.value -o tsv)"
echo "Deployed synthetic demo: ${DEPLOYMENT}"
