# Deployment Instructions

Follow these steps to deploy your CI Monitor to GitHub.

## Option A: Deploy from Command Line (Recommended)

### Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `snowflake-ci-monitor`
3. Make it **Private**
4. **DO NOT** check "Initialize with README" or any other boxes
5. Click **Create repository**

### Step 2: Run Deployment Commands

Open **Command Prompt** or **PowerShell** and run:

```cmd
cd "C:\Users\chenk\OneDrive\Desktop\Claude Code\competitive-intelligence"

git init
git add .
git commit -m "Initial CI Monitor setup"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/snowflake-ci-monitor.git
git push -u origin main
```

**Replace `YOUR_USERNAME` with your actual GitHub username!**

### Step 3: Configure GitHub Secrets

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Add these secrets:
   - `SENDGRID_API_KEY` = your SendGrid API key
   - `RECIPIENT_EMAIL` = chen.kelvin822@gmail.com

### Step 4: Enable GitHub Actions

1. Go to **Settings** → **Actions** → **General**
2. Under **Workflow permissions**:
   - Select **Read and write permissions**
   - Click **Save**

### Step 5: Test the Workflow

1. Go to **Actions** tab
2. Click **Daily Competitive Intelligence Monitor**
3. Click **Run workflow** → **Run workflow**
4. Wait 1-2 minutes
5. Check your email!

---

## Option B: Deploy with GitHub Desktop (Easier)

### Step 1: Install GitHub Desktop

1. Download from https://desktop.github.com/
2. Install and sign in with your GitHub account

### Step 2: Create Repository

1. In GitHub Desktop, click **File** → **New Repository**
2. Name: `snowflake-ci-monitor`
3. Local Path: Choose a location (NOT the competitive-intelligence folder)
4. Click **Create Repository**

### Step 3: Copy Files

1. Open File Explorer
2. Go to: `C:\Users\chenk\OneDrive\Desktop\Claude Code\competitive-intelligence`
3. Select ALL files and folders (Ctrl+A)
4. Copy them (Ctrl+C)
5. Go to your new repository folder (from Step 2)
6. Paste all files (Ctrl+V)

### Step 4: Publish to GitHub

1. In GitHub Desktop, you'll see all the new files
2. Add commit message: "Initial CI Monitor setup"
3. Click **Commit to main**
4. Click **Publish repository**
5. Make it **Private**
6. Click **Publish repository**

### Step 5: Configure GitHub (same as Option A Step 3-5)

---

## Option C: Use the GitHub Web Interface (No Git Required)

### Step 1: Create Repository on GitHub

1. Go to https://github.com/new
2. Name: `snowflake-ci-monitor`
3. Make it **Private**
4. **Check** "Initialize this repository with a README"
5. Click **Create repository**

### Step 2: Upload Files

1. In your repository, click **Add file** → **Upload files**
2. Open File Explorer to: `C:\Users\chenk\OneDrive\Desktop\Claude Code\competitive-intelligence`
3. Select ALL files and folders
4. Drag them to the GitHub upload area
5. Scroll down, add commit message: "Initial CI Monitor setup"
6. Click **Commit changes**

**Note**: You may need to upload in batches if there are too many files.

### Step 3: Configure GitHub (same as Option A Step 3-5)

---

## Troubleshooting

### Error: "remote origin already exists"

```cmd
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/snowflake-ci-monitor.git
```

### Error: "Authentication failed"

You need to use a Personal Access Token instead of password:

1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Click **Generate new token (classic)**
3. Give it a name: "CI Monitor Deploy"
4. Check: **repo** (all sub-options)
5. Click **Generate token**
6. Copy the token
7. When git asks for password, paste the token

### Error: "Permission denied"

Make sure you're using your correct GitHub username in the URL.

---

## Quick Reference

After deployment, here are the important URLs:

- **Your Repository**: https://github.com/YOUR_USERNAME/snowflake-ci-monitor
- **Actions Tab**: https://github.com/YOUR_USERNAME/snowflake-ci-monitor/actions
- **Settings**: https://github.com/YOUR_USERNAME/snowflake-ci-monitor/settings

---

## What's Next?

After successful deployment:

1. ✅ Workflow will run automatically at 8 AM ET daily
2. ✅ You'll receive email reports
3. ✅ Check Actions tab to monitor runs
4. ✅ Review [README.md](README.md) for customization options

Need help? Check [SETUP.md](SETUP.md) for detailed troubleshooting.
