# PatchPanda Gateway

Houses the GitHub App and public API.

* What this does
    * Verifies webhooks (issue comments, PR events)
    * Enforces repo/team authorization
    * Loads .testbot.yml + server-side config
    * Exchanges installation tokens
    * Enqueues “generate tests” jobs for the worker
* This also exposes minimal REST endpoints for coverage ingestion and dashboard data
    * ... posts status/comments back to PRs
    * ... records audit events
* Guardrails
    * No code generation happens here
    * This service is the control plane.


```text
patchpanda-gateway/
├─ gateway/
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
