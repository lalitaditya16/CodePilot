#!/bin/bash
# Quick deployment script for pushing to GitHub

echo "🚀 Deploying AI Python Code Generator to GitHub..."

# Check if we have uncommitted changes
if [[ -n $(git status --porcelain) ]]; then
    echo "📝 Adding new changes..."
    git add .
    
    echo "💬 Enter commit message (or press Enter for default):"
    read -r commit_message
    
    if [[ -z "$commit_message" ]]; then
        commit_message="Update: $(date '+%Y-%m-%d %H:%M:%S')"
    fi
    
    git commit -m "$commit_message"
fi

# Push to GitHub
echo "📤 Pushing to GitHub..."
git push origin main

echo "✅ Successfully deployed to GitHub!"
echo "🌐 View your repository at: https://github.com/YOUR_USERNAME/YOUR_REPO_NAME"