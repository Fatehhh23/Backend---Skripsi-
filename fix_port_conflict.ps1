# FIX PostgreSQL Port Conflict - Run as Administrator
# Solusi untuk masalah: password authentication failed

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  FIX PostgreSQL Port 5432 Conflict" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Stop PostgreSQL Windows Service
Write-Host "[1/4] Stopping PostgreSQL Windows Service..." -ForegroundColor Yellow
try {
    Stop-Service -Name "postgresql-x64-16" -Force -ErrorAction Stop
    Write-Host "✓ PostgreSQL Windows service STOPPED!" -ForegroundColor Green
} catch {
    Write-Host "✗ Error: $_" -ForegroundColor Red
    Write-Host "`nNOTE: Jika error 'Access Denied', jalankan PowerShell sebagai Administrator!" -ForegroundColor Yellow
    Write-Host "Klik kanan PowerShell → Run as Administrator`n" -ForegroundColor Yellow
    exit 1
}

# Step 2: Disable auto-start (optional)
Write-Host "`n[2/4] Disable PostgreSQL auto-start (optional)..." -ForegroundColor Yellow
$response = Read-Host "Disable auto-start? (Y/N)"
if ($response -eq "Y" -or $response -eq "y") {
    Set-Service -Name "postgresql-x64-16" -StartupType Disabled
    Write-Host "✓ Auto-start DISABLED!" -ForegroundColor Green
} else {
    Write-Host "Skipped" -ForegroundColor Gray
}

# Step 3: Verify port 5432 is free
Write-Host "`n[3/4] Checking port 5432..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
$portCheck = netstat -ano | findstr ":5432"
if ($portCheck) {
    Write-Host "⚠ Port 5432 masih digunakan:" -ForegroundColor Yellow
    Write-Host $portCheck
} else {
    Write-Host "✓ Port 5432 TERSEDIA!" -ForegroundColor Green
}

# Step 4: Test Docker database connection
Write-Host "`n[4/4] Testing Docker database connection..." -ForegroundColor Yellow
try {
    $result = docker exec tsunami_db psql -U tsunami_user -d tsunami_db -c "SELECT 'Connection SUCCESS!' as status;" 2>&1
    if ($result -match "SUCCESS") {
        Write-Host "✓ Docker database CONNECTION OK!" -ForegroundColor Green
    } else {
        Write-Host "⚠ Docker database might not be ready yet." -ForegroundColor Yellow
        Write-Host "Wait 10 seconds and try again..." -ForegroundColor Yellow
    }
} catch {
    Write-Host "✗ Docker database not accessible: $_" -ForegroundColor Red
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  SELESAI!" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nSekarang coba connect pgAdmin lagi:" -ForegroundColor White
Write-Host "  Host: localhost" -ForegroundColor White
Write-Host "  Port: 5432" -ForegroundColor White
Write-Host "  Database: tsunami_db" -ForegroundColor White
Write-Host "  Username: tsunami_user" -ForegroundColor White
Write-Host "  Password: tsunami_password`n" -ForegroundColor White
