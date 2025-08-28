# PatchPanda Gateway

Houses the GitHub App and public API.

* What this does
    * Verifies webhooks (issue comments, PR events)
    * Enforces repo/team authorization
    * Loads .testbot.yml + server-side config
    * Exchanges installation tokens
    * Enqueues "generate tests" jobs for the worker
* This also exposes minimal REST endpoints for coverage ingestion and dashboard data
    * ... posts status/comments back to PRs
    * ... records audit events
* Guardrails
    * No code generation happens here
    * This service is the control plane.

## Cloud Provider Support

PatchPanda Gateway supports multiple cloud providers for secrets management and encryption:

### Google Cloud Platform (Recommended)
- **Secret Manager**: Secure storage for application secrets
- **Cloud KMS**: Encryption/decryption of sensitive data
- **Service Account**: Secure authentication without key files
- **Setup Guide**: See [GCP Setup Guide](docs/gcp-setup.md)

### Amazon Web Services
- **Secrets Manager**: Secure storage for application secrets
- **KMS**: Encryption/decryption of sensitive data
- **IAM**: Role-based access control

### Local Development
- Environment variables for development and testing
- Automatic fallback to local secrets when cloud services unavailable

## Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
poetry install

# Install GCP dependencies (if using GCP)
poetry install
```

### 2. Configure Environment

```bash
# Copy environment template
cp env.example .env

# Edit with your configuration
nano .env
```

### 3. Set Up Cloud Provider

#### For GCP (Recommended)
```bash
# Run the GCP setup script
python scripts/setup_gcp.py

# Follow the setup guide
docs/gcp-setup.md
```

#### For AWS
```bash
# Set AWS credentials in .env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
```

### 4. Run the Application

```bash
# Development mode
poetry run uvicorn patchpanda.gateway.main:app --reload

# Production mode
poetry run patchpanda-gateway
```

## Project Structure

```text
patchpanda-gateway/
├─ src/patchpanda/gateway/
│  ├─ api/                         # FastAPI routers
│  │  ├─ webhooks.py               # POST /webhooks/github (HMAC verify)
│  │  ├─ coverage.py               # POST /api/coverage, GET list/detail
│  │  ├─ jobs.py                   # GET/POST job metadata, replay
│  │  └─ admin.py                  # billing projects, keys (restricted)
│  ├─ services/
│  │  ├─ github_app.py             # JWT, installation tokens, GH REST calls
│  │  ├─ authz.py                  # RBAC (teams/users) + SSO session (OIDC)
│  │  ├─ config_loader.py          # fetch/parse .testbot.yml (repo@sha)
│  │  ├─ queue.py                  # enqueue to Redis/SQS (adapter)
│  │  └─ checks.py                 # create/update PR Check Runs & comments
│  ├─ models/                      # Pydantic v2 schemas (shared copies)
│  │  ├─ coverage.py
│  │  ├─ jobs.py
│  │  └─ config.py
│  ├─ db/
│  │  ├─ base.py                   # SQLAlchemy engine/session
│  │  ├─ tables.py                 # jobs, coverage, billing, bindings, audit
│  │  └─ migrations/               # Alembic
│  ├─ security/
│  │  ├─ secrets.py                # KMS/Secrets Manager wrappers
│  │  └─ signature.py              # webhook signature verify
│  ├─ settings.py                  # Pydantic Settings (env-driven)
│  └─ main.py                      # FastAPI app factory + router mount
├─ tests/                          # pytest (unit + router tests)
├─ alembic.ini
├─ pyproject.toml                  # fastapi, pydantic, httpx, sqlalchemy, alembic
├─ Makefile                        # run, test, lint, migrate
├─ Dockerfile
└─ README.md
```

**Notes**

* **Framework**: FastAPI + Uvicorn.
* **DB**: Postgres via SQLAlchemy + Alembic.
* **Queue**: small adapter with `QUEUE_BACKEND=redis|sqs`.
* **Auth**: OIDC (dashboard sessions) + GitHub team mapping for RBAC.
* **Secrets**: App private key + provider keys via cloud KMS/Secrets Manager.
