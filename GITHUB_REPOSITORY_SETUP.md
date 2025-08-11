# GitHub Repository Setup Instructions

This document outlines the manual GitHub repository configurations needed to complete the DevOps improvements implemented in the GitHub Actions workflow.

## 🔧 Required Repository Settings

### 1. Create Production Environment

**Location**: Repository Settings > Environments

1. Navigate to your repository settings
2. Click **Environments** in the left sidebar
3. Click **New environment**
4. Name: `production`
5. Configure environment settings:
   - **Environment protection rules**: 
     - ✅ Required reviewers (optional, for extra security)
     - ✅ Wait timer: 0 minutes
   - **Environment secrets**: Will be configured in next step

### 2. Move Variables to Environment Level

**Current Issue**: Variables are currently stored as repository-level secrets/variables
**Solution**: Move non-sensitive configuration to environment variables

**In Repository Settings > Environments > production > Environment variables:**

Add these variables:
```
GRAPHQL_ENDPOINT=/graphql
DEFAULT_HEADER_PHOTO_URL=https://storage.googleapis.com/owswims-prod/photos/default-image.jpg
KUBE_NAMESPACE=mupo-shared
```

**Why**: Environment variables provide better organization and deployment tracking

### 3. Keep Secrets at Repository Level

**Location**: Repository Settings > Secrets and variables > Actions > Secrets

Keep these as **repository secrets** (they're sensitive):
- `GCLOUD_SERVICE_KEY` - GCP service account JSON
- `GCP_PROJECT_ID` - Google Cloud project ID  
- `GCP_REGION` - GCP region (e.g., europe-west1)
- `K8S_CLUSTER` - Kubernetes cluster name
- `GOOGLE_MAPS_API_KEY` - Google Maps API key
- `SECRET_KEY` - Django secret key
- `SENTRY_DSN` - Sentry error tracking DSN
- `RAPIDAPI_KEY` - RapidAPI key (if used)

### 4. Configure Branch Protection Rules

**Location**: Repository Settings > Branches

1. Click **Add rule**
2. **Branch name pattern**: `master`
3. Configure protection settings:
   - ✅ **Require a pull request before merging**
     - ✅ Require approvals: 1
     - ✅ Dismiss stale PR approvals when new commits are pushed
   - ✅ **Require status checks to pass before merging**
     - ✅ Require branches to be up to date before merging
     - Add status checks: `build` (will appear after first workflow run)
   - ✅ **Require conversation resolution before merging**
   - ✅ **Include administrators** (recommended)

**Why**: Prevents direct pushes to master, ensures code review process

## 🔄 Migration Steps

### Step 1: Environment Variables Migration

**Before** (Repository Variables):
```yaml
env:
  GRAPHQL_ENDPOINT: /graphql
  DEFAULT_HEADER_PHOTO_URL: https://...
  KUBE_NAMESPACE: mupo-shared
```

**After** (Environment Variables):
```yaml
jobs:
  build:
    environment: production
    # Variables accessed as ${{ vars.VARIABLE_NAME }}
```

### Step 2: Test the Setup

1. **Create the environment** and add variables
2. **Commit the updated workflow** (already done)
3. **Test with a small change**:
   ```bash
   git commit --allow-empty -m "Test improved DevOps workflow"
   git push origin master
   ```
4. **Monitor the Actions tab** for successful deployment
5. **Check the deployment summary** for improved visibility

## ✨ Benefits After Setup

### Improved Security
- ✅ Branch protection prevents accidental direct pushes
- ✅ Environment separation for better secrets management
- ✅ Required code reviews for all changes

### Better DevOps Practices
- ✅ Fixed Ubuntu version (ubuntu-24.04) for reproducible builds
- ✅ Proper SHA handling with 8-character short SHA
- ✅ Docker build action with caching for faster builds
- ✅ Job output parameters for reliable value passing
- ✅ Environment tracking for deployment visibility

### Enhanced Visibility
- ✅ GitHub Step Summary with build information
- ✅ Deployment details in workflow summaries
- ✅ Environment-specific deployment tracking

## 🚨 Important Notes

1. **Don't delete existing secrets** until environment is working
2. **Test thoroughly** before enabling branch protection on active development
3. **Inform team members** about the new code review requirements
4. **Monitor first few deployments** to ensure everything works correctly

## 🔮 Optional Future Improvements

Consider these additional improvements (not implemented yet):

1. **Workload Identity Federation**: Replace service account JSON with federated identity
2. **Slack/Teams Notifications**: Add deployment notifications
3. **Multi-environment Setup**: Create staging environment
4. **Automated Security Scanning**: Add container and code security scans

---

This setup follows enterprise DevOps best practices and provides a solid foundation for scaling your deployment pipeline.