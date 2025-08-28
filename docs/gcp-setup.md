# Google Cloud Platform Setup Guide

This guide will help you set up Google Cloud Platform integration for PatchPanda Gateway, including Secret Manager and Cloud KMS for secure secrets management.

**Note**: This setup uses the shared "PatchPanda" GCP project (`patchpanda-1`) which is used for all PatchPanda-related services, not just the gateway.

## Prerequisites

- Google Cloud Platform account
- Google Cloud CLI (`gcloud`) installed and configured
- Python 3.12+ with Poetry for dependency management

## 1. Project Setup

### Use the existing PatchPanda project

```bash
# Set the existing PatchPanda project as default
gcloud config set project patchpanda-1

# Verify the project is set correctly
gcloud config get-value project

# Enable billing (required for Secret Manager and KMS)
# Visit: https://console.cloud.google.com/billing
```

**Important**: This project (`patchpanda-1`) is shared across all PatchPanda services. When creating resources like service accounts, keyrings, or secrets, use descriptive names that won't conflict with other services.

### Enable required APIs

```bash
# Enable Secret Manager API
gcloud services enable secretmanager.googleapis.com

# Enable Cloud KMS API
gcloud services enable cloudkms.googleapis.com

# Enable Cloud Resource Manager API
gcloud services enable cloudresourcemanager.googleapis.com
```

### Check for existing resources

Since this is a shared project, check if resources already exist before creating new ones:

```bash
# Check for existing keyrings
gcloud kms keyrings list --location=us-central1

# Check for existing secrets
gcloud secrets list

# Check for existing service accounts
gcloud iam service-accounts list
```

### Set up .gitignore (if using service account keys)

If you need to use service account keys for local development, add them to .gitignore:

```bash
# Add to .gitignore
echo "$(gcloud info --format='value(config.paths.global_config_dir)')/keys/" >> .gitignore
echo "*.json" >> .gitignore
```

## 2. Service Account Setup

### Create a service account for the application

```bash
# Create service account (using a more generic name since this is shared)
gcloud iam service-accounts create patchpanda-gateway-sa \
    --display-name="PatchPanda Gateway Service Account"

# Get the service account email
SA_EMAIL=$(gcloud iam service-accounts list \
    --filter="displayName:PatchPanda Gateway Service Account" \
    --format="value(email)")

echo "Service Account Email: $SA_EMAIL"
```

**Naming Convention**: Since this is a shared project, we use the prefix `patchpanda-gateway-` for resources specific to this service to avoid conflicts with other PatchPanda services.

### Grant necessary permissions

```bash
# Grant Secret Manager Admin role
gcloud projects add-iam-policy-binding patchpanda-1 \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/secretmanager.admin"

# Grant Cloud KMS Admin role
gcloud projects add-iam-policy-binding patchpanda-1 \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/cloudkms.admin"

# Grant Cloud KMS CryptoKey Encrypter/Decrypter role
gcloud projects add-iam-policy-binding patchpanda-1 \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/cloudkms.cryptoKeyEncrypterDecrypter"
```

### Grant impersonation permissions

To use service account impersonation, your user account needs the `Service Account Token Creator` role:

```bash
# Get your current user email
USER_EMAIL=$(gcloud config get-value account)

# Grant the Service Account Token Creator role to your user
gcloud projects add-iam-policy-binding patchpanda-1 \
    --member="user:$USER_EMAIL" \
    --role="roles/iam.serviceAccountTokenCreator"
```

### Option 1: Use Service Account Impersonation (Recommended - Keyless)

For local development, use service account impersonation instead of downloading keys:

```bash
# Set up impersonation for the service account
gcloud config set auth/impersonate_service_account \
    patchpanda-gateway-sa@patchpanda-1.iam.gserviceaccount.com

# Verify impersonation is working
gcloud auth list
gcloud config get-value project

# Test access to the project
gcloud projects describe patchpanda-1
```

**Benefits**: No keys downloaded, no files to manage, automatic credential rotation, more secure.

### Option 2: Use Application Default Credentials (Production)

For production deployments, the platform automatically provides credentials:

```bash
# For Cloud Run, GKE, or Compute Engine, the service account will automatically
# use default credentials without needing to download keys

# Verify the service account can access the project
gcloud auth list
gcloud config get-value project
```

### Option 3: Download service account key (Last Resort Only)

**⚠️ Security Warning**: Only use this if impersonation doesn't work. Never commit service account keys to version control.

```bash
KEYS_PATH=$(gcloud info --format='value(config.paths.global_config_dir)')/keys
mkdir -p $KEYS_PATH

# Create service account key
gcloud iam service-accounts keys create \
    $KEYS_PATH/patchpanda-gateway-sa-key.json \
    --iam-account=$SA_EMAIL

echo "Service account key saved to: $KEYS_PATH/patchpanda-gateway-sa-key.json"
echo "⚠️  Remember to add this path to .gitignore!"
```

## 3. Cloud KMS Setup

### Create a keyring and crypto key

```bash
# Set your preferred location (e.g., us-central1, us-east1, europe-west1)
LOCATION="us-central1"

# Create keyring (if it doesn't already exist)
gcloud kms keyrings create patchpanda-keys \
    --location=$LOCATION

# Create crypto key (if it doesn't already exist)
gcloud kms keys create patchpanda-crypto-key \
    --keyring=patchpanda-keys \
    --location=$LOCATION \
    --purpose=encryption \
    --protection-level=software

# Verify the key was created
gcloud kms keys list \
    --keyring=patchpanda-keys \
    --location=$LOCATION
```

## 4. Secret Manager Setup

### Create secrets for your GitHub App

```bash
# GitHub App Private Key (Required)
# This is the RSA private key from your GitHub App settings
echo "-----BEGIN RSA PRIVATE KEY-----" | \
gcloud secrets create patchpanda-github-private-key \
    --data-file=- \
    --replication-policy="automatic"

# GitHub Webhook Secret (Required)
# This is the webhook secret you set when creating the GitHub App
echo "your-webhook-secret-here" | \
gcloud secrets create patchpanda-webhook-secret \
    --data-file=- \
    --replication-policy="automatic"
```

**Note**: If these secrets already exist in the shared project, you can skip this step and proceed to updating them with your actual values.

### Optional: Additional secrets (if needed)

```bash
# OIDC Client Secret (only if using OIDC for authentication)
echo "your-oidc-client-secret-here" | \
gcloud secrets create patchpanda-oidc-client-secret \
    --data-file=- \
    --replication-policy="automatic"

# Application Secret Key (only if your app needs a general-purpose secret)
echo "your-application-secret-key-here" | \
gcloud secrets create patchpanda-secret-key \
    --data-file=- \
    --replication-policy="automatic"
```

### Update existing secrets (if needed)

```bash
# Update GitHub App Private Key
echo "-----BEGIN RSA PRIVATE KEY-----" | \
gcloud secrets versions add patchpanda-github-private-key \
    --data-file=-

# Update other secrets as needed
echo "new-secret-value" | \
gcloud secrets versions add patchpanda-webhook-secret \
    --data-file=-
```

## 5. Environment Configuration

### Update your `.env` file

```bash
# Copy the example environment file
cp env.example .env

# Edit the file with your GCP configuration
nano .env
```

Add the following GCP configuration to your `.env` file:

```bash
# Google Cloud Platform
GCP_PROJECT_ID=patchpanda-1
GCP_REGION=us-central1
GCP_LOCATION=us-central1
GCP_KEY_RING=patchpanda-keys
GCP_CRYPTO_KEY=patchpanda-crypto-key
GCP_SECRETS_PREFIX=patchpanda

# Authentication (Choose one option):
# Option 1: Use default credentials (Recommended for production)
GCP_USE_DEFAULT_CREDENTIALS=true
# GCP_SERVICE_ACCOUNT_KEY_PATH=

# Option 2: Use service account impersonation (Local development - recommended)
# GCP_USE_DEFAULT_CREDENTIALS=true
# GCP_SERVICE_ACCOUNT_KEY_PATH=
# Note: Set up impersonation with: gcloud config set auth/impersonate_service_account

# Option 3: Use service account key file (Last resort only)
# GCP_USE_DEFAULT_CREDENTIALS=false
# GCP_SERVICE_ACCOUNT_KEY_PATH=/path/to/patchpanda-gateway-sa-key.json
```

### Configure authentication

```bash
# For production or local development with impersonation (keyless - recommended)
sed -i "s|GCP_USE_DEFAULT_CREDENTIALS=.*|GCP_USE_DEFAULT_CREDENTIALS=true|" .env
sed -i "s|GCP_SERVICE_ACCOUNT_KEY_PATH=.*|GCP_SERVICE_ACCOUNT_KEY_PATH=|" .env

# Set up service account impersonation for local development
gcloud config set auth/impersonate_service_account \
    patchpanda-gateway-sa@patchpanda-1.iam.gserviceaccount.com

# For local development with service account key (last resort only)
# sed -i "s|GCP_USE_DEFAULT_CREDENTIALS=.*|GCP_USE_DEFAULT_CREDENTIALS=false|" .env
# sed -i "s|GCP_SERVICE_ACCOUNT_KEY_PATH=.*|GCP_SERVICE_ACCOUNT_KEY_PATH=$HOME/patchpanda-gateway-sa-key.json|" .env

# Verify the project ID is set correctly
sed -i "s|GCP_PROJECT_ID=.*|GCP_PROJECT_ID=patchpanda-1|" .env
```

## 6. Local Development Setup

### Install dependencies

```bash
# Install the new GCP dependencies
poetry install
```

### Test the configuration

```bash
# Test GCP connectivity
poetry run python -c "
from patchpanda.gateway.security.secrets import SecretsManager
import asyncio

async def test_gcp():
    secrets = SecretsManager()
    private_key = await secrets.get_github_private_key()
    print(f'GitHub Private Key loaded: {bool(private_key)}')
    webhook_secret = await secrets.get_webhook_secret()
    print(f'Webhook Secret loaded: {bool(webhook_secret)}')

asyncio.run(test_gcp())
"
```

### Test service account impersonation

Verify that impersonation is working correctly:

```bash
# Test basic access
gcloud projects describe patchpanda-1

# Test Secret Manager access
gcloud secrets list

# Test KMS access
gcloud kms keyrings list --location=us-central1

# If using impersonation, you should see the service account in the output
gcloud auth list
```

## 7. Production Deployment

### For Cloud Run, GKE, or Compute Engine (Recommended)

1. **Use default credentials**: Set `GCP_USE_DEFAULT_CREDENTIALS=true` in production
2. **No service account keys**: The platform automatically provides credentials
3. **Grant IAM roles**: Ensure the service account running your application has the necessary permissions
4. **Workload Identity**: For GKE, consider setting up Workload Identity Federation for even better security

### For other cloud providers

1. **Service account key**: Place the service account key in a secure location (not in containers)
2. **Environment variables**: Set all GCP configuration via environment variables
3. **Secrets rotation**: Regularly rotate your service account keys
4. **Consider alternatives**: Look into using OAuth2 or other authentication methods if available

### Setting up Workload Identity Federation (GKE)

If using Google Kubernetes Engine, set up Workload Identity Federation for enhanced security:

```bash
# Enable Workload Identity on your cluster
gcloud container clusters update YOUR_CLUSTER_NAME \
    --workload-pool=patchpanda-1.svc.id.goog

# Bind the Kubernetes service account to the GCP service account
gcloud iam service-accounts add-iam-policy-binding \
    patchpanda-gateway-sa@patchpanda-1.iam.gserviceaccount.com \
    --role="roles/iam.workloadIdentityUser" \
    --member="serviceAccount:patchpanda-1.svc.id.goog[default/patchpanda-gateway]"
```

## 8. Migration from AWS

If you're migrating from AWS to GCP:

### 1. Export secrets from AWS

```bash
# Export secrets from AWS Secrets Manager
aws secretsmanager get-secret-value --secret-id github-app-private-key --query SecretString --output text > github-private-key.txt
aws secretsmanager get-secret-value --secret-id github-webhook-secret --query SecretString --output text > webhook-secret.txt
```

### 2. Import to GCP Secret Manager

```bash
# Import to GCP Secret Manager
cat github-private-key.txt | \
gcloud secrets create patchpanda-github-private-key \
    --data-file=- \
    --replication-policy="automatic"

cat webhook-secret.txt | \
gcloud secrets create patchpanda-webhook-secret \
    --data-file=- \
    --replication-policy="automatic"
```

**Note**: These are the only two secrets required for basic GitHub App functionality. The private key is used for JWT generation, and the webhook secret is used for verifying webhook payloads.

### 3. Update configuration

```bash
# Comment out AWS configuration in .env
# AWS_REGION=us-east-1
# AWS_ACCESS_KEY_ID=your_access_key_here
# AWS_SECRET_ACCESS_KEY=your_secret_key_here

# Enable GCP configuration
GCP_PROJECT_ID=patchpanda-1
GCP_USE_DEFAULT_CREDENTIALS=true
```

## 9. Troubleshooting

### Common issues and solutions

#### Authentication errors

```bash
# Verify service account permissions
gcloud projects get-iam-policy patchpanda-1 \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:$SA_EMAIL" \
    --format="table(bindings.role)"
```

#### Secret access issues

```bash
# Test secret access
gcloud secrets versions access latest --secret="patchpanda-github-private-key"
```

#### KMS permission issues

```bash
# Verify KMS permissions
gcloud kms keys list \
    --keyring=patchpanda-keys \
    --location=us-central1
```

### Debug mode

Enable debug logging by setting `DEBUG=true` in your `.env` file to see detailed error messages.

## 10. Security Best Practices

### Authentication Security

1. **Use service account impersonation for local development**: No keys needed, automatic rotation
2. **Use Workload Identity Federation in production**: Best security for GKE deployments
3. **Avoid downloading service account keys**: Only as a last resort if impersonation fails
4. **Never commit keys to version control**: Add service account key paths to `.gitignore`
5. **Use least privilege**: Only grant necessary IAM roles to service accounts and users

### General Security

1. **Principle of least privilege**: Only grant necessary permissions
2. **Audit logging**: Enable Cloud Audit Logs for monitoring
3. **Secret versioning**: Use secret versions for easy rollback
4. **Network security**: Restrict access using VPC Service Controls if needed
5. **Environment separation**: Use different service accounts for different environments

## 11. Cost Optimization

- **Secret Manager**: $0.06 per 10,000 API calls
- **Cloud KMS**: $0.03 per 10,000 API calls
- **Storage**: $0.06 per GB-month for secrets

Monitor usage in the Google Cloud Console and set up billing alerts.

## Support

For issues with this setup:

1. Check the [Google Cloud documentation](https://cloud.google.com/docs)
2. Review the [Secret Manager documentation](https://cloud.google.com/secret-manager/docs)
3. Review the [Cloud KMS documentation](https://cloud.google.com/kms/docs)
4. Check the PatchPanda Gateway logs for detailed error messages
