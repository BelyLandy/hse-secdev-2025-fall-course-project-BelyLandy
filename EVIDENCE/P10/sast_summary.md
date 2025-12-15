# P10 SAST & Secrets summary (local triage)

- Commit: `7bc0654`

## Semgrep
- Total: 0
- By level: `{}`

## Gitleaks
- Total: 0
- Top rules: `[]`

## Notes
- Semgrep: профиль `p/ci` + кастом-правила `security/semgrep/rules.yml`.
- Gitleaks: конфиг `security/.gitleaks.toml`; фиктивный JWT в `tests/fixtures/dummy_jwt.txt` в allowlist точечно.
