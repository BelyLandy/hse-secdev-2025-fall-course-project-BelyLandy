# P12 - Hardening Summary

## Dockerfile hardening
- Базовый образ зафиксирован (без :latest, используется фиксированный tag/digest).
- Multi-stage build: сборка wheels отдельно, runtime-образ меньше.
- Запуск от non-root пользователя (app), корректные права (chown для /app и /data).
- Снижение поверхности атаки:
  - pip install --no-cache-dir
  - очистка build artifacts.

## IaC hardening
- Не используется default namespace:
  - добавлен Namespace idea-backlog;
  - проставлен metadata.namespace для всех ресурсов.
- Добавлен ServiceAccount с automountServiceAccountToken: false.
- Безопасность Pod/Container:
  - runAsNonRoot: true, фиксированный UID/GID, seccompProfile: RuntimeDefault
  - allowPrivilegeEscalation: false
  - readOnlyRootFilesystem: true, emptyDir для /tmp
  - capabilities.drop: ["ALL"]
  - заданы resources.requests/limits
  - добавлены liveness/readiness probes
- Сеть:
  - Service = ClusterIP.
  - Добавлен NetworkPolicy для ограничения ingress/egress.

- Конфигурация:
  - добавлен ConfigMap idea-backlog-config и подключён через env vars (APP_ENV, LOG_LEVEL, FEATURE_FLAGS);
  - секреты подключены через secretKeyRef (DATABASE_URL из idea-backlog-secrets).
    - Манифест Secret намеренно не хранится в репозитории (создаётся внешне: kubectl/helm/vault).

## Reports
- Hadolint: EVIDENCE/P12/hadolint_report.json
- Checkov: EVIDENCE/P12/checkov_report.json (после фиксов: `failed = 0`)
- Trivy: EVIDENCE/P12/trivy_report.json
  - High/Critical: 0/0
  - Пример фикса: обновлён filelock, чтобы убрать CVE-2025-68146
  - Оставшиеся Medium OS CVE отслеживаются. Стратегия - обновление base image digest, rebuild, регулярный re-scan в CI (weekly schedule).
