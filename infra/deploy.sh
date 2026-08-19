#!/usr/bin/env bash
set -euo pipefail

# Synthetic-only Azure deployment. Never place MIMIC data or artifacts in this workspace command.
: "${APP_NAME:?Set a globally unique lowercase APP_NAME, e.g. sepsisewsdemo123}"
: "${IMAGE:?Set a public container image, e.g. ghcr.io/owner/sepsis-demo:sha}"
: "${SOURCE_SHA:?Set the exact 40-character deployed source commit}"
RESOURCE_GROUP="${RESOURCE_GROUP:-rg-${APP_NAME}}"
LOCATION="${LOCATION:-eastus2}"

az group create --name "$RESOURCE_GROUP" --location "$LOCATION"
DEPLOYMENT="$(az deployment group create --resource-group "$RESOURCE_GROUP" --name demo \
  --template-file infra/main.bicep \
  --parameters appName="$APP_NAME" location="$LOCATION" image="$IMAGE" sourceSha="$SOURCE_SHA" \
  --query properties.outputs.appUrl.value -o tsv)"
echo "Deployed synthetic demo: ${DEPLOYMENT}"
