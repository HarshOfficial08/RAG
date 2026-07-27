# Code Quality & SonarQube

## Depends on
`09-testing-strategy.md` (coverage feeds into Sonar's metrics)

## Setup
- **SonarCloud** (hosted, free for a personal/public repo) is simpler to stand up than
  self-hosted SonarQube for a prototype timeline — use self-hosted only if the repo
  must stay private and you're fine running the Docker image yourself.
- One `sonar-project.properties` at repo root:
  ```properties
  sonar.projectKey=securerag
  sonar.sources=backend/app,frontend/src
  sonar.tests=backend/tests,frontend/src/**/*.test.tsx
  sonar.python.coverage.reportPaths=backend/coverage.xml
  sonar.javascript.lcov.reportPaths=frontend/coverage/lcov.info
  ```
- Run via CI (GitHub Actions `sonarsource/sonarqube-scan-action`) on every push to
  main, so the quality gate is enforced, not just checked manually before a demo.

## Linting/formatting (Sonar catches issues; these prevent most of them upfront)
- Backend: **Ruff** (lint + format, replaces flake8/isort/black in one tool) + **mypy**
  for type checking.
- Frontend: **ESLint** (typescript-eslint) + **Prettier**.
- Both wired as pre-commit hooks (`pre-commit` framework) so issues are caught before
  they ever reach Sonar/CI.

## DRY checklist to apply while building (not just what Sonar flags automatically)
- No duplicated tenant-filter construction — it lives in exactly one place
  (`vector_store.search`).
- No duplicated masking invocation logic across ingestion/retrieval/output paths — one
  `mask(text) -> MaskResult` function called from all three sites.
- No copy-pasted API-call boilerplate on the frontend — everything through the one
  `ApiClient`.
- Sonar's own duplication detector (`sonar.cpd.*`) will flag copy-pasted blocks >10
  lines automatically — treat any hit here as something to extract, not suppress.

## Quality gate (what to actually set, proportionate to a prototype)
- 0 new blocker/critical issues on new code.
- No new code duplication above ~3%.
- Coverage on `masking/` and `retrieval/vector_store.py` specifically (not just an
  overall average) — these are the modules where a regression matters most.

## Definition of done
- SonarCloud dashboard is green (or has a documented, deliberate reason for any
  open item) at the point you'd demo this in the interview.
