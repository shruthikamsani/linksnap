# LinkSnap — URL Shortener

A production-grade URL shortener built with a complete DevOps pipeline.

## What it does
Paste a long URL, get a short one. Click the short link and get redirected to the original. Tracks click counts for every link.

## Tech Stack
- **App:** Python Flask + SQLite
- **Container:** Docker
- **Orchestration:** Kubernetes + Helm
- **CI/CD:** GitHub Actions
- **Scripts:** PowerShell automation

## Pipeline
Every git push automatically:
1. Runs 8 automated tests
2. Builds Docker image
3. Pushes to GitHub Container Registry

## Run Locally
```powershell
py -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
py app.py
# Open http://127.0.0.1:5000
```

## Deploy to Kubernetes
```powershell
minikube start
helm install linksnap ./linksnap-chart
kubectl port-forward pod/$(kubectl get pods -l app=linksnap -o jsonpath='{.items[0].metadata.name}') 9090:5000
```

## Scripts
```powershell
.\scripts\health-check.ps1 -Url "http://127.0.0.1:9090"
.\scripts\get-logs.ps1
.\scripts\deploy.ps1 -Version "v1" -Replicas 2
```