# LinkSnap Log Collector
# Collects logs from all running LinkSnap pods
# Usage: .\scripts\get-logs.ps1

param(
    [int]$Lines = 50
)

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  LinkSnap Log Collector" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Get all linksnap pods
$Pods = kubectl get pods -l app=linksnap -o jsonpath='{.items[*].metadata.name}'

if (-not $Pods) {
    Write-Host "  No LinkSnap pods found!" -ForegroundColor Red
    Write-Host "  Run: kubectl get pods"
    exit 1
}

# Loop through each pod and get logs
foreach ($Pod in $Pods.Split(' ')) {
    Write-Host "  📋 Logs from pod: $Pod" -ForegroundColor Yellow
    Write-Host "  ----------------------------------------"
    kubectl logs $Pod --tail=$Lines
    Write-Host ""
}

Write-Host "  ✅ Done collecting logs" -ForegroundColor Green
Write-Host ""