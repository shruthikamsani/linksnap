# LinkSnap Health Check Script
# Usage: .\scripts\health-check.ps1
# Usage: .\scripts\health-check.ps1 -Url "http://127.0.0.1:57984"

param(
    [string]$Url = "http://127.0.0.1:5000"
)

$HealthEndpoint = "$Url/health"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  LinkSnap Health Check" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Checking: $HealthEndpoint"
Write-Host "  Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

try {
    $Response = Invoke-WebRequest -Uri $HealthEndpoint -Method GET -TimeoutSec 10 -UseBasicParsing

    if ($Response.StatusCode -eq 200) {
        $Body = $Response.Content | ConvertFrom-Json
        Write-Host "  STATUS: HEALTHY" -ForegroundColor Green
        Write-Host "  Service: $($Body.service)"
        Write-Host "  Database: $($Body.database)"
        Write-Host ""
        exit 0
    }
} catch {
    Write-Host "  STATUS: UNHEALTHY" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)"
    Write-Host ""
    Write-Host "  Possible fixes:" -ForegroundColor Yellow
    Write-Host "  1. Is the app running? Run: py app.py"
    Write-Host "  2. Is Docker running? Run: docker ps"
    Write-Host "  3. Is Kubernetes running? Run: kubectl get pods"
    Write-Host ""
    exit 1
}