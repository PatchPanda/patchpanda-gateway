# PatchPanda Gateway

Houses the GitHub App and public API.

* Verifies webhooks (issue comments, PR events)
* Enforces repo/team authorization
* Loads .testbot.yml + server-side config
* Exchanges installation tokens
* Enqueues “generate tests” jobs for the worker


* This also exposes minimal REST endpoints for coverage ingestion and dashboard data
* ... posts status/comments back to PRs
* ... records audit events


* No code generation happens here
* This service is the control plane.
