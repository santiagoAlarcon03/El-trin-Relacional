# Script para ejecutar tests con servidor temporal
# Inicia el servidor, ejecuta los tests y detiene el servidor

Write-Host "=" -NoNewline -ForegroundColor Blue
Write-Host ("=" * 79) -ForegroundColor Blue
Write-Host "🚀 INICIANDO SERVIDOR Y EJECUTANDO TESTS" -ForegroundColor Cyan
Write-Host ("=" * 80) -ForegroundColor Blue

$projectPath = "C:\Users\USER\Desktop\Códigos\El-trin-Relacional"
$pythonExe = "$projectPath\.venv\Scripts\python.exe"

# Iniciar servidor en background job
Write-Host "`n📡 Iniciando servidor FastAPI..." -ForegroundColor Yellow
$serverJob = Start-Job -ScriptBlock {
    param($path, $python)
    Set-Location $path
    & $python -m uvicorn api.main:app --port 8000 2>&1
} -ArgumentList $projectPath, $pythonExe

# Esperar a que el servidor inicie
Write-Host "⏳ Esperando 5 segundos para que el servidor inicie..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Verificar si el servidor está corriendo
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Servidor iniciado correctamente`n" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: El servidor no respondió" -ForegroundColor Red
    Stop-Job $serverJob
    Remove-Job $serverJob
    exit 1
}

# Ejecutar tests
Write-Host "🧪 Ejecutando tests obligatorios...`n" -ForegroundColor Cyan
Write-Host ("=" * 80) -ForegroundColor Blue

& $pythonExe "$projectPath\tests\test_cases_obligatorios.py"

# Detener servidor
Write-Host "`n`n🛑 Deteniendo servidor..." -ForegroundColor Yellow
Stop-Job $serverJob
Remove-Job $serverJob

Write-Host "✅ Tests completados" -ForegroundColor Green
