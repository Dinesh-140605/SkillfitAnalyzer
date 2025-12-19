# Deployment Helper Script

Write-Host "🚀 SkillFit Analyzer - Deployment Helper" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is initialized
if (-not (Test-Path ".git")) {
    Write-Host "❌ Git repository not found!" -ForegroundColor Red
    Write-Host "Please initialize git first: git init" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Git repository found" -ForegroundColor Green
Write-Host ""

# Check for uncommitted changes
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "📝 Uncommitted changes detected:" -ForegroundColor Yellow
    git status --short
    Write-Host ""
    
    $commit = Read-Host "Would you like to commit these changes? (y/n)"
    if ($commit -eq "y") {
        $message = Read-Host "Enter commit message"
        git add .
        git commit -m "$message"
        Write-Host "✅ Changes committed" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "📋 Deployment Checklist:" -ForegroundColor Cyan
Write-Host "1. ✅ Configuration files created (render.yaml, vercel.json, netlify.toml)" -ForegroundColor Green
Write-Host "2. ✅ API configuration created (src/config/api.ts)" -ForegroundColor Green
Write-Host "3. ✅ Documentation created (DEPLOYMENT_GUIDE.md)" -ForegroundColor Green
Write-Host ""

Write-Host "⚠️  Next Steps:" -ForegroundColor Yellow
Write-Host "1. Update your component files to use the API config" -ForegroundColor White
Write-Host "2. Push changes to GitHub: git push origin main" -ForegroundColor White
Write-Host "3. Follow the deployment guide in DEPLOYMENT_README.md" -ForegroundColor White
Write-Host ""

Write-Host "🎯 Recommended Deployment:" -ForegroundColor Cyan
Write-Host "   Frontend: Vercel (https://vercel.com)" -ForegroundColor White
Write-Host "   Backend:  Render (https://render.com)" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Would you like to push to GitHub now? (y/n)"
if ($choice -eq "y") {
    Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
    git push origin main
    Write-Host "✅ Pushed to GitHub successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎉 You're ready to deploy!" -ForegroundColor Green
    Write-Host "Open DEPLOYMENT_README.md for next steps" -ForegroundColor Cyan
} else {
    Write-Host "Remember to push to GitHub before deploying!" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📚 Documentation Files:" -ForegroundColor Cyan
Write-Host "   - DEPLOYMENT_README.md (Start here!)" -ForegroundColor White
Write-Host "   - DEPLOYMENT_GUIDE.md (Detailed guide)" -ForegroundColor White
Write-Host "   - DEPLOYMENT_CHECKLIST.md (Step-by-step)" -ForegroundColor White
Write-Host ""
