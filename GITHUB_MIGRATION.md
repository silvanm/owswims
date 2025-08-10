# GitHub Migration Guide

This guide helps migrate the OWSwims project from GitLab to GitHub while maintaining GCP deployment.

## Prerequisites

- GitHub account with repository creation permissions
- Google Cloud Platform project with existing OWSwims deployment
- Kubernetes cluster and Container Registry already configured
- Local git repository with all commits

## Step 1: Create GitHub Repository

1. Create a new repository on GitHub:
   ```
   Repository name: owswims
   Description: Open Water Swimming Events Map - Discover swimming events worldwide
   Visibility: Private (or Public if desired)
   ```

2. **Do not** initialize with README, .gitignore, or license (we'll push existing code)

## Step 2: Update Git Remotes

```bash
# Add GitHub as new remote
git remote add github https://github.com/YOUR_USERNAME/owswims.git

# Optionally rename existing GitLab remote
git remote rename origin gitlab

# Verify remotes
git remote -v
```

## Step 3: Configure GitHub Secrets

In your GitHub repository, go to Settings > Secrets and Variables > Actions and add:

### Required Secrets
- `GCP_PROJECT_ID`: Your Google Cloud project ID
- `GCLOUD_SERVICE_KEY`: Base64-encoded GCP service account JSON key
- `GCP_REGION`: Your GCP region (e.g., "europe-west1")
- `K8S_CLUSTER`: Your Kubernetes cluster name

### Application Secrets
- `SECRET_KEY`: Django secret key
- `GOOGLE_MAPS_API_KEY`: Google Maps API key
- `RAPIDAPI_KEY`: RapidAPI key (if used)
- `SENTRY_DSN`: Sentry error tracking DSN

### Optional Secrets
- `FIRECRAWL_API_KEY`: For web scraping functionality
- `OPENAI_API_KEY`: For LLM-based event processing

## Step 4: Push Code to GitHub

```bash
# Push all branches to GitHub
git push github --all

# Push all tags
git push github --tags

# Set GitHub as default upstream (optional)
git branch --set-upstream-to=github/master master
```

## Step 5: Test GitHub Actions

1. Make a small change to trigger the workflow:
   ```bash
   echo "# Migrated to GitHub" >> README_GITHUB.md
   git add README_GITHUB.md
   git commit -m "Test GitHub Actions workflow"
   git push github master
   ```

2. Check Actions tab in GitHub to verify the workflow runs successfully

## Step 6: Verify Deployment

After the GitHub Action completes:

1. Check that the Docker image was pushed to GCR:
   ```bash
   gcloud container images list --repository=europe-docker.pkg.dev/YOUR_PROJECT/owswims-repo
   ```

2. Verify Kubernetes deployment:
   ```bash
   kubectl get pods -n owswims
   kubectl get services -n owswims
   ```

3. Test the application endpoint

## Step 7: Update Documentation

Update any references to GitLab in:
- README.md
- Documentation files
- Issue templates
- Contributing guidelines

## Step 8: Archive GitLab Repository (Optional)

1. Archive the GitLab repository to prevent accidental pushes
2. Update any external systems pointing to GitLab URLs
3. Inform team members about the migration

## Troubleshooting

### Common Issues

**GitHub Actions failing with authentication errors:**
- Verify `GCLOUD_SERVICE_KEY` is properly base64-encoded
- Ensure the service account has necessary permissions

**Docker build failures:**
- Check that all required build arguments are provided as secrets
- Verify Dockerfile builds locally

**Deployment failures:**
- Ensure Kubernetes cluster is accessible
- Verify Helm charts in `helm/` directory are valid
- Check namespace exists: `kubectl create namespace owswims`

### Service Account Permissions

Your GCP service account needs these roles:
- Container Registry Service Agent
- Kubernetes Engine Developer
- Cloud Run Developer (if using Cloud Run)
- Storage Admin (for file uploads)

## Manual Deployment

If GitHub Actions are not working, you can deploy manually:

```bash
# GitHub-optimized deployment
./deploy-github.sh

# Original deployment method (still works)
./deploy.sh
```

## Rollback Plan

If you need to rollback to GitLab:

1. Re-enable GitLab CI/CD pipelines
2. Update git remote back to GitLab:
   ```bash
   git remote set-url origin https://gitlab.com/YOUR_USERNAME/owswims.git
   ```
3. Push latest changes to GitLab

## Post-Migration Checklist

- [ ] GitHub repository created and configured
- [ ] All secrets configured in GitHub
- [ ] Code pushed to GitHub successfully
- [ ] GitHub Actions workflow running successfully
- [ ] Application deploys and functions correctly
- [ ] Team members have access to GitHub repository
- [ ] Documentation updated
- [ ] GitLab repository archived
- [ ] External integrations updated to point to GitHub