# NexusFlow — One-Click Launcher (Windows PowerShell)
# Run: .\start.ps1

Write-Host "⚡ Starting NexusFlow..." -ForegroundColor Cyan

# Start Backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python -m venv venv; .\venv\Scripts\activate; pip install -r requirements.txt -q; uvicorn main:app --reload --port 8000" -WindowStyle Normal

Start-Sleep -Seconds 3

# Start Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm install; npm run dev" -WindowStyle Normal

Write-Host ""
Write-Host "✅ NexusFlow is starting!" -ForegroundColor Green
Write-Host "   Frontend → http://localhost:5173" -ForegroundColor White
Write-Host "   Backend  → http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs → http://localhost:8000/docs" -ForegroundColor White
