# Start backend: run migrations then start uvicorn
Set-Location -Path (Join-Path $PSScriptRoot '..\backend')
if (Test-Path env) { Write-Host 'Using existing env' }
Write-Host 'Applying migrations (alembic upgrade head)'
alembic upgrade head
Write-Host 'Starting uvicorn'
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
