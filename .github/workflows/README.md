# GitHub Actions Workflows

This directory contains CI/CD workflows for the Sidekick Medical Assistant project.

## Current Workflows

### ci.yml - Continuous Integration
**Triggers:** Pull requests and pushes to `develop` and `main` branches

**Jobs:**
1. **lint** - Code quality checks (flake8, black)
2. **backend-tests** - Backend Infrastructure tests
3. **ai-tests** - AI Integration tests
4. **frontend-tests** - Frontend validation
5. **integration-tests** - Cross-team integration tests

**Status:** ✅ Active

## Required Secrets

Set these in: **Settings → Secrets and variables → Actions**

| Secret Name | Description | Required For |
|-------------|-------------|--------------|
| `GEMINI_API_KEY_TEST` | Test API key for Gemini | AI tests |

## Branch Protection

### develop branch
- Require PR before merging
- Require 1 approval
- Require status checks: lint, backend-tests, ai-tests, frontend-tests, integration-tests

### main branch
- Require PR before merging
- Require 2 approvals
- Require status checks: lint, backend-tests, ai-tests, frontend-tests, integration-tests

## Adding New Workflows

When adding deployment workflows later:
1. Create new file: `deploy-staging.yml` or `deploy-prod.yml`
2. Add required secrets
3. Update this README

## Troubleshooting

### Tests failing?
1. Check the Actions tab for detailed logs
2. Run tests locally: `pytest tests/`
3. Ensure all dependencies are in requirements.txt

### Lint errors?
1. Run locally: `flake8 .`
2. Auto-fix: `black .`

### Cache issues?
1. Clear cache in Actions tab
2. Re-run workflow
