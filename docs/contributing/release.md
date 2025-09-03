# Release

## Purpose

This document describes the minimal, practical steps to prepare, create, verify, and roll back a release for the TruLedgr monorepo. Use this as the canonical checklist before tagging and publishing a release (for example: `v1.0.0`).

## Quick checklist (must complete before tagging)

- [ ] Decide release version and update any canonical version fields (see "Versioning" section).
- [ ] All tests passing: unit + integration across sub-projects.
- [ ] Lint/format checks pass for all code (Python: ruff/black; JS/TS: ESLint/Prettier; mobile linters).
- [ ] CI pipelines green (build/test/lint/security scans).
- [ ] Database migrations created and tested (and rollback tested).
- [ ] Dependency/security audits run and critical issues addressed.
- [ ] Documentation updated (CHANGELOG, README, API docs, upgrade notes).
- [ ] Build artifacts produced and validated (docker images, npm bundles, python wheels, mobile artifacts).
- [ ] Release notes drafted and reviewed.
- [ ] Smoke deploy to staging + acceptance tests passed.
- [ ] Rollback plan confirmed and stakeholders notified.

## Versioning

- Decide whether this release uses a repo-wide tag (recommended for single-app releases) or per-package releases (if you publish independent packages).
- Common places to update version strings:
  - `pyproject.toml` / Python package metadata
  - `package.json` (frontend or library packages)
  - iOS `Info.plist` / build settings
  - Android `build.gradle` (versionName / versionCode)

## Tagging and pushing the release (example)

Use annotated tags so CI and GitHub Releases get proper metadata.

```bash
# Ensure main is up-to-date
git checkout main
git pull origin main

# Create an annotated tag
git tag -a v1.0.0 -m "Release v1.0.0"

# Push tag to origin
git push origin v1.0.0
```

If you publish multiple packages independently, bump each package's version and follow its publish steps (npm publish, twine upload, etc.). Consider using tools like Changesets or Lerna for multi-package versioning.

## Run tests & quality gates

### API (Python)

```bash
cd api
python -m pytest
ruff check .
black --check .
```

### Web frontend

```bash
cd dash
npm ci
npm test
npm run build
npm run lint
```

### Docs

```bash
cd docs
pip install -r requirements.txt
mkdocs build
```

## Build artifacts

- Docker images: build and tag with the release tag, push to registry, and verify container start.
- Python package: build wheel / sdist and optionally upload to internal PyPI or PyPI (twine).
- Frontend: ensure production bundle is generated and versioned.
- Mobile: generate signed APK / IPA if releasing to stores or CI-managed distribution.

### Example Docker build & push

```bash
# from repo root
docker build -t myregistry/api:v1.0.0 -f api/Dockerfile api/
docker push myregistry/api:v1.0.0
```

## CHANGELOG / Release notes

- Generate a changelog from merged PRs or use Conventional Commit messages to auto-generate.

We follow the Keep a Changelog format (<https://keepachangelog.com/>) for structured, human-friendly changelogs. The main points:

- Use headings for each released version: Unreleased, v1.0.0, v0.9.0, etc.
- Group changes under: Added, Changed, Deprecated, Removed, Fixed, Security.
- Link issues and PRs where helpful.

At minimum a changelog entry should include:

- Highlights / new features
- Bug fixes
- Breaking changes and migration steps
- Database migration instructions
- Notable contributors

### Keep a Changelog example

Use the following template for `CHANGELOG.md` entries. Put a short entry in `CHANGELOG.md` and paste or generate the release notes from it when creating a GitHub Release.

```markdown
## [Unreleased]

### Added
- New OAuth provider support for Microsoft (`api`) (#123)

### Fixed
- Corrected session expiry handling in API (#130)

## [1.0.0] - 2025-09-01

### Added
- Initial stable release: API endpoints, web dashboard, mobile clients

### Security
- Rotate signing keys for session tokens (see migration notes)

```

When generating release notes for GitHub Releases, include the `Unreleased` -> `vX.Y.Z` summary, upgrade steps, and any migration commands (for example, Alembic commands).

## Smoke tests and verification

After publishing artifacts and deploying to staging or a canary environment, run a smoke test suite and these quick checks:

```bash
# Basic health-checks (example)
curl -fS https://staging.api.truledgr.com/health || echo "health check failed"
# Example API sanity test
python scripts/smoke_tests/run_quick_smoke.py --base-url https://staging.api.truledgr.com
```

## Rollback strategy

Keep steps documented and tested for rolling back in case of regression.

- To undo a pushed tag:

```bash
git push --delete origin v1.0.0
git tag -d v1.0.0
```

- To revert a release commit (if needed):

```bash
# Create a revert commit and push
git revert <release-commit-sha>
git push origin main
```

- For deployments, have a documented way to redeploy the previous image or artifact (container registry tags, versioned bucket artifacts, etc.).

## CI / Automation notes

- Ensure CI config understands tags (some pipelines trigger on tags to publish artifacts).
- Verify that required secrets for publishing (PyPI token, Docker registry credentials, App Store / Play Store credentials) exist in CI and are scoped correctly.
- If using GitHub Actions, protect `main` and require passing checks and PR reviews before merging.

## Monorepo considerations

- If a single release applies to the whole repo, the annotated git tag approach above is sufficient.
- If packages are versioned independently, use a release manager tool (Changesets, Lerna) and document per-package publish steps.
- Clearly state which sub-projects are included in the release in the release notes.

## Post-release tasks

- Create GitHub Release from the pushed tag and paste final release notes.
- Announce release on team channels and update any external docs or dashboards.
- Monitor logs and metrics for regressions; be prepared to roll back.
- Add contributors for this release to `CONTRIBUTORS.md`.

## Security & compliance

- Ensure license files are present in distributed artifacts.
- Run secret-scanning and SAST prior to release.
- Resolve or acknowledge any critical or high security findings before pushing the release.

## Contacts

- Release owner: @release-manager
- On-call/incident: @oncall
- CI/infra contact: @infra

## Appendix: example end-to-end minimal commands

```bash
# From repo root: run quick full checks
# API
cd api && python -m pytest && ruff check . && black --check . && cd -

# Frontend
cd dash && npm ci && npm test && npm run build && cd -

# Docs
cd docs && pip install -r requirements.txt && mkdocs build && cd -

# Tag and push
git checkout main
git pull origin main
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

If you want, I can:
- Create a GitHub Release draft from merged PRs (I can generate a changelog draft here).
- Add a `release` CI workflow that runs on tags and publishes artifacts.

---
Generated on: 2025-08-30
