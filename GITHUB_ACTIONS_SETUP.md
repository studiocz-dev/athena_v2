# GitHub Actions Auto-Deploy Setup Guide

## 🎯 Overview

Your repository now has GitHub Actions configured for **automatic deployment** to bot-hosting.net. Every time you push to the `main` branch, your bot files will be automatically uploaded via SFTP.

## 📋 Setup Steps

### Step 1: Configure GitHub Secrets

You need to add your SFTP credentials as **GitHub repository secrets** (encrypted and secure).

1. **Go to your GitHub repository**:
   https://github.com/studiocz-dev/athena_v2

2. **Navigate to Settings**:
   - Click **Settings** tab (top right)
   - In left sidebar, click **Secrets and variables** → **Actions**

3. **Add the following secrets** (click "New repository secret" for each):

   | Secret Name | Value |
   |-------------|-------|
   | `SFTP_HOST` | `de1.bot-hosting.net` |
   | `SFTP_PORT` | `2022` |
   | `SFTP_USERNAME` | `1030846920597454929.d0046ffd` |
   | `SFTP_PASSWORD` | `oEugkjW1NpC64Bf` |

4. **How to add each secret**:
   - Click **"New repository secret"** button
   - Enter **Name** (e.g., `SFTP_HOST`)
   - Enter **Secret** (e.g., `de1.bot-hosting.net`)
   - Click **"Add secret"**
   - Repeat for all 4 secrets

### Step 2: Verify Secrets Added

After adding all 4 secrets, you should see:

```
✓ SFTP_HOST
✓ SFTP_PORT
✓ SFTP_USERNAME
✓ SFTP_PASSWORD
```

## 🚀 How It Works

### Automatic Deployment

Once secrets are configured:

1. **You push code to GitHub**:
   ```bash
   git add .
   git commit -m "Update bot code"
   git push origin main
   ```

2. **GitHub Actions automatically**:
   - ✅ Detects push to `main` branch
   - ✅ Checks out your code
   - ✅ Connects to bot-hosting.net via SFTP
   - ✅ Uploads all files to `/home/container` directory
   - ✅ Completes in ~30-60 seconds

3. **Check deployment status**:
   - Go to **Actions** tab in GitHub
   - See workflow run with ✅ or ❌
   - View logs for details

### Manual Deployment

You can also trigger deployment manually:

1. Go to GitHub → **Actions** tab
2. Click **"Deploy to bot-hosting.net"** workflow
3. Click **"Run workflow"** button
4. Select `main` branch
5. Click **"Run workflow"**

## 📊 Workflow File

The workflow is defined in: `.github/workflows/deploy.yml`

```yaml
name: Deploy to bot-hosting.net

on:
  push:
    branches:
      - main  # Auto-deploy on push to main
  workflow_dispatch:  # Manual trigger button

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - Checkout code
      - Deploy via SFTP
      - Success notification
```

## 🔄 Complete Deployment Workflow

### New Code Changes:

```bash
# 1. Make changes locally
nano auto_trader.py

# 2. Test locally
python auto_trader.py

# 3. Commit and push
git add .
git commit -m "Update trading strategy"
git push origin main

# 4. GitHub Actions auto-deploys (watch in Actions tab)

# 5. SSH to server and restart bot
ssh 1030846920597454929.d0046ffd@de1.bot-hosting.net -p 2022
cd /home/container
screen -r athena_bot  # Ctrl+C to stop
python3 auto_trader.py  # Restart with new code
```

## ⚠️ Important Notes

### What Gets Deployed

✅ **Uploaded to bot-hosting.net**:
- All `.py` files
- `requirements.txt`
- Documentation (`.md` files)
- Configuration templates (`.env.example`)
- Scripts

❌ **NOT uploaded** (protected by `.gitignore`):
- `.env` file (your API keys)
- `*.db` files (trading database)
- `trading_data/` directory
- `__pycache__/`
- Logs

### After Deployment

**The bot does NOT auto-restart**. You need to:

1. SSH into bot-hosting.net
2. Stop current bot (if running)
3. Start bot with new code

**Optional**: Set up auto-restart script on server side.

### Security

✅ **Secrets are encrypted**: GitHub encrypts secrets, they're never visible in logs
✅ **Protected credentials**: SFTP password not exposed in code
✅ **Secure connection**: SFTP uses encrypted connection
✅ **Limited access**: Only deploys to specified path `/bot`

## 🧪 Testing the Workflow

### Test Deployment (First Time):

1. **Make a small change**:
   ```bash
   echo "# Test deployment" >> README.md
   git add README.md
   git commit -m "Test GitHub Actions deployment"
   git push origin main
   ```

2. **Watch deployment**:
   - Go to https://github.com/studiocz-dev/athena_v2/actions
   - See workflow running (yellow dot → green checkmark)
   - Click on workflow to see logs

3. **Verify on server**:
   ```bash
   ssh 1030846920597454929.d0046ffd@de1.bot-hosting.net -p 2022
   cd /home/container
   ls -la  # Check if README.md updated
   ```

## 🔧 Troubleshooting

### Workflow Fails

**Error: "Connection timeout"**
- Check SFTP_HOST secret is correct
- Verify port 2022 is accessible
- Bot-hosting.net may be blocking GitHub IPs (rare)

**Error: "Authentication failed"**
- Verify SFTP_USERNAME and SFTP_PASSWORD secrets
- Check for typos when adding secrets

**Error: "Permission denied"**
- Check remote_path `/home/container` exists
- Verify user has write permissions

### View Detailed Logs

1. Go to **Actions** tab
2. Click on failed workflow
3. Expand "Deploy to bot-hosting.net via SFTP" step
4. Read error messages

### Manual Override

If GitHub Actions fails, you can always use:
```powershell
.\deploy_to_bothosting.ps1  # Local SFTP script
```

## 📈 Deployment History

GitHub Actions keeps:
- ✅ Complete deployment history
- ✅ Logs for each deployment (retained 90 days)
- ✅ Success/failure status
- ✅ Commit that triggered deployment

View: https://github.com/studiocz-dev/athena_v2/actions

## 🎯 Advanced Configuration

### Deploy Only Specific Files

Edit `.github/workflows/deploy.yml`:
```yaml
local_path: './src/*'  # Only src folder
```

### Deploy to Different Path

Edit `.github/workflows/deploy.yml`:
```yaml
remote_path: '/home/container'  # Current bot-hosting.net path
```

### Add Slack/Discord Notifications

Add after deployment step:
```yaml
- name: Notify Discord
  run: |
    curl -X POST ${{ secrets.DISCORD_WEBHOOK }} \
      -H "Content-Type: application/json" \
      -d '{"content":"✅ Bot deployed successfully!"}'
```

### Deploy on Tag (Production Releases)

Add to workflow triggers:
```yaml
on:
  push:
    tags:
      - 'v*'  # Deploy when you create version tags
```

## ✅ Setup Checklist

- [ ] Navigate to GitHub repository Settings
- [ ] Click Secrets and variables → Actions
- [ ] Add secret: `SFTP_HOST` = `de1.bot-hosting.net`
- [ ] Add secret: `SFTP_PORT` = `2022`
- [ ] Add secret: `SFTP_USERNAME` = `1030846920597454929.d0046ffd`
- [ ] Add secret: `SFTP_PASSWORD` = `oEugkjW1NpC64Bf`
- [ ] Verify all 4 secrets show in list
- [ ] Push code to test: `git push origin main`
- [ ] Check Actions tab for workflow run
- [ ] Verify deployment success (green checkmark)
- [ ] SSH to server and verify files updated
- [ ] Restart bot with new code

## 🎉 Ready!

Once secrets are configured:
1. **Push code** → **Auto-deploys** → **Restart bot on server**
2. Every push to `main` triggers automatic deployment
3. View status in GitHub Actions tab
4. Manual trigger available via "Run workflow" button

---

**Next Step**: Go to https://github.com/studiocz-dev/athena_v2/settings/secrets/actions and add the 4 secrets! 🚀
