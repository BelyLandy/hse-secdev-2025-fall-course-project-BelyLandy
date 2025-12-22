# P12 Hardening Summary

## Dockerfile hardening
- Base image pinned (no `:latest`, uses pinned tag/digest).
- Multi-stage build (build wheels отдельно, runtime образ меньше).
- Runs as **non-root** user (`app`) with correct permissions (`chown` for /app and /data).
- Reduced attack surface: `pip install --no-cache-dir`, cleanup of build artifacts.

## IaC hardening
- Not using `default` namespace: added `Namespace idea-backlog` and set `metadata.namespace` everywhere.
- Added `ServiceAccount` with `automountServiceAccountToken: false`.
- Pod/container security:
  - `runAsNonRoot: true`, fixed UID/GID, `seccompProfile: RuntimeDefault`
  - `allowPrivilegeEscalation: false`
  - `readOnlyRootFilesystem: true` + `emptyDir` for `/tmp`
  - `capabilities.drop: ["ALL"]`
  - `resources.requests/limits` set
  - liveness/readiness probes added
- Networking:
  - Service is `ClusterIP` (not exposed to the world).
  - Added `NetworkPolicy` to restrict ingress/egress (min baseline policy).

- Added `ConfigMap idea-backlog-config` and wired it via env vars (`APP_ENV`, `LOG_LEVEL`, `FEATURE_FLAGS`).
- Added secret wiring via `secretKeyRef` (`DATABASE_URL` from `idea-backlog-secrets`).
  - Secret manifest is intentionally not stored in repo. Must be created externally (kubectl/helm/vault).

- Hadolint: `EVIDENCE/P12/hadolint_report.json`
- Checkov: `EVIDENCE/P12/checkov_report.json` (after fixes: `failed = 0`)
- Trivy: `EVIDENCE/P12/trivy_report.json`
  - High/Critical: 0/0
  - Example fix: updated `filelock` to remove `CVE-2025-68146`
  - Remaining medium OS CVEs tracked; mitigation is base image digest updates + rebuild + re-scan in CI.
