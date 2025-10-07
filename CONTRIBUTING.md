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
