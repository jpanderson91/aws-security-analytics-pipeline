# GitHub Repository Setup Commands

# After creating the repository on GitHub, run these commands:

# Add the remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/aws-security-analytics-pipeline.git

# Verify the remote was added
git remote -v

# Push to GitHub
git branch -M main
git push -u origin main

# Your repository will then be available at:
# https://github.com/YOUR_USERNAME/aws-security-analytics-pipeline

# For future updates, simply use:
# git add .
# git commit -m "your commit message"
# git push
