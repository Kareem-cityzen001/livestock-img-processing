#!/usr/bin/env powershell
# Test upload endpoint with PowerShell

$ErrorActionPreference = "Continue"

Write-Host "`n" + ("="*70)
Write-Host "TESTING UPLOAD ENDPOINT" 
Write-Host ("="*70)

# First, test if server is running
Write-Host "`nTest 1: Check server connection..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Server is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Cannot connect to server: $_" -ForegroundColor Red
    exit 1
}

# Find a test image
Write-Host "`nTest 2: Find test image..." -ForegroundColor Cyan
$imagePath = $null
foreach ($dir in @("datasets/train/healthy", "datasets/train/foot-and-mouth", "datasets/train/lumpy")) {
    if (Test-Path $dir) {
        $images = Get-ChildItem -Path $dir -Filter "*.jpg", "*.jpeg", "*.png"  
        if ($images) {
            $imagePath = $images[0].FullName
            break
        }
    }
}

if ($imagePath) {
    Write-Host "✅ Found test image: $imagePath" -ForegroundColor Green
    $fileSize = (Get-Item $imagePath).Length / 1024
    Write-Host "   Size: $($fileSize.ToString('F1')) KB"
} else {
    Write-Host "❌ No test image found" -ForegroundColor Red
    exit 1
}

# Test upload
Write-Host "`nTest 3: Upload test image..." -ForegroundColor Cyan
try {
    $form = @{
        image = Get-Item -LiteralPath $imagePath
        behavior_description = "Test animal with no visible symptoms"
    }
    
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/upload" `
        -Method POST `
        -Form $form `
        -TimeoutSec 30 `
        -ErrorAction Stop
    
    Write-Host "✅ Upload successful!" -ForegroundColor Green
    Write-Host "   Status: $($response.StatusCode)"
    Write-Host "   Content size: $($response.Content.Length) bytes"
    
    # Try to parse as JSON
    try {
        $data = $response.Content | ConvertFrom-Json
        Write-Host "`n✅ Response is valid JSON:" -ForegroundColor Green
        Write-Host "   Diagnosis: $($data.Diagnosis)"
        Write-Host "   Confidence: $($data.Confidence)"
        Write-Host "   Status: $($data.Status)"
    } catch {
        Write-Host "`nResponse content:" -ForegroundColor Yellow
        Write-Host $response.Content.Substring(0, [Math]::Min(500, $response.Content.Length))
    }
    
} catch {
    Write-Host "❌ Upload failed: $_" -ForegroundColor Red
    if ($_.Exception.Response) {
        Write-Host "Status: $($_.Exception.Response.StatusCode)"
    }
}

Write-Host "`n" + ("="*70)
