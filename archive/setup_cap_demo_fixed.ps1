# CAP Demo Project Setup Script
# Run this from the cap-data-ingestion-demo directory

Write-Host "🚀 Setting up CAP Data Ingestion Demo Project..." -ForegroundColor Green

# Create Python virtual environment
Write-Host "📦 Creating Python virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Copy configuration files from reference project
$sourceDir = "..\aws-security-analytics-pipeline"

Write-Host "📋 Copying VS Code configuration files..." -ForegroundColor Yellow

# Copy VS Code settings
Copy-Item "$sourceDir\cap-vscode-settings.json" ".vscode\settings.json"
Copy-Item "$sourceDir\cap-tasks.json" ".vscode\tasks.json"
Copy-Item "$sourceDir\cap-launch.json" ".vscode\launch.json"

# Copy requirements and test script
Copy-Item "$sourceDir\cap-requirements.txt" "requirements.txt"
Copy-Item "$sourceDir\test_cap_environment.py" "test_environment.py"

Write-Host "📚 Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Initialize git repository
Write-Host "📝 Initializing Git repository..." -ForegroundColor Yellow
git init
git add .
git commit -m "Initial CAP demo project setup"

Write-Host "✅ CAP Demo Project setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Test environment: python test_environment.py" -ForegroundColor White
Write-Host "2. Open workspace in VS Code: code cap-workspace.code-workspace" -ForegroundColor White
Write-Host "3. Begin with MSK Kafka cluster setup" -ForegroundColor White
