# setup.ps1 - iHIS Project Setup Script for Windows PowerShell

Write-Host "=== Setting up iHIS Project Structure ===" -ForegroundColor Green
Write-Host ""

# 1. Create directory structure
Write-Host "Creating directory structure..." -ForegroundColor Yellow

$directories = @(
    'backend\app\models',
    'backend\app\routes\api',
    'backend\app\services\ai',
    'backend\app\utils',
    'backend\app\templates\email',
    'backend\migrations',
    'backend\tests',
    'frontend\public\css',
    'frontend\public\js',
    'frontend\public\assets\images',
    'frontend\pages\auth',
    'frontend\pages\dashboard',
    'frontend\pages\patients',
    'frontend\pages\doctors',
    'frontend\pages\emr',
    'frontend\pages\appointments',
    'frontend\pages\laboratory',
    'frontend\pages\radiology',
    'frontend\pages\pharmacy',
    'frontend\pages\nursing',
    'frontend\pages\dental',
    'frontend\pages\physiotherapy',
    'frontend\pages\admin',
    'frontend\pages\reception',
    'frontend\pages\reports'
)

foreach ($dir in $directories) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    Write-Host "  Created: $dir" -ForegroundColor Gray
}

Write-Host "Directories created successfully!" -ForegroundColor Green
Write-Host ""

# 2. Create initial files
Write-Host "Creating initial files..." -ForegroundColor Yellow

$files = @(
    'backend\app\__init__.py',
    'backend\app\extensions.py',
    'backend\config.py',
    'backend\run.py',
    'backend\requirements.txt',
    'backend\.env.example',
    'backend\Dockerfile',
    'frontend\public\index.html',
    'frontend\public\css\style.css',
    'frontend\public\js\app.js',
    'frontend\README.md',
    '.gitignore',
    'docker-compose.yml',
    'README.md'
)

foreach ($file in $files) {
    New-Item -ItemType File -Force -Path $file | Out-Null
    Write-Host "  Created: $file" -ForegroundColor Gray
}

Write-Host "Files created successfully!" -ForegroundColor Green
Write-Host ""

# 3. Create .gitkeep files in empty directories
Write-Host "Creating .gitkeep files..." -ForegroundColor Yellow

$gitkeepDirs = @(
    'backend\app\models',
    'backend\app\routes\api',
    'backend\app\services\ai',
    'backend\app\utils',
    'backend\app\templates\email',
    'frontend\public\assets\images',
    'frontend\pages\auth',
    'frontend\pages\dashboard',
    'frontend\pages\patients',
    'frontend\pages\doctors',
    'frontend\pages\emr',
    'frontend\pages\appointments',
    'frontend\pages\laboratory',
    'frontend\pages\radiology',
    'frontend\pages\pharmacy',
    'frontend\pages\nursing',
    'frontend\pages\dental',
    'frontend\pages\physiotherapy',
    'frontend\pages\admin',
    'frontend\pages\reception',
    'frontend\pages\reports'
)

foreach ($dir in $gitkeepDirs) {
    $gitkeepPath = Join-Path $dir '.gitkeep'
    New-Item -ItemType File -Force -Path $gitkeepPath | Out-Null
}

Write-Host ".gitkeep files created!" -ForegroundColor Green
Write-Host ""

Write-Host "=== Setup Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Run: python -m venv venv" -ForegroundColor White
Write-Host "2. Run: .\venv\Scripts\activate" -ForegroundColor White
Write-Host "3. Run: pip install -r backend\requirements.txt" -ForegroundColor White
Write-Host "4. Start adding code to the files!" -ForegroundColor White

# Show the structure
Write-Host ""
Write-Host "Project Structure:" -ForegroundColor Yellow
Get-ChildItem -Directory -Recurse | Select-Object FullName