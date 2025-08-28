# PatchPanda Gateway Runbook

This runbook contains operational procedures for the PatchPanda Gateway service, including secrets management, incident response, and maintenance tasks.

## Table of Contents

- [Secrets Management](#secrets-management)
- [Incident Response](#incident-response)
- [Maintenance Procedures](#maintenance-procedures)
- [Troubleshooting](#troubleshooting)

## Secrets Management

### Overview

The PatchPanda Gateway uses Google Cloud Platform (GCP) Secret Manager with Cloud KMS encryption for secure secrets storage. All secrets are encrypted at rest using customer-managed encryption keys (CMEK).

### Current Secrets

- **GitHub App Private Key**: RSA private key for JWT generation
- **Webhook Secret**: Secret for verifying GitHub webhook payloads
- **OIDC Client Secret**: OAuth2 client secret for authentication (if enabled)

### Secrets Rotation Procedures

#### 1. GitHub App Private Key Rotation

**When to rotate**:
- Annually (recommended)
- When compromised
- When GitHub App is regenerated
- When service account changes

**Prerequisites**:
- Access to GCP project `patchpanda-1`
- Service account with Secret Manager Admin role
- New GitHub App private key from GitHub

**Procedure**:

```bash
# 1. Generate new private key in GitHub App settings
# Go to: https://github.com/settings/apps/[YOUR_APP_NAME]/private-key
# Download the new .pem file

# 2. Create new secret version in GCP
cat /path/to/new-private-key.pem | \
gcloud secrets versions add patchpanda-github-private-key \
    --data-file=-

# 3. Verify the new secret is accessible
gcloud secrets versions access latest \
    --secret="patchpanda-github-private-key"

# 4. Test the application with new key
# Restart the gateway service to pick up the new secret
# Monitor logs for any authentication errors

# 5. After successful deployment, mark old version for deletion
gcloud secrets versions destroy [OLD_VERSION_NUMBER] \
    --secret="patchpanda-github-private-key"
```

**Rollback procedure**:
```bash
# If issues occur, restore the previous version
gcloud secrets versions access [PREVIOUS_VERSION_NUMBER] \
    --secret="patchpanda-github-private-key" | \
gcloud secrets versions add patchpanda-github-private-key \
    --data-file=-
```

#### 2. Webhook Secret Rotation

**When to rotate**:
- Annually (recommended)
- When compromised
- When GitHub App webhook URL changes
- When service account changes

**Prerequisites**:
- Access to GCP project `patchpanda-1`
- Service account with Secret Manager Admin role
- New webhook secret (can be generated)

**Procedure**:

```bash
# 1. Generate new webhook secret
# Option A: Use openssl to generate random secret
openssl rand -hex 32

# Option B: Use Python to generate random secret
python3 -c "import secrets; print(secrets.token_hex(32))"

# 2. Update the secret in GCP
echo "NEW_WEBHOOK_SECRET_HERE" | \
gcloud secrets versions add patchpanda-webhook-secret \
    --data-file=-

# 3. Update GitHub App webhook settings
# Go to: https://github.com/settings/apps/[YOUR_APP_NAME]/webhook
# Update the webhook secret with the new value

# 4. Verify the new secret is accessible
gcloud secrets versions access latest \
    --secret="patchpanda-webhook-secret"

# 5. Test webhook delivery
# Send a test webhook from GitHub and verify it's processed correctly

# 6. After successful verification, mark old version for deletion
gcloud secrets versions destroy [OLD_VERSION_NUMBER] \
    --secret="patchpanda-webhook-secret"
```

**Rollback procedure**:
```bash
# If webhook verification fails, restore the previous version
gcloud secrets versions access [PREVIOUS_VERSION_NUMBER] \
    --secret="patchpanda-webhook-secret" | \
gcloud secrets versions add patchpanda-webhook-secret \
    --data-file=-

# Also restore the previous webhook secret in GitHub App settings
```

#### 3. Service Account Key Rotation (if using key-based auth)

**When to rotate**:
- Every 90 days (GCP recommendation)
- When compromised
- When service account permissions change

**Prerequisites**:
- Access to GCP project `patchpanda-1`
- Service account with IAM Admin role

**Procedure**:

```bash
# 1. Create new service account key
gcloud iam service-accounts keys create \
    /tmp/new-key.json \
    --iam-account=patchpanda-gateway-sa@patchpanda-1.iam.gserviceaccount.com

# 2. Update the application configuration
# Place the new key in the secure location
# Update GCP_SERVICE_ACCOUNT_KEY_PATH if needed

# 3. Test the application with new key
# Restart the gateway service
# Monitor logs for authentication errors

# 4. After successful deployment, delete the old key
gcloud iam service-accounts keys delete [OLD_KEY_ID] \
    --iam-account=patchpanda-gateway-sa@patchpanda-1.iam.gserviceaccount.com

# 5. Clean up temporary files
rm /tmp/new-key.json
```

**Note**: Service account key rotation is not required if using service account impersonation or default credentials.

#### 4. Cloud KMS Key Rotation

**When to rotate**:
- Annually (recommended)
- When compliance requirements mandate
- When key is compromised

**Prerequisites**:
- Access to GCP project `patchpanda-1`
- Service account with Cloud KMS Admin role

**Procedure**:

```bash
# 1. Create new crypto key version
gcloud kms keys versions create \
    --keyring=patchpanda-keys \
    --key=patchpanda-crypto-key \
    --location=us-central1

# 2. Set the new version as primary
gcloud kms keys set-primary-version \
    --keyring=patchpanda-keys \
    --key=patchpanda-crypto-key \
    --location=us-central1 \
    --version=[NEW_VERSION_NUMBER]

# 3. Test encryption/decryption with new key
# The application will automatically use the primary version

# 4. After successful testing, destroy old versions (optional)
gcloud kms keys versions destroy [OLD_VERSION_NUMBER] \
    --keyring=patchpanda-keys \
    --key=patchpanda-crypto-key \
    --location=us-central1
```

### Secrets Monitoring and Alerting

#### Cloud Monitoring Setup

```bash
# Enable Cloud Monitoring API
gcloud services enable monitoring.googleapis.com

# Create notification channels for secrets access
gcloud alpha monitoring channels create \
    --display-name="Secrets Access Alerts" \
    --type="email" \
    --channel-labels="email_address=admin@patchpanda.com"
```

#### Log-based Metrics

Monitor these metrics for unusual activity:
- Secret access frequency
- Failed authentication attempts
- KMS encryption/decryption operations
- Service account key usage

### Emergency Procedures

#### Immediate Secret Compromise Response

1. **Isolate the affected system**
   - Stop the gateway service
   - Block network access if necessary

2. **Rotate compromised secrets immediately**
   - Follow the rotation procedures above
   - Use emergency rotation procedures if needed

3. **Investigate the compromise**
   - Review Cloud Audit Logs
   - Check for unauthorized access
   - Identify the source of compromise

4. **Notify stakeholders**
   - Security team
   - Development team
   - Management

5. **Document the incident**
   - Timeline of events
   - Actions taken
   - Lessons learned

#### Emergency Rotation Procedures

```bash
# Emergency GitHub App private key rotation
# 1. Generate new key in GitHub immediately
# 2. Update GCP secret
echo "EMERGENCY_NEW_PRIVATE_KEY" | \
gcloud secrets versions add patchpanda-github-private-key \
    --data-file=-

# 3. Restart service
# 4. Verify functionality
# 5. Follow up with proper rotation procedure
```

## Incident Response

### Severity Levels

- **P0 (Critical)**: Service completely down, security breach
- **P1 (High)**: Major functionality broken, performance severely degraded
- **P2 (Medium)**: Minor functionality broken, performance impacted
- **P3 (Low)**: Cosmetic issues, minor bugs

### Response Procedures

#### P0/P1 Incidents

1. **Immediate Response** (within 15 minutes)
   - Acknowledge the incident
   - Assess impact and scope
   - Implement immediate mitigation if possible

2. **Escalation** (within 30 minutes)
   - Notify on-call engineer
   - Notify team lead
   - Create incident ticket

3. **Resolution** (ongoing)
   - Work on permanent fix
   - Provide status updates every hour
   - Document all actions taken

#### P2/P3 Incidents

1. **Response** (within 2 hours)
   - Acknowledge the incident
   - Assess impact
   - Create incident ticket

2. **Resolution** (within 24 hours)
   - Implement fix
   - Test thoroughly
   - Deploy to production

### Post-Incident Review

1. **Incident Summary**
   - What happened
   - When it happened
   - How it was resolved

2. **Root Cause Analysis**
   - Why it happened
   - Contributing factors
   - Systemic issues

3. **Action Items**
   - Immediate fixes
   - Long-term improvements
   - Process changes

4. **Lessons Learned**
   - What worked well
   - What could be improved
   - Training needs

## Maintenance Procedures

### Regular Maintenance Schedule

- **Daily**: Monitor logs and metrics
- **Weekly**: Review security alerts and performance metrics
- **Monthly**: Review and update runbook procedures
- **Quarterly**: Conduct security review and access audit
- **Annually**: Full security assessment and penetration testing

### Health Checks

#### Application Health

```bash
# Check application status
curl -f http://localhost:8000/health

# Check database connectivity
poetry run python -c "
from patchpanda.gateway.db.base import get_db
import asyncio

async def check_db():
    try:
        db = get_db()
        await db.execute('SELECT 1')
        print('Database: OK')
    except Exception as e:
        print(f'Database: ERROR - {e}')

asyncio.run(check_db())
"
```

#### GCP Resources Health

```bash
# Check secrets accessibility
gcloud secrets versions access latest \
    --secret="patchpanda-github-private-key"

# Check KMS key status
gcloud kms keys list \
    --keyring=patchpanda-keys \
    --location=us-central1

# Check service account permissions
gcloud projects get-iam-policy patchpanda-1 \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:patchpanda-gateway-sa@patchpanda-1.iam.gserviceaccount.com"
```

### Backup and Recovery

#### Secrets Backup

```bash
# Export all secrets (for disaster recovery)
mkdir -p /tmp/secrets-backup-$(date +%Y%m%d)

# Export GitHub private key
gcloud secrets versions access latest \
    --secret="patchpanda-github-private-key" > \
    /tmp/secrets-backup-$(date +%Y%m%d)/github-private-key.pem

# Export webhook secret
gcloud secrets versions access latest \
    --secret="patchpanda-webhook-secret" > \
    /tmp/secrets-backup-$(date +%Y%m%d)/webhook-secret.txt

# Export OIDC secret (if exists)
gcloud secrets versions access latest \
    --secret="patchpanda-oidc-client-secret" > \
    /tmp/secrets-backup-$(date +%Y%m%d)/oidc-secret.txt 2>/dev/null || echo "OIDC secret not found"

# Archive and encrypt the backup
tar -czf /tmp/secrets-backup-$(date +%Y%m%d).tar.gz \
    /tmp/secrets-backup-$(date +%Y%m%d)

# Clean up temporary files
rm -rf /tmp/secrets-backup-$(date +%Y%m%d)

echo "Backup created: /tmp/secrets-backup-$(date +%Y%m%d).tar.gz"
echo "⚠️  Store this backup securely and delete after 30 days"
```

#### Recovery Procedures

```bash
# Restore secrets from backup
tar -xzf /tmp/secrets-backup-YYYYMMDD.tar.gz

# Restore GitHub private key
cat /tmp/secrets-backup-YYYYMMDD/github-private-key.pem | \
gcloud secrets versions add patchpanda-github-private-key \
    --data-file=-

# Restore webhook secret
cat /tmp/secrets-backup-YYYYMMDD/webhook-secret.txt | \
gcloud secrets versions add patchpanda-webhook-secret \
    --data-file=-

# Restore OIDC secret (if exists)
if [ -f "/tmp/secrets-backup-YYYYMMDD/oidc-secret.txt" ]; then
    cat /tmp/secrets-backup-YYYYMMDD/oidc-secret.txt | \
    gcloud secrets versions add patchpanda-oidc-client-secret \
        --data-file=-
fi

# Clean up
rm -rf /tmp/secrets-backup-YYYYMMDD
```

## Troubleshooting

### Common Issues

#### Authentication Errors

**Symptoms**: 401/403 errors, "permission denied" messages

**Diagnosis**:
```bash
# Check service account permissions
gcloud projects get-iam-policy patchpanda-1 \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:patchpanda-gateway-sa@patchpanda-1.iam.gserviceaccount.com"

# Check if service account can access secrets
gcloud auth list
gcloud secrets list
```

**Solutions**:
- Verify service account has correct IAM roles
- Check if using correct project
- Verify service account key is valid (if using key-based auth)

#### Secret Access Issues

**Symptoms**: "Secret not found" errors, empty secret values

**Diagnosis**:
```bash
# Check if secret exists
gcloud secrets list --filter="name:patchpanda"

# Check secret versions
gcloud secrets versions list patchpanda-github-private-key

# Test secret access
gcloud secrets versions access latest \
    --secret="patchpanda-github-private-key"
```

**Solutions**:
- Verify secret names are correct
- Check if secret has versions
- Verify service account has Secret Manager access

#### KMS Issues

**Symptoms**: Encryption/decryption failures, "key not found" errors

**Diagnosis**:
```bash
# Check KMS key status
gcloud kms keys list \
    --keyring=patchpanda-keys \
    --location=us-central1

# Check key versions
gcloud kms keys versions list \
    --keyring=patchpanda-keys \
    --key=patchpanda-crypto-key \
    --location=us-central1
```

**Solutions**:
- Verify key exists and is enabled
- Check if key has versions
- Verify service account has KMS permissions

### Debug Mode

Enable debug logging for troubleshooting:

```bash
# Set debug mode in environment
export DEBUG=true

# Or update .env file
echo "DEBUG=true" >> .env

# Restart the service
# Check logs for detailed error messages
```

### Getting Help

1. **Check logs first**: Look for error messages and stack traces
2. **Review this runbook**: Check relevant procedures
3. **Check GCP documentation**: [Secret Manager](https://cloud.google.com/secret-manager/docs), [Cloud KMS](https://cloud.google.com/kms/docs)
4. **Contact the team**: Create an issue or reach out to the development team
5. **Escalate if needed**: For critical issues, escalate to senior team members

---

**Last Updated**: $(date +%Y-%m-%d)
**Maintained By**: PatchPanda Gateway Team
**Review Schedule**: Monthly
