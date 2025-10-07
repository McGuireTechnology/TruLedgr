# Contributing & CI/CD Setup

This document explains the CI/CD secrets and repository settings required for automated deployments.

## Required GitHub Secrets (Repository)
- `DO_API_TOKEN` - DigitalOcean API token (used for doctl and DOCR login)
- `DOCR_REGISTRY` - Your DigitalOcean Container Registry namespace
- `DO_APP_ID` - App Platform app id (optional, for updating the app spec)
- `SPACES_KEY` & `SPACES_SECRET` - DigitalOcean Spaces S3 access keys for static site uploads
- `SPACES_REGION` - Example: `nyc3`
- `SPACES_BUCKET` - Bucket name for static website hosting
- `CODECOV_TOKEN` - (optional) Codecov upload token

## Branch protection
Protect `main` and `staging` branches with required status checks and at least 1 approver. Enable CODEOWNERS enforcement if desired.

## Notes
- The `.do/app-spec.yml` file is an example app spec for DigitalOcean App Platform. Customize before using `doctl apps create` or `doctl apps update`.
- Mobile release flows (App Store / Play Store) require additional secrets (Apple API key, Google Play service account). Add them to GitHub secrets when ready.

### Dependency changes and lockfile

- When changing `pyproject.toml`, always regenerate `poetry.lock` locally (run `poetry lock`) and commit the updated `poetry.lock` alongside your `pyproject.toml` change.
- The repository includes a pre-commit hook that will run `poetry lock` automatically and fail if `poetry.lock` was modified but not staged. CI also runs `poetry lock --check` early in the pipeline to prevent long runs with an out-of-date lockfile.

## Branching and naming

Use a predictable branch naming scheme so intent is clear and CI/PR rules can be applied consistently.

Recommended patterns:

- `feature/<ticket>-short-description` — for new features or non-urgent work (target `staging`).
- `hotfix/<ticket>-short-description` — for urgent fixes that must go to `main` immediately (create from `main`, then merge back to `staging`).
- `bugfix/<ticket>-short-description` — for non-urgent bug fixes (target `staging`).
- `chore/<short>` — for maintenance tasks, CI, docs, tooling.
- `release/<version>` — optional, for release preparation.

Naming rules:

- Use lowercase and hyphens to separate words.
- Include a ticket or issue ID when available: `feature/ABC-123-add-login`.
- Keep names short but descriptive.

Typical flow:

- Create feature branches from `staging` (or `main` if your team prefers). Example:
	```bash
	git checkout staging
	git pull origin staging
	git checkout -b feature/TICKET-short-desc
	```
- Push and open a PR targeting `staging` for feature/bugfix branches. For hotfixes, target `main` and then merge `main` -> `staging` afterwards.
- Use squash merges for feature branches to keep history tidy, or your team's preferred merge strategy.

CI & branch protection suggestions:

- Require status checks (pre-commit, tests, lockfile check) for `main` and `staging` branch protection rules.
- Optionally configure workflows to run different jobs or faster checks for `hotfix/*` branches.

If you'd like, I can add these conventions as a short checklist/template in PR descriptions or add automation to guard branch names in CI.
