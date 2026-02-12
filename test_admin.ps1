#Path: test_admin.ps1

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   TESTING ADMIN FEATURES" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# ============================================
# STEP 1: Login as Admin
# ============================================

Write-Host "STEP 1: Login as Admin..." -ForegroundColor Yellow

$adminLoginBody = @{
    email    = "admin@avatar.com"
    password = "admin123"
} | ConvertTo-Json

try {
    $adminLoginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
        -Method Post `
        -Body $adminLoginBody `
        -ContentType "application/json" -ErrorAction Stop
    
    Write-Host "✅ Admin logged in successfully!" -ForegroundColor Green
    $adminToken = $adminLoginResponse.access_token
    Write-Host "User: $($adminLoginResponse.user.username)" -ForegroundColor Green
    Write-Host "Role: $($adminLoginResponse.user.role)" -ForegroundColor Green
}
catch {
    Write-Host "❌ Admin login failed" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

# ============================================
# STEP 2: Test Admin Endpoints
# ============================================

Write-Host "`n`nSTEP 2: Testing Admin Endpoints..." -ForegroundColor Yellow

# Test GET /admin/stats
Write-Host "`n2.1 Testing GET /admin/stats..." -ForegroundColor Cyan
try {
    $stats = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/admin/stats" `
        -Headers @{Authorization = "Bearer $adminToken" } -ErrorAction Stop
    
    Write-Host "✅ Stats retrieved successfully!" -ForegroundColor Green
    Write-Host "Total Users: $($stats.total_users)" -ForegroundColor White
    Write-Host "Active Users: $($stats.active_users)" -ForegroundColor White
    Write-Host "Admin Users: $($stats.admin_users)" -ForegroundColor White
    Write-Host "Total Simulations: $($stats.total_simulations)" -ForegroundColor White
}
catch {
    Write-Host "❌ Failed to get stats" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

# Test GET /admin/users
Write-Host "`n2.2 Testing GET /admin/users..." -ForegroundColor Cyan
try {
    $users = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/admin/users?page=1&page_size=10" `
        -Headers @{Authorization = "Bearer $adminToken" } -ErrorAction Stop
    
    Write-Host "✅ Users retrieved successfully!" -ForegroundColor Green
    if ($null -ne $users.total) {
        Write-Host "Total Users: $($users.total)" -ForegroundColor White
        Write-Host "Page: $($users.page)" -ForegroundColor White
        Write-Host "Users on this page: $($users.users.Count)" -ForegroundColor White
    }
    else {
        Write-Host "Users list structure unexpected." -ForegroundColor Yellow
        $users | ConvertTo-Json -Depth 5 | Write-Host
    }

}
catch {
    Write-Host "❌ Failed to get users" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

# Test GET /admin/simulations
Write-Host "`n2.3 Testing GET /admin/simulations..." -ForegroundColor Cyan
try {
    $simulations = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/admin/simulations?page=1&page_size=10" `
        -Headers @{Authorization = "Bearer $adminToken" } -ErrorAction Stop
    
    Write-Host "✅ Simulations retrieved successfully!" -ForegroundColor Green
    if ($null -ne $simulations.total) {
        Write-Host "Total Simulations: $($simulations.total)" -ForegroundColor White
    }
    else {
        Write-Host "Simulations list structure unexpected." -ForegroundColor Yellow
        $simulations | ConvertTo-Json -Depth 5 | Write-Host
    }
}
catch {
    Write-Host "❌ Failed to get simulations" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

# ============================================
# STEP 3: Test Access Control (Regular User)
# ============================================

Write-Host "`n`nSTEP 3: Testing Access Control (Regular User)..." -ForegroundColor Yellow

# Login as regular user
$userLoginBody = @{
    email    = "user@avatar.com"
    password = "user123"
} | ConvertTo-Json

try {
    $userLoginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
        -Method Post `
        -Body $userLoginBody `
        -ContentType "application/json" -ErrorAction Stop
    
    Write-Host "✅ Regular user logged in successfully!" -ForegroundColor Green
    $userToken = $userLoginResponse.access_token
    Write-Host "User: $($userLoginResponse.user.username)" -ForegroundColor Green
    Write-Host "Role: $($userLoginResponse.user.role)" -ForegroundColor Green
}
catch {
    Write-Host "❌ User login failed" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

# Try to access admin endpoint as regular user (should fail with 403)
Write-Host "`n3.1 Trying to access admin endpoint as regular user (should fail)..." -ForegroundColor Cyan
try {
    Invoke-RestMethod -Uri "http://localhost:8000/api/v1/admin/stats" `
        -Headers @{Authorization = "Bearer $userToken" } -ErrorAction Stop
    
    Write-Host "❌ SECURITY ISSUE: Regular user can access admin endpoint!" -ForegroundColor Red
}
catch {
    if ($_.Exception.Response.StatusCode.value__ -eq 403) {
        Write-Host "✅ Access correctly denied (403 Forbidden)" -ForegroundColor Green
    }
    else {
        Write-Host "⚠️  Unexpected error: $($_.Exception.Response.StatusCode)" -ForegroundColor Yellow
        Write-Host $_.Exception.Message -ForegroundColor Yellow
    }
}

# ============================================
# FINAL SUMMARY
# ============================================

Write-Host "`n`n========================================" -ForegroundColor Green
Write-Host "   TEST SUMMARY" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green
