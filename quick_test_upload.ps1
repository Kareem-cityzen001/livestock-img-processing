#!/usr/bin/env powershell
# Test upload quickly

Write-Host "Testing upload..." -ForegroundColor Cyan

# Get any jpg file
$image = Get-ChildItem -Path c:\TROJAN\datasets\train -File -Recurse -Filter *.jpg | Select-Object -First 1

if ($image) {
    Write-Host "Found image: $($image.Name) ($($image.Length / 1024) KB)" -ForegroundColor Green
    
    try {
        # Upload to simple test endpoint first
        $form = @{
            image = $image
        }
        
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/upload-test-simple" `
            -Method POST `
            -Form $form `
            -TimeoutSec 10
        
        Write-Host "✅ Simple upload test successful!" -ForegroundColor Green
        $data = $response.Content | ConvertFrom-Json
        Write-Host "Response: $($data.Diagnosis)" -ForegroundColor Green
        
        # Now try real upload
        Write-Host "`nTesting full upload..." -ForegroundColor Cyan
        $form2 = @{
            image = $image
            behavior_description = "Test animal"
        }
        
        $response2 = Invoke-WebRequest -Uri "http://127.0.0.1:5000/upload" `
            -Method POST `
            -Form $form2 `
            -TimeoutSec 60
        
        Write-Host "✅ Full upload successful!" -ForegroundColor Green
        $data2 = $response2.Content | ConvertFrom-Json
        Write-Host "Diagnosis: $($data2.Diagnosis)" -ForegroundColor Green
        Write-Host "Confidence: $($data2.Confidence)" -ForegroundColor Green
        
    } catch {
        Write-Host "❌ Error: $_" -ForegroundColor Red
        if ($_.Exception.Response) {
            $r = $_.Exception.Response
            Write-Host "Status: $($r.StatusCode)" -ForegroundColor Red
        }
    }
} else {
    Write-Host "No test image found" -ForegroundColor Red
}
